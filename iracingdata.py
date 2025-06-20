import configparser
from iracingdataapi.client import irDataClient

cfg = configparser.ConfigParser()
cfg.read("config.ini")
user = cfg["credentials"]["user"]
pwd  = cfg["credentials"]["pass"]
memId = cfg['credentials']['memberId']


idc = irDataClient(username=user, password=pwd)




# get the summary data of a member
#print(idc.stats_member_summary(cust_id=memId))
#print(idc.member_info())
info=(idc.stats_member_recent_races(cust_id=memId))
#print(idc.stats_member_yearly(cust_id=memId))
#print(idc.result(subsession_id=77807155))
#print(idc.stats_member_career(cust_id=memId))
races=(idc.stats_member_recent_races(cust_id=memId))
cars=(idc.get_cars())
# say your dict is called data
first_newi = info['races'][0]['newi_rating']   # grabs the first newi_rating :contentReference[oaicite:0]{index=0}
first_safety = info['races'][0]['new_sub_level']

#all_newi = [race['newi_rating'] for race in info['races']]
latestraces = [race['series_name'] for race in races['races']]
#print(all_newi)
print("Current iRating:",first_newi)
print("Current Safety Rating:",first_safety)
print(latestraces)


# build a lookup dict once
cars_by_id = {c['car_id']: c for c in cars}

# then to grab car 123:
car = cars_by_id.get(169)
if car:
    print(car['car_name'])
else:
    print("No car with that ID.")





#Internal Helpers
#- __init__(username, password, silent=False): set up the client with creds; silent mutes console output.
#- _encode_password(username, password): hash/encode your login before sending.
#- _login(): authenticate against iRacing’s API.
#- _build_url(endpoint): prepend base URL to an API endpoint.
#- _get_resource(endpoint, payload): GET data from an endpoint with optional payload.
#- _get_resource_or_link(url, payload): fetch data or grab a download link if returned.
#- _get_chunks(chunks): merge paginated chunks into one response.
#- _add_assets(objects, assets, id_key): attach asset info (graphics, specs) from assets to each object by id_key.
#- _parse_csv_response(text): turn raw CSV text into Python structures.
#
#Constants & Lookups
#- constants_categories(): fetch category constants (e.g., “Pro”, “Am”).
#- constants_divisions(): get division constants.
#- constants_event_types(): list event-type codes.
#- lookup_countries(): pull iRacing’s country codes.
#- lookup_drivers(search_term, league_id=None): search drivers by search_term, optionally within a league_id.
#- lookup_licenses(): list license levels and colors.
#- lookup_club_history(season_year, season_quarter): get club standings for a given year/quarter.
#
#Core Data Fetchers
#- cars(): list all car definitions.
#- tracks(): list all track definitions.
#- series(): list all racing series.
#- get_series(): alias to series().
#- get_series_assets(): fetch asset data (logos, skins) for each series.
#- series_past_seasons(series_id): list past seasons of a given series_id.
#- series_seasons(include_series=False): list seasons (optionally grouped by series).
#- series_stats(): global stats across all series.
#
#Asset Managers
#- get_cars(): same as cars().
#- get_cars_assets(): same as get_series_assets() but for cars.
#- get_tracks(): same as tracks().
#- get_tracks_assets(): fetch skins/assets for tracks.
#- get_carclasses(): list car classes (e.g., “GT3”, “DTM”).
#- hosted_sessions(): list your hosted sessions.
#- hosted_combined_sessions(package_id): get combined-session info for a hosted package_id.
#
#League Endpoints
#- league_directory(search, tag, restrict_to_members, minimum_roster_count, lowerbound, upperbound, sort, order): search leagues.
#- league_get(league_id, include_licenses=False): get league info.
#- league_membership(include_league=False): list your league memberships.
#- league_roster(league_id, include_licenses=False): list members in a league.
#- league_seasons(league_id, retired=False): list seasons in a league.
#- league_season_standings(league_id, season_id, car_class_id=None, car_id=None): get standings.
#- league_season_sessions(league_id, season_id, results_only=False): list sessions.
#- league_cust_league_sessions(mine, package_id): custom league session queries.
#- league_get_points_systems(league_id, season_id): get point systems used.
#
#Season & Schedule
#- season_list(season_year, season_quarter): list seasons for a year/quarter.
#- season_race_guide(start_from, include_end_after_from=False): get upcoming races from a date.
#- season_spectator_subsessionids(event_types): get subsession IDs for spectating given event_types.
#- schedule(): fetch the global schedule.
#
#Race & Results
#- race_details(subsession_id): get detailed race metadata.
#- race_results(subsession_id): final results for a subsession_id.
#- leaderboard(subsession_id): live leaderboard data.
#- lap_times(subsession_id): lap-time summaries.
#- points(subsession_id): points awarded per finisher.
#
#Result Drill-Downs
#- result(subsession_id, include_licenses=False): raw result data.
#- result_lap_data(subsession_id, simsession_number, cust_id=None, team_id=None): per-car lap data.
#- result_lap_chart_data(subsession_id, simsession_number): chart-friendly lap data.
#- result_event_log(subsession_id, simsession_number): event logs (incidents).
#- result_search_series(season_year, season_quarter, race_week_num=None, official_only=False, event_types=None, category_ids=None): search races in series.
#- result_search_hosted(start_range_begin, start_range_end, league_season_id=None, car_id=None, track_id=None, category_ids=None, team_id=None): search hosted events.
#- result_season_results(season_id, event_type, race_week_num=None): get season’s results by week.
#
#Member Endpoints
#- member(cust_id, include_licenses=False): fetch a member’s profile.
#- member_info(): your own member info.
#- member_profile(cust_id): detailed profile for cust_id.
#- member_awards(cust_id): list awards/trophies.
#- member_chart_data(cust_id, category_id, chart_type): analytics charts (e.g., safety) for cust_id.
#
#Member Stats
#- stats_member_bests(cust_id, car_id=None): best lap/performance for a car.
#- stats_member_career(cust_id): overall career stats.
#- stats_member_recent_races(cust_id): recent race history.
#- stats_member_summary(cust_id): high-level summary (iRating, SR).
#- stats_member_yearly(cust_id): yearly breakdown.
#- stats_member_recap(cust_id, year, quarter): quarterly recap.
#
#Season Stats
#- stats_season_driver_standings(season_id, car_class_id, race_week_num=None, club_id=None, division=None): driver standings.
#- stats_season_team_standings(season_id, car_class_id, race_week_num=None): team standings.
#- stats_season_qualify_results(season_id, car_class_id, race_week_num=None, club_id=None, division=None): qualifying results.
#- stats_season_tt_results(season_id, car_class_id, race_week_num=None, club_id=None, division=None): time-trial results.
#- stats_season_tt_standings(season_id, car_class_id, race_week_num=None, club_id=None, division=None): TT standings.
#- stats_season_supersession_standings(season_id, car_class_id, race_week_num=None, club_id=None, division=None): supersession standings.
#
#Other Stats
#- stats_car_class_records(car_class_id): all-time records for a class.
#- stats_class_season_totals(season_id): season totals by class.
#- stats_world_records(car_id, track_id, season_year=None, season_quarter=None): world-record lap times.
#
#Teams
#- team(team_id, include_licenses=False): get team info and optionally member licenses.
