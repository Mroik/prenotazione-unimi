EASYSTAFF_BASE_URL = "https://orari-be.divsi.unimi.it/EasyAcademy/auth/auth_app.php"
CAS_LOGIN_URL = "https://cas.unimi.it/login"
CAS_REDIRECT_URI = "https://easystaff.divsi.unimi.it/PortaleStudenti/index.php?view=login&scope=openid+profile"
USE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
}
LIBRARY_ENDPOINT = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/index.php"
LIBRARY_AJAX_ENDPOINT = "https://orari-be.divsi.unimi.it/PortaleEasyPlanning/biblio/ajax.php"
