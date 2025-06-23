import configparser
import logging
from datetime import datetime

import mariadb
from iracingdataapi.client import irDataClient

from ir_utils import format_session_time, sr_convert, time_convert


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
    except Exception:
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


def car_name(car_id: int, lookup: dict) -> str:
    """Return the car name for the given id."""
    return lookup.get(car_id, "No car with that ID.")


def main():
    logging.basicConfig(level=logging.INFO)

    cfg = configparser.ConfigParser()
    cfg.read("config.ini")

    ir_user = cfg["iracingcreds"]["user"]
    ir_pwd = cfg["iracingcreds"]["pass"]
    ir_mem_id = cfg["iracingcreds"]["memberId"]
    ir_drivername = cfg["iracingcreds"]["d_name"]

    db_host = cfg["databasecreds"]["host"]
    db_user = cfg["databasecreds"]["databseuser"]
    db_pwd = cfg["databasecreds"]["databasepasswd"]
    db_database = cfg["databasecreds"]["database"]

    client = irDataClient(username=ir_user, password=ir_pwd)
    recent_races = client.stats_member_recent_races(cust_id=ir_mem_id)
    cars = client.get_cars()
    cars_by_id = {c["car_id"]: c["car_name"] for c in cars}

    with mariadb.connect(
        user=db_user, password=db_pwd, host=db_host, database=db_database
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT SubsessionId FROM Stuff.iRacing ORDER BY SessionDate DESC LIMIT 10"
            )
            existing_ids = [row[0] for row in cur.fetchall()]

            insert_stmt = """
                INSERT INTO iRacing (
                    subsessionId, SessionDate, SeriesName, Car, Track,
                    QualifyingTime, RaceTime, Incidents, OldSafetyRating, NewSafetyRating, SafetyRatingGain,
                    StartPosition, FinishPosition, OldiRating, NewiRating, iRatingGain, Laps, LapsLed,
                    Points, SoF, TeamRace, QualiSetByTeammate, FastestLapSetByTeammate, SeasonWeek, SeasonNumber, SeasonYear
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for race in recent_races["races"]:
                subsession_id = race["subsession_id"]
                if subsession_id in existing_ids:
                    continue

                qinfo, rinfo, is_teamrace = fetch_lap_data(
                    subsession_id, client, ir_mem_id, ir_drivername
                )

                qbest_lap = best_lap(qinfo)
                rbest_lap = best_lap(rinfo)

                qbest_time = qbest_lap["lap_time"] if qbest_lap else None
                rbest_time = rbest_lap["lap_time"] if rbest_lap else None

                qbest_driver = qbest_lap.get("display_name") if qbest_lap else None
                q_set_by_teammate = (
                    bool(is_teamrace)
                    and qbest_driver is not None
                    and qbest_driver != ir_drivername
                )
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

                values = (
                    subsession_id,
                    session_time,
                    race["series_name"],
                    car_name(race["car_id"], cars_by_id),
                    race["track"]["track_name"],
                    qbest_time if qbest_time else "0:00.000",
                    rbest_time if rbest_time else "0:00.000",
                    race["incidents"],
                    sr_convert(race["old_sub_level"]),
                    sr_convert(race["new_sub_level"]),
                    sr_convert(sr_gain),
                    race["start_position"],
                    race["finish_position"],
                    race["oldi_rating"],
                    race["newi_rating"],
                    ir_gain,
                    race["laps"],
                    race["laps_led"],
                    race["points"],
                    race["strength_of_field"],
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
                except mariadb.Error as exc:
                    logging.error("Failed to insert session %s: %s", subsession_id, exc)


if __name__ == "__main__":
    main()
