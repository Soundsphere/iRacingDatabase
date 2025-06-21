import configparser
from iracingdataapi.client import irDataClient

## get the login config from the config file
cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["credentials"]["user"]
pwd  = cfg["credentials"]["pass"]
memId = cfg['credentials']['memberId']

## create the client
idc = irDataClient(username=user, password=pwd)


## get the data from iRacing for the last sessions races. This contains most, but not all info the table
recentraces = (idc.stats_member_recent_races(cust_id=memId))

## extrac the subsessionId for each recent race
sessId = recentraces['races'][0]['subsession_id']

## this gets us the missing info for the fastest qualifying time
qualiinfo = (idc.result_lap_data(subsession_id=sessId,simsession_number=-1,cust_id=memId))

# this gets us the fastest lap time from the race
raceinfo = (idc.result_lap_data(subsession_id=sessId,simsession_number=0,cust_id=memId))






print(recentraces)
print(qualiinfo)
print(raceinfo)