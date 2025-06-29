import configparser
import os
import sys
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["iracingcreds"]["user"]
pwd = cfg["iracingcreds"]["pass"]
memId = cfg["iracingcreds"]["memberId"]

## since the carlist updates every 3 months with new added cars,
## this needs to be run before every new season

# Ensure the script works regardless of where it is called from
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.getcwd())

idc = irDataClient(username=user, password=pwd)

carcl = idc.get_cars()

# Write the car list to car_list.cfg (overwrite if it exists)
with open("car_list.cfg", "w", encoding="utf-8") as f:
    f.write(str(carcl))

