import configparser
from pathlib import Path
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
config_path = Path(__file__).resolve().parent / "config.ini"
cfg.read(config_path)
user = cfg["iracingcreds"]["user"]
pwd = cfg["iracingcreds"]["pass"]
memId = cfg["iracingcreds"]["memberId"]

## since the carlist updates every 3 months with new added cars,
## this needs to be run before every new season

idc = irDataClient(username=user, password=pwd)

carcl = idc.get_cars()

# Write the car list to car_list.cfg (overwrite if it exists)
with open("car_list.cfg", "w", encoding="utf-8") as f:
    f.write(str(carcl))

