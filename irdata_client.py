import base64
import csv
import hashlib
import time
from datetime import datetime, timedelta
from io import StringIO
from typing import Dict, Optional, Union

import requests


class irDataClient:
    def __init__(self, username: str = None, password: str = None, silent: bool = False):
        self.authenticated = False
        self.session = requests.Session()
        self.base_url = "https://members-ng.iracing.com"
        self.silent = silent

        self.username = username
        self.encoded_password = self._encode_password(username, password)

    def _encode_password(self, username: str, password: str) -> str:
        initial_hash = hashlib.sha256((password + username.lower()).encode("utf-8")).digest()
        return base64.b64encode(initial_hash).decode("utf-8")

    def _login(self) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"email": self.username, "password": self.encoded_password}
        try:
            r = self.session.post(
                "https://members-ng.iracing.com/auth",
                headers=headers,
                json=data,
                timeout=5.0,
            )
            if r.status_code == 429:
                ratelimit_reset = r.headers.get("x-ratelimit-reset")
                if ratelimit_reset:
                    reset_datetime = datetime.fromtimestamp(int(ratelimit_reset))
                    delta = reset_datetime - datetime.now() + timedelta(milliseconds=500)
                    if not self.silent:
                        print(f"Rate limited, waiting {delta.total_seconds()} seconds")
                    if delta.total_seconds() > 0:
                        time.sleep(delta.total_seconds())
                return self._login()
        except requests.Timeout:
            raise RuntimeError("Login timed out")
        except requests.ConnectionError:
            raise RuntimeError("Connection error")
        else:
            response_data = r.json()
            if r.status_code == 200 and response_data.get("authcode"):
                self.authenticated = True
                return "Logged in"
            raise RuntimeError("Error from iRacing: ", response_data)

    def _build_url(self, endpoint: str) -> str:
        return self.base_url + endpoint

    def _get_resource_or_link(self, url: str, payload: dict = None) -> list[Union[Dict, str], bool]:
        if not self.authenticated:
            self._login()
            return self._get_resource_or_link(url, payload=payload)

        r = self.session.get(url, params=payload)

        if r.status_code == 401 and self.authenticated:
            self.authenticated = False
            return self._get_resource_or_link(url, payload=payload)

        if r.status_code == 429:
            ratelimit_reset = r.headers.get("x-ratelimit-reset")
            if ratelimit_reset:
                reset_datetime = datetime.fromtimestamp(int(ratelimit_reset))
                delta = reset_datetime - datetime.now() + timedelta(milliseconds=500)
                if not self.silent:
                    print(f"Rate limited, waiting {delta.total_seconds()} seconds")
                if delta.total_seconds() > 0:
                    time.sleep(delta.total_seconds())
            return self._get_resource_or_link(url, payload=payload)

        if r.status_code != 200:
            raise RuntimeError("Unhandled Non-200 response", r)
        data = r.json()
        if not isinstance(data, list) and "link" in data.keys():
            return [data.get("link"), True]
        return [data, False]

    def _get_resource(self, endpoint: str, payload: Optional[dict] = None) -> Optional[Union[list, dict]]:
        request_url = self._build_url(endpoint)
        resource_obj, is_link = self._get_resource_or_link(request_url, payload=payload)

        if not is_link:
            return resource_obj
        r = self.session.get(resource_obj)

        if r.status_code == 401 and self.authenticated:
            self.authenticated = False
            self._login()
            return self._get_resource(endpoint, payload=payload)

        if r.status_code == 429:
            ratelimit_reset = r.headers.get("x-ratelimit-reset")
            if ratelimit_reset:
                reset_datetime = datetime.fromtimestamp(int(ratelimit_reset))
                delta = reset_datetime - datetime.now()
                if delta.total_seconds() > 0:
                    time.sleep(delta.total_seconds())
            return self._get_resource(endpoint, payload=payload)

        if r.status_code != 200:
            raise RuntimeError("Unhandled Non-200 response", r)

        content_type = r.headers.get("Content-Type")
        if "application/json" in content_type:
            return r.json()
        if "text/csv" in content_type or "text/plain" in content_type:
            return self._parse_csv_response(r.text)
        print("Error: Unsupported Content-Type")
        return None

    def _get_chunks(self, chunks) -> list:
        if not isinstance(chunks, dict):
            return []
        base_url = chunks.get("base_download_url")
        urls = [base_url + x for x in chunks.get("chunk_file_names")]
        list_of_chunks = [self.session.get(url).json() for url in urls]
        output = [item for sublist in list_of_chunks for item in sublist]
        return output

    def _parse_csv_response(self, text: str) -> list:
        csv_data = []
        reader = csv.reader(StringIO(text), delimiter=",")
        headers = [header.lower() for header in next(reader)]
        for row in reader:
            if len(row) == len(headers):
                csv_data.append(dict(zip(headers, row)))
            else:
                print("Warning: Row length does not match headers length")
        return csv_data

    def get_cars(self) -> list[Dict]:
        return self._get_resource("/data/car/get")

    def result(self, subsession_id: int, include_licenses: bool = False) -> Dict:
        payload = {"subsession_id": subsession_id, "include_licenses": include_licenses}
        return self._get_resource("/data/results/get", payload=payload)

    def result_lap_data(self, subsession_id: int, simsession_number: int = 0, cust_id: Optional[int] = None, team_id: Optional[int] = None) -> list[Optional[Dict]]:
        if not cust_id and not team_id:
            raise RuntimeError("Please supply either a cust_id or a team_id")
        payload = {"subsession_id": subsession_id, "simsession_number": simsession_number}
        if cust_id:
            payload["cust_id"] = cust_id
        if team_id:
            payload["team_id"] = team_id
        resource = self._get_resource("/data/results/lap_data", payload=payload)
        if resource.get("chunk_info"):
            return self._get_chunks(resource.get("chunk_info"))
        return []

    def stats_member_recent_races(self, cust_id: Optional[int] = None) -> Dict:
        payload = {}
        if cust_id:
            payload = {"cust_id": cust_id}
        return self._get_resource("/data/stats/member_recent_races", payload=payload)

