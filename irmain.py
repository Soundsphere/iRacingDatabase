import mariadb
import configparser
from iracingdataapi.client import irDataClient
from datetime import datetime

## get the login config from the config file
cfg = configparser.ConfigParser()
cfg.read("config.ini")

## iracing login data
ir_user = cfg['iracingcreds']["user"]
ir_pwd  = cfg['iracingcreds']["pass"]
ir_memId = cfg['iracingcreds']['memberId']
ir_drivername = cfg['iracingcreds']['d_name']

## database login
db_host = cfg['databasecreds']['host']
db_user = cfg['databasecreds']['databseuser']
db_pwd = cfg['databasecreds']['databasepasswd']
db_database = cfg['databasecreds']['database']


## connect to the database
conn = mariadb.connect(
    user=db_user,
    password=db_pwd,
    host=db_host,
    database=db_database)
cur = conn.cursor()


## create the client
idc = irDataClient(username=ir_user, password=ir_pwd)

cur.execute('SELECT SubsessionId FROM Stuff.iRacing ORDER BY SessionDate DESC LIMIT 10')
existing_ids = [row[0] for row in cur.fetchall()]

## calculate laptimes from iRacing
def time_convert(raw):
    # raw is in 1/10 000 of a second
    ms_total = raw // 10                   # now in milliseconds
    secs, ms = divmod(ms_total, 1_000)     # split into seconds + ms
    mins, secs = divmod(secs, 60)          # split seconds into minutes
    return f"{mins}:{secs:02d}.{ms:03d}"

def sr_convert(sr_number):
        converted_sr = sr_number/100
        return converted_sr


def format_session_time(raw_time: str) -> str:
        """Convert an ISO formatted timestamp to ``YYYY-MM-DD HH:MM:SS``."""
        dt = datetime.fromisoformat(raw_time.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def fetch_lap_data(subsession_id: int):
        """Return qualifying and race lap data for the given subsession.

        The function also determines whether the session is a team race. If the
        normal lookup using the member id fails, the except block fetches the
        data using the team id and marks the session as a team race.
        """
        is_teamrace = False
        try:
                qinfo = idc.result_lap_data(
                        subsession_id=subsession_id,
                        simsession_number=-1,
                        cust_id=ir_memId,
                )
                rinfo = idc.result_lap_data(
                        subsession_id=subsession_id,
                        simsession_number=0,
                        cust_id=ir_memId,
                )
        except Exception:
                team_race = idc.result(subsession_id=subsession_id)
                teamid_var = team_race['session_results'][2]
                teamid_output = next(
                        (
                                str(driver['team_id'])[1:]
                                for team in teamid_var.get('results', [])
                                for driver in team.get('driver_results', [])
                                if driver['display_name'] == ir_drivername
                        ),
                        None,
                )
                qinfo = idc.result_lap_data(
                        subsession_id=subsession_id,
                        simsession_number=-1,
                        team_id=teamid_output,
                )
                rinfo = idc.result_lap_data(
                        subsession_id=subsession_id,
                        simsession_number=0,
                        team_id=teamid_output,
                )
                is_teamrace = True
        return qinfo, rinfo, is_teamrace


def best_lap(info):
        """Return the lap dict flagged as personal best.

        The iRacing API marks the best lap in the lap data with the
        ``personal_best_lap`` flag.  In order to determine who set the lap
        we return the entire lap dictionary instead of only the lap time.
        """

        return next((lap for lap in info if lap['personal_best_lap']), None)


## get the car name from the Id
def car_name(carId):
        return cars_by_id.get(carId, "No car with that ID.")


## get the data from iRacing for the last sessions races. This contains most, but not all info the table
recentraces = (idc.stats_member_recent_races(cust_id=ir_memId))

## get the car list from iRacing and build lookup dictionary
cars = idc.get_cars()
cars_by_id = {c['car_id']: c['car_name'] for c in cars}

## first version. Iterate of the past races as long as we can match a subsession id and output the data to terminal. 
for i in recentraces['races']:
        eachId = i['subsession_id']
        if eachId in existing_ids:
                continue

        qinfo, rinfo, is_teamrace = fetch_lap_data(eachId)

        qbest_lap = best_lap(qinfo)
        rbest_lap = best_lap(rinfo)

        qbest_time = qbest_lap['lap_time'] if qbest_lap else None
        rbest_time = rbest_lap['lap_time'] if rbest_lap else None

        qbest_driver = qbest_lap.get('display_name') if qbest_lap else None
        q_set_by_teammate = (
                bool(is_teamrace)
                and qbest_driver is not None
                and qbest_driver != ir_drivername
        )
        iRgain = int(i['newi_rating']) - int(i['oldi_rating'])
        srgain = int(i['new_sub_level']) - int(i['old_sub_level'])
        ## print everything


        insert_stmt = """
            INSERT INTO iRacing (
                subsessionId, SessionDate, SeriesName, Car, Track,
                QualifyingTime, RaceTime, Incidents, OldSafetyRating, NewSafetyRating, SafetyRatingGain,
                StartPosition, FinishPosition, OldiRating, NewiRating, iRatingGain, Laps, LapsLed,
                Points, SoF, TeamRace, QualiSetByTeammate, SeasonWeek, SeasonNumber, SeasonYear
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cur.execute(
            insert_stmt,
            (
                eachId,
                session_time,
                i['series_name'],
                car_name(i['car_id']),
                i['track']['track_name'],
                (qbest_time) if qbest_time else "0:00.000",
                (rbest_time) if rbest_time else "0:00.000",
                i['incidents'],
                sr_convert(i['old_sub_level']),
                sr_convert(i['new_sub_level']),
                sr_convert(srgain),
                i['start_position'],
                i['finish_position'],
                i['oldi_rating'],
                i['newi_rating'],
                iRgain,
                i['laps'],
                i['laps_led'],
                i['points'],
                i['strength_of_field'],
                str(is_teamrace).lower(),
                str(q_set_by_teammate).lower(),
                i['race_week_num'],
                i['season_quarter'],
                i['season_year'],
            ),
        )

conn.commit()
