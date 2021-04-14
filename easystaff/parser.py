import requests
from bs4 import BeautifulSoup
import json
import re

from easystaff import const


class EasyStaff:
    def __init__(self, username, password, cf_code, excludes=None):
        self.session = requests.Session()
        self.session.headers.update(const.USE_HEADERS)
        self.username = username
        self._password = password
        self.cf_code = cf_code
        if excludes is None:
            self.excludes = []
        else:
            self.excludes = excludes
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

    def get_available_bookings(self):
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
        lectures = json.loads(groups[0])

        available_bookings = []
        for lecture in lectures:
            for booking in lecture["prenotazioni"]:
                entry_id = booking["entry_id"]
                if entry_id not in self.excludes:
                    available_bookings.append(entry_id)
        self.session.close()
        return available_bookings

    def book_lecture(self, lecture_id):
        booking_res = self.session.get("https://easystaff.divsi.unimi.it/PortaleStudenti/call_ajax.php", params=(
            ('language', 'it'),
            ('mode', 'salva_prenotazioni'),
            ('codice_fiscale', self.cf_code),
            ('id_entries', f"[{lecture_id}]"),
            ('id_btn_element', f"{lecture_id}"),
        ))
        assert booking_res.status_code == 200
        print(lecture_id, "Booked") # DEBUG / Can be changed to make the user aware of the booking
