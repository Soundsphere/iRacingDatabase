import configparser
from iracingdataapi.client import irDataClient
#import ast


cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg['credentials']['user']
pwd  = cfg['credentials']["pass"]
memId = cfg['credentials']['memberId']

db_host = cfg['databasecreds']['host']


print(db_host)