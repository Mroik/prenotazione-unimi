import requests

from . import const


class SiLab:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.session.headers.update(const.USE_HEADERS)

    def get_slots(self):
        if self.token is None:
            resp = self.session.post(const.ENDPOINT_SILAB_SLOTS)
        else:
            resp = self.session.post(const.ENDPOINT_SILAB_SLOTS, headers={
                "authorization": "Bearer " + self.token
            })
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
                const.ENDPOINT_SILAB_BOOK + str(slotid),
                headers={
                    "authorization": "Bearer " + self.token
                }
        )
        if resp.status_code == 504:
            return False
        assert resp.status_code == 200
        return True if resp.json()["status"] == "success" else False

    def unbook_slot(self, slotid):
        assert self.token is not None

        resp = self.session.post(
                const.ENDPOINT_SILAB_UNBOOK + str(slotid),
                headers={
                    "authorization": "Bearer " + self.token
                }
        )
        if resp.status_code == 504:
            return False
        assert resp.status_code == 200
        return True if resp.json()["status"] == "success" else False

    def get_penalty(self):
        assert self.token is not None

        resp = self.session.post(const.ENDPOINT_SILAB_SLOTS, headers={
            "authorization": "Bearer " + self.token
        })
        assert resp.status_code == 200
        resp = resp.json()["rooms"][0]
        return resp["absences"], resp["maxbookings"]

    def confirm_silab(self, room_id):
        assert self.token is not None
        resp = self.session.post(
                const.ENDPOINT_SILAB_CONFIRM + str(room_id),
                headers={
                    "authorization": "Bearer " + self.token
                }
        )
        if resp.status_code != 200:
            raise Exception("Something went wrong")
        return resp.json()["longMessage"]
