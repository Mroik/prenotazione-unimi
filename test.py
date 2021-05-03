import requests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime

def get_available_libraries():
    endpoint = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/index.php"
    resp = requests.get(endpoint, params=(
        ("include", "form"),
    ))
    data = bs(resp.text, "html.parser")
    avail_biblio = data.find_all(id="area")[0]
    results = []
    for opt in avail_biblio.find_all("option"):
        results.append({opt["value"]: opt.string.replace("\n", "").replace("\t", "")})
    services = json.loads(re.findall("(?<=a_s = ){.*}", resp.text)[0])
    return results, services


# This function is tecnically uneeded because get_available_timeslots returns
# the next days as well
def get_available_dates(location, service):
    endpoint = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/ajax.php"
    resp = requests.get(endpoint, params=(
        ("tipo", "data_inizio_form"),
        ("area", location),
        ("servizio", service)
    ))
    return json.loads(resp.text)


def get_available_timeslots(area, service, cf, full_name, email):
    s = requests.Session()
    # try getting token
    endpoint = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/index.php"
    resp = s.get(endpoint, params=(
        ("include", "form"),
    ))
    data = bs(resp.text, "html.parser")
    token = ""
    for x in data.find_all("input"):
        try:
            if x["name"] == "_token":
                token = x["value"]
                break
        except Exception:
            pass
    assert token != ""

    # get timeslotz
    endpoint = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/index.php"
    resp = s.post(
            endpoint,
            data={
                "_token": token,
                "raggruppamento_aree": "all",
                "area": area,
                "raggruppamento_servizi": 0,
                "servizio": service,
                "data_inizio": datetime.today().strftime("%d-%m-%Y"),
                "codice_fiscale": cf,
                "cognome_nome": full_name,
                "email": email
            },
            params=(("include", "timetable"),)
    )
    data = bs(resp.text, "html.parser")
    timeslots = []
    for x in data.find_all("p"):
        temp = re.findall("(?<=timestamp'\)\.val\(')\d+", str(x.get("onclick")))
        if len(temp) == 0:
            continue
        timeslots.append(datetime.fromtimestamp(int(temp[0])))
    return timeslots


def book_timeslot(area, service, cf, full_name, email, timeslot):
    s = requests.Session()
    # Token
    endpoint = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/index.php"
    resp = s.get(endpoint, params=(
        ("include", "form"),
    ))
    data = bs(resp.text, "html.parser")
    token = ""
    for x in data.find_all("input"):
        try:
            if x["name"] == "_token":
                token = x["value"]
                break
        except Exception:
            pass
    assert token != ""

    # Risorsa
    endpoint = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/index.php"
    resp = s.post(
            endpoint,
            data={
                "_token": token,
                "raggruppamento_aree": "all",
                "area": area,
                "raggruppamento_servizi": 0,
                "servizio": service,
                "data_inizio": datetime.today().strftime("%d-%m-%Y"),
                "codice_fiscale": cf,
                "cognome_nome": full_name,
                "email": email
            },
            params=(("include", "timetable"),)
    )
    data = bs(resp.text, "html.parser")
    for x in data.find_all("p"):
        temp = re.findall("(?<=risorsa'\)\.val\(')\d+", str(x.get("onclick")))
        if len(temp) == 0:
            continue
        risorsa = temp[0]
        temp = re.findall("(?<=timestamp'\)\.val\(')\d+", str(x.get("onclick")))
        if len(temp) == 0:
            risorsa = None
            continue
        if temp[0] == timeslot:
            break
        else:
            risorsa = None
    assert risorsa != None

    # Entry
    endpoint = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/index.php"
    resp = s.post(
            endpoint,
            data={
                "servizio": service,
                "durata_servizio": 16200, # Constant
                "timestamp": timeslot,
                "endtime": int(timeslot) + 16200,
                "risorsa": risorsa,
                "data_inizio": datetime.today().strftime("%d-%m-%Y"),
                "area": area,
                "cognome_nome": full_name,
                "email": email,
                "codice_fiscale": cf,
                "_token": token
            },
            params=(("include", "review"),)
    )
    data = bs(resp.text, "html.parser")
    entry = None
    for x in data.find_all("input"):
        if x["name"] == "entry":
            entry = x["value"]
            break
    assert entry != None

    # Book
    endpoint = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/index.php"
    resp = s.post(
            endpoint,
            data={
                "public_primary": cf,
                "entry": entry,
                "_token": token,
                "conferma": ""
            },
            params=(("include", "confirmed"),)
    )
    assert resp.status_code == 200
