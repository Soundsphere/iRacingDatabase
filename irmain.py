import configparser
from iracingdataapi.client import irDataClient

## get the login config from the config file
cfg = configparser.ConfigParser()
cfg.read("config.ini")
#iracing login data
ir_user = cfg['iracingcreds']["user"]
ir_pwd  = cfg['iracingcreds']["pass"]
ir_memId = cfg['iracingcreds']['memberId']
ir_drivername = cfg['iracingcreds']['d_name']


## create the client
idc = irDataClient(username=ir_user, password=ir_pwd)

## calculate laptimes from iRacing
def time_convert(raw):
    # raw is in 1/10 000 of a second
    ms_total = raw // 10                   # now in milliseconds
    secs, ms = divmod(ms_total, 1_000)     # split into seconds + ms
    mins, secs = divmod(secs, 60)          # split seconds into minutes
    return f"{mins}:{secs:02d}.{ms:03d}"


## get the car name from the Id
def car_name(carId):
	cars_by_id = {c['car_id']: c for c in cars}
	car = cars_by_id.get(carId)
	if car:
		return(car['car_name'])
	else:
		return("No car with that ID.")


## get the data from iRacing for the last sessions races. This contains most, but not all info the table
recentraces = (idc.stats_member_recent_races(cust_id=ir_memId))

## get the car list from iRacing 
cars=(idc.get_cars())

## first version. Iterate of the past races as long as we can match a subsession id and output the data to terminal. 
for i in recentraces['races']:
	## get the subsession id for each row in recent race data
	eachId = i['subsession_id']
	print(eachId)
	## get the times for quali and reace here
	## IF TEAMEVENT A TEAM ID HAS TO BE SUPPLIED. CREATE A CHECK TO EITHER GET MEMID OR TEAMID
	try:
		qinfo = (idc.result_lap_data(subsession_id=eachId,simsession_number=-1,cust_id=ir_memId))
		rinfo = (idc.result_lap_data(subsession_id=eachId,simsession_number=0,cust_id=ir_memId))
	except:
		team_race = (idc.result(subsession_id=eachId))
		teamid_var = team_race['session_results'][2]
		for team in teamid_var.get('results', []):
			for driver in team.get('driver_results', []):
				if driver['display_name'] == ir_drivername:
					teamid_output = str(driver['team_id'])[1:]
		qinfo = (idc.result_lap_data(subsession_id=eachId,simsession_number=-1,team_id=teamid_output))
		rinfo = (idc.result_lap_data(subsession_id=eachId,simsession_number=0,team_id=teamid_output))				
	## get the best time from each record
	qbest_time = next(
    (lap['lap_time'] for lap in qinfo if lap['personal_best_lap']),
    None
	)	
	rbest_time = next(
    (lap['lap_time'] for lap in rinfo if lap['personal_best_lap']),
    None
	)
	iRgain = int(i['newi_rating']) - int(i['oldi_rating'])
	SFgain = int(i['new_sub_level']) - int(i['old_sub_level'])
	## prrint everything
	print(str("Date:"),i['session_start_time'])
	print(str("Subsession Id:"),eachId)
	print(str("Series Name:"),i['series_name'])
	print(str("Car:"),car_name(i['car_id']))
	print(str("Track:"),i['track']['track_name'])
	if qbest_time is None:
		print("No Qualifying Time Set")
	else:
		print(str("Quali Time:"),time_convert(qbest_time))
	if rbest_time is None:
		print("No valid lap in race")
	else:
		print(str("Race Time:"),time_convert(rbest_time))
	print(str("Incidents"),i['incidents'])
	print(str("Old iRating:"),i['oldi_rating'])
	print(str("New iRating:"),i['newi_rating'])
	print(str("iRating Gain:"),iRgain)
	print(str("Old Safety Rating:"),i['old_sub_level'])
	print(str("New Safety Rating:"),i['new_sub_level'])
	print(str("Safety Rating Gain:"),SFgain)
	print(str("Start Position:"),i['start_position'])
	print(str("Finish Position"),i['finish_position'])
	print(str("Laps:"),i['laps'])
	print(str("Laps Led:"),i['laps_led'])
	print(str("Points:"),i['points'])
	print(str("Strength of Field:"),i['strength_of_field'])
	print(str("Season Year:"),i['season_year'])
	print(str("Season:"),i['season_quarter'])
	print(str("Race Week:"),i['race_week_num'])
	print(end='\n')


## put everything into a variable instead of printing it directly to the terminal. This will then be used to create the input query
#while True:
#	try:
#		for i in recentraces['races']:
#			## get the subsession id for each row in recent race data
#			eachId = i['subsession_id']
#			## get the times for quali and reace here
#			try:
#				qinfo = (idc.result_lap_data(subsession_id=eachId,simsession_number=-1,cust_id=ir_memId))
#				rinfo = (idc.result_lap_data(subsession_id=eachId,simsession_number=0,cust_id=ir_memId))
#			except:
#				team_race = (idc.result(subsession_id=eachId))
#				teamid_var = team_race['session_results'][2]
#				for team in teamid_var.get('results', []):
#					for driver in team.get('driver_results', []):
#						if driver['display_name'] == drivername:
#							teamid_output = str(driver['team_id'])[1:]
#				qinfo = (idc.result_lap_data(subsession_id=eachId,simsession_number=-1,team_id=teamid_output))
#				rinfo = (idc.result_lap_data(subsession_id=eachId,simsession_number=0,team_id=teamid_output))
#			## get the best time from each record
#			qbest_time = next(
#		    (lap['lap_time'] for lap in qinfo if lap['personal_best_lap']),
#		    None
#			)	
#			rbest_time = next(
#		    (lap['lap_time'] for lap in rinfo if lap['personal_best_lap']),
#		    None
#			)
#			iRgain = int(i['newi_rating']) - int(i['oldi_rating'])
#			SFgain = int(i['new_sub_level']) - int(i['old_sub_level'])
#			## prrint everything
#			racedate = i['session_start_time']
#			seriesname = i['series_name']
#			carn = car_name(i['car_id'])
#			trackname = i['track']['track_name']
#			if qbest_time is None:
#				qtime = str("0:0.000")
#			else:
#				qtime = time_convert(qbest_time)
#			if rbest_time is None:
#				rtime = str("0:00.000")
#			else:
#				rtime = time_convert(rbest_time)
#			inc = i['incidents']
#			oldir = i['oldi_rating']
#			newir = i['newi_rating']
#			oldsr = i['old_sub_level']
#			newsr = i['new_sub_level']
#			startp = i['start_position']
#			finishp = i['finish_position']
#			lapsdriven = i['laps']
#			lapsled = i['laps_led']
#			points = i['points']
#			sof = i['strength_of_field']
#			syear = i['season_year']
#			sseason = i['season_quarter']
#			weeknum = i['race_week_num']
#			#print(eachId, racedate,seriesname,carn,trackname,qtime,rtime,inc,oldir,newir,oldsr,newsr,startp,finishp,lapsdriven,lapsled,points,sof,syear,sseason,weeknum)
#	except:
#		break

