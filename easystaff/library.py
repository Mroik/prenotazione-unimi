import json
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from easystaff import const


class Library:
    def __init__(self, cf_code, full_name, email):
        self.cf_code = cf_code
        self.full_name = full_name
        self.email = email
        self.session = requests.Session()

    def _get_token():
        resp = self.session.get(const.LIBRARY_ENDPOINT,
                                params=(("include", "form"),))
        token = ""
        for x in BeautifulSoup(resp.text, "html.parser").find_all("input"):
            try:
                if x["name"] == "_token":
                    token = x["value"]
                    break
            except Exception:
                pass
        assert token != ""
        return token

    def _get_risorsa(self,library, service, token, timeslot):
        resp = self.session.post(
                const.LIBRARY_ENDPOINT,
                data={
                    "_token": token,
                    "raggruppamento_aree": "all",
                    "area": library,
                    "raggruppamento_servizi": 0,
                    "servizio": service,
                    "data_inizio": datetime.today().strftime("%d-%m-%Y"),
                    "codice_fiscale": self.cf_code,
                    "cognome_nome": self.full_name,
                    "email": self.email
                },
                params=(("include", "timetable"),)
        )
        for x in BeautifulSoup(resp.text, "html.parser").find_all("p"):
            found = re.findall("(?<=risorsa'\)\.val\(')\d+",
                                str(x.get("onclick")))
            if len(found) == 0:
                continue
            risorsa = found[0]
            found = re.findall("(?<=timestamp'\)\.val\(')\d+",
                                str(x.get("onclick")))
            if found[0] == timeslot:
                break
            else:
                risorsa = None
        assert risorsa != None
        return risorsa

    def get_available_libraries():
        resp = self.session.get(const.LIBRARY_ENDPOINT,
                                params=(("include", "form"),))
        avail_biblio = BeautifulSoup(resp.text, "html.parser").find_all(id="area")[0]
        libraries = {}
        for opt in avail_biblio.find_all("option"):
            libraries[opt["value"]] = opt.string.replace("\n", "").replace("\t", "")
        services = json.loads(re.findall("(?<=a_s = ){.*}", resp.text)[0])
        return libraries, services

    # This method is not really needed, I decided to keep it anyway
    def get_available_dates(library, service):
        resp = self.session.get(const.LIBRARY_AJAX_ENDPOINT, params=(
            ("tipo", "data_inizio_form"),
            ("area", library),
            ("servizio", service)
        ))
        return resp.json()

    # Returns the available timeslots in datetime format, this way we can
    # extract date and time from it, the website itself uses unix timestamps,
    # so when booking convert back to unix
    def get_avalilable_timeslots(self, library, service):
        resp = self.session.post(
                const.LIBRARY_ENDPOINT,
                data={
                    "_token": self._get_token(),
                    "raggruppamento_aree": "all",
                    "area": library,
                    "raggruppamento_servizi": 0,
                    "servizio": service,
                    "data_inizio": datetime.today().strftime("%d-%m-%Y"),
                    "codice_fiscale": self.cf_code,
                    "cognome_nome": self.full_name,
                    "email": self.email
                },
                params=(("include", "timetable"),)
        )
        timeslots = []
        for slot in BeautifulSoup(resp.text, "html.parser").find_all("p"):
            found = re.findall("(?<=timestamp'\)\.val\(')\d+", str(slot.get("onclick")))
            if len(temp) == 0:
                continue
            timeslots.append(datetime.fromtimestamp(int(found[0])))
        return timeslots

    def book_timeslot(self, library, service, timeslot):
        token = self._get_token()
        risorsa = self._get_risorsa(library, service, token, timeslot)
        resp = self.session.post(
                const.LIBRARY_ENDPOINT,
                data={
                    "servizio": service,
                    "durata_servizio": 16200, # Constant
                    "timestamp": timeslot,
                    "endtime": int(timeslot) + 16200,
                    "risorsa": risorsa,
                    "data_inizio": datetime.today().strftime("%d-%m-%Y"),
                    "area": library,
                    "cognome_nome": self.full_name,
                    "email": self.email,
                    "codice_fiscale": self.cf_code,
                    "_token": token
                },
                params=(("include", "review"),)
        )
        entry = None
        for x in BeautifulSoup(resp.text, "html.parser").find_all("input"):
            if x["name"] == "entry":
                entry = x["value"]
                break
        assert entry != None

        resp= self.session.post(
                const.LIBRARY_ENDPOINT,
                data={
                    "public_primary": self.cf_code,
                    "entry": entry,
                    "_token": token,
                    "conferma": ""
                },
                params=(("include", "confirmed"),)
        )
        assert resp.status_code == 200
