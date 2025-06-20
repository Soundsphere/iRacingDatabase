import configparser
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["credentials"]["user"]
pwd  = cfg["credentials"]["pass"]
memId = cfg['credentials']['memberId']


idc = irDataClient(username=user, password=pwd)


recentraces=(idc.stats_member_recent_races(cust_id=memId))
cars=(idc.get_cars())

#all_newi = [race['newi_rating'] for race in info['races']]
latestraces = [race['series_name'] for race in recentraces['races']]
first_newi = recentraces['races'][0]['newi_rating']   # grabs the first newi_rating :contentReference[oaicite:0]{index=0}
first_safety = recentraces['races'][0]['new_sub_level']
sessId = recentraces['races'][0]['subsession_id']

print("SessionId:",sessId)
print("Current iRating:",first_newi)
print("Current Safety Rating:",first_safety)





# build a lookup dict once
cars_by_id = {c['car_id']: c for c in cars}

# then to grab car 123:
car = cars_by_id.get(169)
if car:
    print(car['car_name'])
else:
    print("No car with that ID.")
