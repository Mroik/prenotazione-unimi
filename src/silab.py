import requests

from src import const


class SiLab:
    def __init__(self):
        self.token = None
        self.session = requests.Session()

    def get_slots(self):
        resp = self.session.post(const.ENDPOINT_SILAB_SLOTS)
        assert resp.status_code == 200
        return resp.json()["rooms"]

    def login(self, username, password):
        resp = self.session.post(
            const.ENDPOINT_SILAB_LOGIN,
            data={
                "username": username,
                "password": password
            }
        )
        assert resp.status_code == 200
        self.token = resp.json()["jwt"]
        assert self.token != ""

    def book_slot(self, slotid):
        assert self.token is not None

        resp = self.session.post(
            const.ENDPOINT_SILAB_BOOK + slotid,
            headers={
                "authorization": "Bearer " + self.token
            }
        )
        assert resp.status_code == 200
        return True if resp.json()["status"] == "success" else False
