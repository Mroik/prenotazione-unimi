#!/bin/python
import requests
from bs4 import BeautifulSoup as bs
import sys
import json

if len(sys.argv) < 4:
    print("user pass cod.fis")
    sys.exit()

# Metti le tue credenziali
userName = sys.argv[1]
password = sys.argv[2]

escludi = []
if len(sys.argv) > 4:
    for x in range(4, len(sys.argv)):
        escludi.append(sys.argv[x])

s = requests.Session()

data = s.get("https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php??response_type=token&client_id=client&redirect_uri=https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=login&scope=openid+profile")

data = data.text
data = bs(data, "html.parser")
lt_code = data.find(id="hLT")["value"]
exec_code = data.find(id="hExecution")["value"]

endpoint = "https://cas.unimi.it/login"

params = {
        "username": userName,
        "selTipoUtente": "S",
        "password": password,
        "hCancelLoginLink": "http://www.unimi.it",
        "hForgotPasswordLink": "https://auth.unimi.it/password/",
        "lt": lt_code,
        "execution": exec_code,
        "service": "https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php??response_type=token&client_id=client&redirect_uri=https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=login&scope=openid+profile",
        "_eventId": "submit",
        "_responsive": "responsive"
}

req = s.post(endpoint, data = params)
if req.status_code == 200:
    print("Login: success")
else:
    print("Login: failed")
req = s.get(endpoint)

########### FINE LOGIN #####################

data = s.get("https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php??response_type=token&client_id=client&redirect_uri=https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=login&scope=openid+profile")

param = {
        "access_token": data.text[131:131+193]
}

data = s.post("https://easystaff.divsi.unimi.it/PortaleStudenti/login.php?from=&from_include=", data=param)
data = s.get("https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=prenotalezione&include=prenotalezione&_lang=it")

id_entries = []
data = json.loads(data.text[data.text.find("JSON.parse('")+12:data.text.find("JSON.parse('")+12+data.text[data.text.find("JSON.parse('")+12:].find(";")-3])
for x in data:
    for y in x["prenotazioni"]:
        if not y["nome"] in escludi:
            id_entries.append(y["entry_id"])

#### FINALMENTE ZONA PRENOTAZIONE ###########

cod_fiscale = sys.argv[3]
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Referer': 'https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=prenotalezione&include=prenotalezione_gestisci&_lang=it',
    'TE': 'Trailers',
}

print("Prenotazione in corso...")
for id_lezione in id_entries:
    params = (
        ('language', 'it'),
        ('mode', 'salva_prenotazioni'),
        ('codice_fiscale', '{}'.format(cod_fiscale)),
        ('id_entries', '[{}]'.format(id_lezione)),
        ('id_btn_element', '{}'.format(id_lezione)),
    )
    
    response = requests.get('https://easystaff.divsi.unimi.it/PortaleStudenti/call_ajax.php', headers=headers, params=params)
    #print(id_lezione, response.status_code) # DEBUG

print("Fine prenotazione")
