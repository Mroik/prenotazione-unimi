import json
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from easystaff import const


class EasyStaff:
    def __init__(self, username, password, cf_code, excludes=None):
        self.session = requests.Session()
        self.session.headers.update(const.USE_HEADERS)
        self.username = username
        self._password = password
        self.cf_code = cf_code
        self.excludes = [] if excludes is None else excludes
        self._access_token = None

    def _get_prelogin_params(self):
        prelogin_res = self.session.get(const.EASYSTAFF_BASE_URL, params=(
            ("response_type", "token"),
            ("client_id", "client"),
            ("redirect_uri", const.CAS_REDIRECT_URI),
        ))
        assert prelogin_res.status_code == 200
        soup = BeautifulSoup(prelogin_res.text, "html.parser")
        lt_code = soup.find(id="hLT")["value"]
        exec_code = soup.find(id="hExecution")["value"]
        return lt_code, exec_code

    def _cas_login(self, lt_code, exec_code):
        auth_res = self.session.post(const.CAS_LOGIN_URL, data={
            "username": self.username,
            "password": self._password,
            "lt": lt_code,
            "execution": exec_code,
            "selTipoUtente": "S",
            "hCancelLoginLink": "http://www.unimi.it",
            "hForgotPasswordLink": "https://auth.unimi.it/password/",
            "service": "https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php"
                       "??response_type=token&client_id=client&redirect_uri=https://easystaff.divsi.unimi.it"
                       "/PortaleStudenti/index.php?view=login&scope=openid+profile",
            "_eventId": "submit",
            "_responsive": "responsive"
        })
        assert auth_res.status_code == 200
        assert "Autenticazione non riuscita" not in auth_res

    def _easystaff_login(self):
        check_res = self.session.get("https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php", params=(
            ("?response_type", "token"),
            ("client_id", "client"),
            ("redirect_uri", const.CAS_REDIRECT_URI),
            ("scope", "openid profile")
        ))
        assert check_res.status_code == 200

        exp = re.compile(r"access_token=(.*)")
        groups = exp.findall(check_res.text)
        assert len(groups) > 0
        self._access_token = groups[0]

        login_res = self.session.post(
            "https://easystaff.divsi.unimi.it/PortaleStudenti/login.php?from=&from_include=",
            data={"access_token": self._access_token}
        )
        assert login_res.status_code == 200

    def get_all_lectures(self):
        lt_code, exec_code = self._get_prelogin_params()
        self._cas_login(lt_code, exec_code)
        self._easystaff_login()
        lectures_page_res = self.session.get("https://easystaff.divsi.unimi.it/PortaleStudenti/index.php", params=(
            ("view", "prenotalezione"),
            ("include", "prenotalezione"),
            ("_lang", "it"),
        ))
        assert lectures_page_res.status_code == 200

        exp = re.compile(r"JSON\.parse\(\'(.*)\'")  # bad code inherited from bad code
        groups = exp.findall(lectures_page_res.text)
        assert len(groups) > 0
        days = json.loads(groups[0])

        available_bookings = []
        for day in days:
            for lecture in day["prenotazioni"]:
                if lecture["nome"] not in self.excludes:
                    available_bookings.append(
                        {**lecture, "date": datetime.strptime(day["data"], "%d/%m/%Y")}
                    )
        self.session.close()
        return available_bookings

    def book_lecture(self, lecture_id, dummy=False):
        if dummy:
            return print("(DRY-RUN) Booking", lecture_id)
        booking_res = self.session.get("https://easystaff.divsi.unimi.it/PortaleStudenti/call_ajax.php", params=(
            ('language', 'it'),
            ('mode', 'salva_prenotazioni'),
            ('codice_fiscale', self.cf_code),
            ('id_entries', f"[{lecture_id}]"),
            ('id_btn_element', f"{lecture_id}"),
        ))
        assert booking_res.status_code == 200


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
