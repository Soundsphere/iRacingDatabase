import configparser

from iracingdataapi.client import irDataClient
from utils import time_convert

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["credentials"]["user"]
pwd = cfg["credentials"]["pass"]
memId = cfg["credentials"]["memberId"]

idc = irDataClient(username=user, password=pwd)

print(time_convert(1019840))

recentraces = idc.stats_member_recent_races(cust_id=memId)
cars = idc.get_cars()

latestraces = [race["series_name"] for race in recentraces["races"]]
newi = recentraces["races"][0]["newi_rating"]
oldi = recentraces["races"][0]["oldi_rating"]
old_safety = recentraces["races"][0]["old_sub_level"]
new_safety = recentraces["races"][0]["new_sub_level"]
sessId = recentraces["races"][0]["subsession_id"]
racename = recentraces["races"][0]["series_name"]
carid = recentraces["races"][0]["car_id"]
inci = recentraces["races"][0]["incidents"]
tname = recentraces["races"][0]["track"]["track_name"]
raceinfo = idc.result_lap_data(
    subsession_id=sessId, simsession_number=-1, cust_id=memId
)

spos = recentraces["races"][0]["start_position"]
fpos = recentraces["races"][0]["finish_position"]

cars_by_id = {c["car_id"]: c for c in cars}

print(raceinfo)

gained = int(spos) - int(fpos)
irgain = int(oldi) - int(newi)
srgain = int(old_safety) - int(new_safety)

print("Details:")
print(" - SessionId:", sessId)
print(" - Series:", racename)
print(" - Track:", tname)
car = cars_by_id.get(carid)
if car:
    print(str(" - ") + car["car_name"])
else:
    print("No car with that ID.")
print("iRating:")
print(" - Old iRating:", oldi)
print(" - iRating gained:", irgain)
print(" - New iRating:", newi)
print("Safety Rating")
print(" - Incidents", inci)
print(" - Old Safety Rating:", old_safety)
print(" - Safety Rating gained:", srgain)
print(" - New Safety Rating:", new_safety)
print(" - Start Position:", spos)
print(" - Finish Position:", fpos)
print(" - Gained:", gained)
