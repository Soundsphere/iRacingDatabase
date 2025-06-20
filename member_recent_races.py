import configparser
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["credentials"]["user"]
pwd  = cfg["credentials"]["pass"]
memId = cfg['credentials']['memberId']


idc = irDataClient(username=user, password=pwd)


info=(idc.stats_member_recent_races(cust_id=memId))

print(info)