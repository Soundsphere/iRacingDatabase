import mariadb
import configparser
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["iracingcreds"]["user"]
pwd = cfg["iracingcreds"]["pass"]
memId = cfg["iracingcreds"]["memberId"]

# db_host = cfg["databasecreds"]["host"]

# print(db_host)

idc = irDataClient(username=user, password=pwd)

# info=(idc.stats_member_recent_races(cust_id=memId))
# carcl=(idc.get_cars())
licence = idc.result(subsession_id=77974315)

print(licence)
