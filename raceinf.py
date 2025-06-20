import configparser
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["credentials"]["user"]
pwd  = cfg["credentials"]["pass"]
memId = cfg['credentials']['memberId']


idc = irDataClient(username=user, password=pwd)


recentraces=(idc.stats_member_recent_races(cust_id=memId))



sessId = recentraces['races'][0]['subsession_id']

raceinfo = (idc.result_lap_data(subsession_id=sessId,simsession_number=0,cust_id=memId))

print(raceinfo)
