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


class SiLab:
    def __init__(self):
        self.token = None
        self.session = requests.Session()

    def get_slots(self):
        resp = self.session.post(const.ENDPOINT_SILAB_SLOTS)
        return resp.json()["rooms"]

    def login(self, user, pwd):
        resp = self.session.post(
                const.ENDPOINT_SILAB_LOGIN,
                data={
                    "username": user,
                    "password": pwd
                }
        )
        self.token = resp.json()["jwt"]
        if self.token != "":
            return True
        self.token = None
        return False

    def book_slot(slotid):
        resp = self.session.post(
                const.ENDPOINT_SILAB_BOOK + slotid,
                headers={
                    "authorization": "Bearer " + token
                }
        )
        return True if resp.json()["status"] == "success" else False
