import configparser
import ast
import logging
from pathlib import Path
from irdata_client import irDataClient

logging.basicConfig(level=logging.INFO)

cfg = configparser.ConfigParser()
config_path = Path(__file__).resolve().parent / "config.ini"
cfg.read(config_path)
user = cfg["iracingcreds"]["user"]
pwd = cfg["iracingcreds"]["pass"]
memId = cfg["iracingcreds"]["memberId"]

## since the carlist updates every 3 months with new added cars,
## this needs to be run before every new season

idc = irDataClient(username=user, password=pwd)

existing_ids: set[int] = set()
# Always write the car list next to this script so cron jobs
# don't place it in an unexpected directory
carlist_path = Path(__file__).resolve().parent / "car_list.cfg"
if carlist_path.exists():
    try:
        with carlist_path.open("r", encoding="utf-8") as f:
            old_cars = ast.literal_eval(f.read())
        existing_ids = {
            c.get("car_id")
            for c in old_cars
            if c.get("car_id") is not None
        }
        logging.info("Loaded %d cars from existing list", len(existing_ids))
    except Exception as exc:  # pragma: no cover - just logging
        logging.warning("Failed to read existing car list: %s", exc)

try:
    carcl = idc.get_cars()
except Exception as exc:  # pragma: no cover - just logging
    logging.error("Failed to fetch car list: %s", exc)
    logging.error("No cars could be loaded")
    raise
else:
    new_ids = {
        c.get("car_id")
        for c in carcl
        if c.get("car_id") is not None
    }
    added = len(new_ids - existing_ids)

    # Write the car list to car_list.cfg (overwrite if it exists)
    with carlist_path.open("w", encoding="utf-8") as f:
        f.write(str(carcl))
    logging.info("Added %d new cars", added)

