import configparser
import logging
import mariadb
from datetime import datetime
from iracingdataapi.client import irDataClient
from ir_utils import format_session_time, sr_convert, time_convert, licence_from_level
import ast
from pathlib import Path

def fetch_lap_data(
    subsession_id: int, client: irDataClient, member_id: str, driver_name: str
):
    """Return qualifying and race lap data for a subsession.

    If the member lookup fails, the data is fetched using the team id and the
    session is marked as a team race.
    """
    is_teamrace = False
    try:
        qinfo = client.result_lap_data(
            subsession_id=subsession_id,
            simsession_number=-1,
            cust_id=member_id,
        )
        rinfo = client.result_lap_data(
            subsession_id=subsession_id,
            simsession_number=0,
            cust_id=member_id,
        )
    except Exception as exc:
        logging.warning(
            "Member lookup failed for subsession %s: %s", subsession_id, exc
        )
        team_race = client.result(subsession_id=subsession_id)
        teamid_var = team_race["session_results"][2]
        teamid_output = next(
            (
                str(driver["team_id"])[1:]
                for team in teamid_var.get("results", [])
                for driver in team.get("driver_results", [])
                if driver["display_name"] == driver_name
            ),
            None,
        )
        logging.info("Using team_id %s for subsession %s", teamid_output, subsession_id)
        qinfo = client.result_lap_data(
            subsession_id=subsession_id,
            simsession_number=-1,
            team_id=teamid_output,
        )
        rinfo = client.result_lap_data(
            subsession_id=subsession_id,
            simsession_number=0,
            team_id=teamid_output,
        )
        is_teamrace = True
    return qinfo, rinfo, is_teamrace


def best_lap(info):
    """Return the lap dictionary marked as the personal best."""
    return next((lap for lap in info if lap["personal_best_lap"]), None)


def _find_driver_result(result: dict, driver_name: str) -> dict | None:
    """Return the result dictionary for the selected driver."""
    sessions = result.get("session_results", [])
    if len(sessions) <= 2:
        return None
    for entry in sessions[2].get("results", []):
        drivers = entry.get("driver_results")
        if drivers is None:
            if entry.get("display_name") == driver_name:
                return entry
        else:
            for driver in drivers:
                if driver.get("display_name") == driver_name:
                    return driver
    return None


def driver_new_licence(result: dict, driver_name: str) -> str | None:
    """Return the licence letter for the driver in a given subsession."""
    driver = _find_driver_result(result, driver_name)
    if driver is not None:
        return licence_from_level(driver.get("new_license_level"))
    return None


def driver_average_lap(result: dict, driver_name: str) -> int | None:
    """Return the average lap time for the selected driver."""
    driver = _find_driver_result(result, driver_name)
    if driver is not None:
        return driver.get("average_lap")
    return None


def car_name(car_id: int, lookup: dict) -> str:
    """Return the car name for the given id."""
    return lookup.get(car_id, "No car with that ID.")


def normalize_category(category: str | None) -> str | None:
    """Map API category strings to human readable labels."""
    mapping = {
        "formula_car": "Formula Car",
        "sports_car": "Sports Car",
        "oval": "Oval",
        "dirtoval": "Dirt Oval",
        "dirtroad": "Dirt Road",
    }
    if category is None:
        return None
    return mapping.get(category, category)


def main():
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting iRacing data pull")

    cfg = configparser.ConfigParser()
    config_path = Path(__file__).resolve().parent / "config.ini"
    cfg.read(config_path)

    ir_user = cfg["iracingcreds"]["user"]
    ir_pwd = cfg["iracingcreds"]["pass"]
    ir_mem_id = cfg["iracingcreds"]["memberId"]
    ir_drivername = cfg["iracingcreds"]["d_name"]

    db_host = cfg["databasecreds"]["host"]
    db_user = cfg["databasecreds"]["databseuser"]
    db_pwd = cfg["databasecreds"]["databasepasswd"]
    db_database = cfg["databasecreds"]["database"]

    try:
        client = irDataClient(username=ir_user, password=ir_pwd)
    except Exception as exc:
        logging.error("Failed to create iRacing client: %s", exc)
        return

    try:
        recent_races = client.stats_member_recent_races(cust_id=ir_mem_id)
        logging.info("Fetched %d recent races", len(recent_races.get("races", [])))
    except Exception as exc:
        logging.error("Failed to fetch recent races: %s", exc)
        return

    try:
        with open("car_list.cfg", "r", encoding="utf-8") as f:
            cars = ast.literal_eval(f.read())
        logging.info("Loaded %d cars from car_list.cfg", len(cars))
    except FileNotFoundError:
        logging.info("car_list.cfg not found, fetching from API")
        try:
            cars = client.get_cars()
            with open("car_list.cfg", "w", encoding="utf-8") as f:
                f.write(str(cars))
            logging.info("Fetched %d cars and saved to car_list.cfg", len(cars))
        except Exception as exc:
            logging.error("Failed to fetch car list: %s", exc)
            return
    except Exception as exc:
        logging.error("Failed to load car list: %s", exc)
        return
    cars_by_id = {c["car_id"]: c["car_name"] for c in cars}
    car_categories = {
        c.get("car_id"): c.get("categories", [None])[0]
        for c in cars
        if c.get("car_id") is not None
    }

    try:
        conn = mariadb.connect(
            user=db_user, password=db_pwd, host=db_host, database=db_database
        )
        logging.info("Connected to database %s on %s", db_database, db_host)
    except mariadb.Error as exc:
        logging.error("Database connection failed: %s", exc)
        return

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT SubsessionId FROM Stuff.iRacing ORDER BY SessionDate DESC LIMIT 15"
            )
            existing_ids = [row[0] for row in cur.fetchall()]
            logging.info("Found %d existing subsessions", len(existing_ids))

            insert_stmt = """
                INSERT INTO iRacing (
                    subsessionId, SessionDate, SeriesName, Car, Track, TrackConfiguration,
                    QualifyingTime, RaceTime, AverageLapTime, Incidents, OldSafetyRating, NewSafetyRating, SafetyRatingGain, Licence,
                    StartPosition, FinishPosition, OldiRating, NewiRating, iRatingGain, Laps, LapsLed,
                    Points, SoF, RaceType, TeamRace, QualiSetByTeammate, FastestLapSetByTeammate,
                    SeasonWeek, SeasonNumber, SeasonYear
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for race in recent_races["races"]:
                subsession_id = race["subsession_id"]
                if subsession_id in existing_ids:
                    logging.info("Skipping existing subsession %s", subsession_id)
                    continue
                logging.info("Processing subsession %s", subsession_id)

                race_type = normalize_category(car_categories.get(race["car_id"]))

                qinfo, rinfo, is_teamrace = fetch_lap_data(
                    subsession_id, client, ir_mem_id, ir_drivername
                )

                qbest_lap = best_lap(qinfo)
                rbest_lap = next(
                    (
                        lap
                        for lap in rinfo
                        if lap.get("display_name") == ir_drivername
                        and lap.get("personal_best_lap")
                    ),
                    None,
                )

                qbest_driver = qbest_lap.get("display_name") if qbest_lap else None
                q_set_by_teammate = (
                    bool(is_teamrace)
                    and qbest_driver is not None
                    and qbest_driver != ir_drivername
                )
                if qbest_lap and not q_set_by_teammate:
                    qbest_time = qbest_lap["lap_time"]
                else:
                    qbest_time = None

                rbest_time = rbest_lap["lap_time"] if rbest_lap else None
                ## set personal fastest lap
                rbest_driver = rbest_lap.get("display_name") if rbest_lap else None
                fastestteammate = (
                    bool(is_teamrace)
                    and rbest_lap is not None
                    and rbest_lap.get("personal_best_lap")
                    and rbest_lap.get("team_fastest_lap")
                    and rbest_driver is not None
                    and rbest_driver != ir_drivername
                )

                ir_gain = int(race["newi_rating"]) - int(race["oldi_rating"])
                sr_gain = int(race["new_sub_level"]) - int(race["old_sub_level"])

                session_time = format_session_time(race["session_start_time"])
                race_result = client.result(subsession_id=subsession_id)
                licence = driver_new_licence(race_result, ir_drivername)
                avg_lap_time = driver_average_lap(race_result, ir_drivername)
                track_config = race_result.get("track", {}).get("config_name")

                values = (
                    subsession_id,
                    session_time,
                    race["series_name"],
                    car_name(race["car_id"], cars_by_id),
                    race["track"]["track_name"],
                    track_config,
                    qbest_time if qbest_time else "0",
                    rbest_time if rbest_time else "0",
                    avg_lap_time if avg_lap_time is not None else "0",
                    race["incidents"],
                    sr_convert(race["old_sub_level"]),
                    sr_convert(race["new_sub_level"]),
                    sr_convert(sr_gain),
                    licence,
                    race["start_position"],
                    race["finish_position"],
                    race["oldi_rating"],
                    race["newi_rating"],
                    ir_gain,
                    race["laps"],
                    race["laps_led"],
                    race["points"],
                    race["strength_of_field"],
                    race_type,
                    str(is_teamrace).lower(),
                    str(q_set_by_teammate).lower(),
                    str(fastestteammate).lower(),
                    race["race_week_num"],
                    race["season_quarter"],
                    race["season_year"],
                )

                try:
                    cur.execute(insert_stmt, values)
                    conn.commit()
                    logging.info("Inserted subsession %s", subsession_id)
                except mariadb.Error as exc:
                    logging.error("Failed to insert session %s: %s", subsession_id, exc)


if __name__ == "__main__":
    main()
