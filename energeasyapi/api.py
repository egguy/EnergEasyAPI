import requests

from energeasyapi.constants import BASE_URL
from energeasyapi.devices import Shutter
from energeasyapi.exceptions import InvalidLogin


class EnergEasyAPI(object):
    def __init__(self):
        super(EnergEasyAPI, self).__init__()
        self.session = requests.session()
        # Fake user agent
        self.session.headers[
            'User-Agent'] = "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0"
        self.logged = False
        self.setup_response = None
        self.equipments = []

    def login(self, username: str, password: str):
        url = "{}/user/login".format(BASE_URL)
        params = {
            "userId": username,
            "userPassword": password,
        }

        response = self.session.post(url, data=params)
        if response.json().get("success", False) is True:
            self.logged = True
            return True
        raise InvalidLogin()

    def fetch_setup(self):
        if not self.logged:
            raise InvalidLogin

        url = "{}/api/enduser-mobile-web/enduserAPI/setup".format(BASE_URL)
        self.setup_response = self.session.get(url).json()

    def list_equipments(self):
        if not self.setup_response:
            self.fetch_setup()

        if not self.equipments:
            for eqp in self.setup_response['devices']:
                # Rolling shutter
                if eqp['controllableName'] == "io:RollerShutterGenericIOComponent":
                    self.equipments.append(Shutter(
                        eqp['deviceURL'],
                        eqp["label"],
                    ))

        return self.equipments

    def send_command(self, uri, command):
        url = "{}/api/enduser-mobile-web/enduserAPI/exec/apply".format(BASE_URL)
        payload = {
            "label": "identification",
            "actions": [
                {
                    "commands": [
                        command
                    ],
                    "deviceURL": uri
                }
            ],
            "internal": False
        }
        return self.session.post(url, json=payload)
