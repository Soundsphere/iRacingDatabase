import mariadb
import configparser
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["iracingcreds"]["user"]
pwd = cfg["iracingcreds"]["pass"]
memId = cfg["iracingcreds"]["memberId"]

db_host = cfg["databasecreds"]["host"]

print(db_host)
