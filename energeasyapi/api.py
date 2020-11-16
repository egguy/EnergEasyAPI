from json import JSONDecodeError

import httpx

from energeasyapi.constants import BASE_URL
from energeasyapi.exceptions import InvalidLogin
from energeasyapi.utils import DevicesContainer


class EnergEasyAPI(object):
    def __init__(self, username=None, password=None):
        super(EnergEasyAPI, self).__init__()

        self.username = username
        self.password = password

        self.session = httpx.AsyncClient()
        # Fake user agent
        self.session.headers[
            'User-Agent'] = "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0"
        self.logged = False
        self.setup_response = None
        self.equipments = DevicesContainer()
        self.id = None

        if self.login and self.password:
            self.login()

    async def login(self):
        self.logged = False
        url = "{}/user/login".format(BASE_URL)
        params = {
            "userId": self.username,
            "userPassword": self.password,
        }

        response = await self.session.post(url, data=params)
        # print(response.content)
        try:
            response_payload = response.json()
        except JSONDecodeError:
            raise InvalidLogin()
        if response_payload.get("success", False) is True:
            self.logged = True
            return True
        raise InvalidLogin()

    async def fetch_setup(self):
        if not self.logged:
            raise InvalidLogin

        url = "{}/api/enduser-mobile-web/enduserAPI/setup".format(BASE_URL)
        response = await self.session.get(url)
        if response.status_code < 200 or 300 < response.status_code:
            await self.login()
            return self.fetch_setup()
        self.setup_response = response.json()

    async def get_id(self):
        if not self.setup_response:
            await self.fetch_setup()
        return self.setup_response["id"]

    def refresh_equipments(self):
        for eqp_data in self.setup_response['devices']:
            self.equipments.add(eqp_data)

    async def list_equipments(self):
        if not self.setup_response:
            await self.fetch_setup()

        if not self.equipments.devices:
            self.refresh_equipments()

        return self.equipments.list_devices()

    async def send_command(self, uri, command):
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
        response = await self.session.post(url, json=payload)
        # print(response, response.content)
        if response.status_code == 401:
            await self.login()
            return self.send_command(uri, command)

        return response
