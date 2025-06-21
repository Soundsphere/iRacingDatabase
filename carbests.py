import configparser
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["credentials"]["user"]
pwd  = cfg["credentials"]["pass"]
memId = cfg['credentials']['memberId']


idc = irDataClient(username=user, password=pwd)

cars=(idc.get_cars())

def car_name(carId):
	cars_by_id = {c['car_id']: c for c in cars}
	car = cars_by_id.get(carId)
	if car:
		return(str(" - ") + car['car_name'])
	else:
		return("No car with that ID.")


#records = (idc.stats_member_bests(cust_id=memId, car_id=159))



cars_by_id = {c['car_id']: c for c in cars}
car = cars_by_id.get(169)
if car:
   	print(str(" - ") + car['car_name'])
else:
   	print("No car with that ID.")

#print(car_name(159))

carclass = (idc.get_carclasses())
print(carclass)