import configparser
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["credentials"]["user"]
pwd  = cfg["credentials"]["pass"]
memId = cfg['credentials']['memberId']


idc = irDataClient(username=user, password=pwd)


records = (idc.stats_member_bests(cust_id=memId, car_id=159))

print(records)