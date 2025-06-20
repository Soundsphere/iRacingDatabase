## get the lap times from the latest quali and race session
## ToDo: Iterate over the last sessions and get each one

import configparser
from iracingdataapi.client import irDataClient

# load config
cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["credentials"]["user"]
pwd  = cfg["credentials"]["pass"]
memId = cfg['credentials']['memberId']

# log into iRacing
idc = irDataClient(username=user, password=pwd)



## calculate laptimes from iRacing
def fmt_laptime(raw):
    # raw is in 1/10 000 of a second
    ms_total = raw // 10                   # now in milliseconds
    secs, ms = divmod(ms_total, 1_000)     # split into seconds + ms
    mins, secs = divmod(secs, 60)          # split seconds into minutes
    return f"{mins}:{secs:02d}.{ms:03d}"

# get the carlist so that we can translate the ID later
cars=(idc.get_cars())

# get the recent races from my user
recentraces=(idc.stats_member_recent_races(cust_id=memId))

# get all subsession ids of the race. Bascially the split id
allsessId = [race['subsession_id'] for race in recentraces['races']]

# get latest subsession id. Basically the split id
sessId = recentraces['races'][0]['subsession_id']

# get quali and race info
qualiinfo = (idc.result_lap_data(subsession_id=sessId,simsession_number=-1,cust_id=memId))
raceinfo = (idc.result_lap_data(subsession_id=sessId,simsession_number=0,cust_id=memId))

# get the track name
tname = recentraces['races'][0]['track']['track_name']


# qualifiying best time
qbest_time = next(
    (lap['lap_time'] for lap in qualiinfo if lap['personal_best_lap']),
    None
)

#race best time
rbest_time = next(
    (lap['lap_time'] for lap in raceinfo if lap['personal_best_lap']),
    None
)

# get the car id 
carid = recentraces['races'][0]['car_id']

# translate car id to name
cars_by_id = {c['car_id']: c for c in cars}



# output it all to terminal
print("SessionId:", sessId)
print("Track:",tname)
car = cars_by_id.get(carid)
if car:
    print(car['car_name'])
else:
    print("No car with that ID.")
print("Quali Time:",fmt_laptime(qbest_time))
print("Race Time:",fmt_laptime(rbest_time))
#print(allsessId)


