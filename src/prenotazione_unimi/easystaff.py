import re
import json

import requests
from bs4 import BeautifulSoup as bs

from exceptions import(
        EasystaffLoginForm,
        EasystaffLogin,
        EasystaffBookingPage,
        EasystaffBooking,
)


FORM_URL = "https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php??response_type=token&client_id=client&redirect_uri=https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=login&scope=openid+profile"
LOGIN_URL = "https://cas.unimi.it/login"
BOOKING_PAGE_URL = "https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=prenotalezione&include=prenotalezione&_lang=it"
EASYSTAFF_LOGIN_URL = "https://easystaff.divsi.unimi.it/PortaleStudenti/login.php?from=&from_include="
BOOK_URL = "https://easystaff.divsi.unimi.it/PortaleStudenti/call_ajax.php?language=it&mode=salva_prenotazioni&codice_fiscale={}&id_entries=[{}]"


class Easystaff:
    def __init__(self):
        self._token = None
        self._session = requests.Session()


    def _get_login_form(self):
        res = self._session.get(FORM_URL)
        if not res.ok:
            raise EasystaffLoginForm(f"Couldn't fetch CAS form, responded with {res.status_code}")

        form_data = {
                "selTipoUtente": "S",
                "hCancelLoginLink": "http://www.unimi.it",
                "hForgotPasswordLink": "https://auth.unimi.it/password/",
                "service": "https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php??response_type=token&client_id=client&redirect_uri=https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=login&scope=openid+profile",
                "_eventId": "submit",
                "_responsive": "responsive",
        }

        form_soup = bs(res.text, "lxml")
        lt = form_soup.find_all(id="hLT")[0]["value"]
        execution = form_soup.find_all(id="hExecution")[0]["value"]

        form_data["lt"] = lt
        form_data["execution"] = execution
        return form_data


    def login(self, username: str, password: str):
        payload = self._get_login_form()
        payload["username"] = username
        payload["password"] = password

        res = self._session.post(LOGIN_URL, data=payload)
        if not res.ok:
            raise EasystaffLogin(f"Failed to login, responded with {res.status_code}")

        token_url = res.text[48:348]
        token_url = token_url[token_url.find("access_token") + 13:]
        res = self._session.post(
                EASYSTAFF_LOGIN_URL,
                data={"access_token": token_url}
        )
        if not res.ok:
            raise EasystaffLogin(f"Failed on access token, responded with {res.status_code}")


    def get_lessons(self):
        res = self._session.get(BOOKING_PAGE_URL)
        if not res.ok:
            raise EasystaffBookingPage(f"Failed to fetch booking page, responded with {res.status_code}")

        lessons = re.findall("JSON\.parse\('.*'\)", res.text)
        lessons = json.loads(lessons[0][12:-2])
        return lessons


    def book_lesson(self, cf: str, entry: int):
        res = self._session.post(BOOK_URL.format(cf, entry))
        if not res.ok:
            raise EasystaffBooking(f"Failed to book lesson {entry}, responded with {res.status_code}")
