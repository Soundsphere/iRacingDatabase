import configparser
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["iracingcreds"]["user"]
pwd = cfg["iracingcreds"]["pass"]
memId = cfg["iracingcreds"]["memberId"]

## since the carlist updates every 3 months with new added cars,
## this needs to be run before every new season

idc = irDataClient(username=user, password=pwd)

carcl=(idc.get_cars())

