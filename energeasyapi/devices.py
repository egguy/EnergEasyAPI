def generate_command(name, parameters=None):
    return {
        "name": name,
        "parameters": [parameters] if parameters else []
    }


class BaseDevice(object):
    def __init__(self, url: str, name: str):
        self.name = name
        self.url = url

    def load_state(self, raw_state):
        raise NotImplementedError

    def __repr__(self):
        return '<{} ({})>'.format(self.name, self.url)


class Shutter(BaseDevice):
    def __init__(self, url, name, state="closed", position=100):
        super().__init__(url, name)
        self.state = state
        self.position = position

    def close(self):
        self.position = 100
        return generate_command("close")

    def open(self):
        self.position = 0
        return generate_command("open")

    def set_position(self, position):
        self.position = position
        return generate_command("setClosure", position)

    def dimmed(self):
        return self.set_position(90)

    def stop(self):
        return generate_command("stop")

    def load_state(self, raw_state):
        states = raw_state['states']

        for state in states:
            name = state['name']
            value = state['value']
            if name == "core:ClosureState":
                self.position = value


class WaterHeater(BaseDevice):
    def __init__(self, url, name):
        super().__init__(url, name)
        self.max_temp = 80
        self.min_temp = 50
        self.target_temperature = None

        self.current_temperature = None
        self.state = None
        self.current_operation = None
        self.is_away_mode_on = False

    def load_state(self, raw_state):
        for state in raw_state['states']:
            name = state['name']
            value = state['value']
            if name == 'io:DHWModeState':
                # ['autoMode', 'manualEcoActive', 'manualEcoInactive']
                self.current_operation = value
                continue
            if name == 'core:TemperatureState':
                self.current_temperature = value
                continue
            if name == 'core:TargetTemperatureState':
                self.target_temperature = value
                continue
            if name == 'core:OperatingModeState':
                self.is_away_mode_on = value['absence'] == 'on'
        """
        states = [{'name': 'core:NameState', 'type': 3, 'value': 'DHWP Actuator'},
    {'name': 'core:VersionState', 'type': 3, 'value': '44373232383032202020'},
    {'name': 'core:StatusState', 'type': 3, 'value': 'available'},
    {'name': 'core:DiscreteRSSILevelState', 'type': 3, 'value': 'good'},
    {'name': 'core:RSSILevelState', 'type': 2, 'value': 96.0},
    {'name': 'io:RateManagementState', 'type': 3, 'value': '?'},
    {'name': 'io:OperatingModeCapabilitiesState',
     'type': 11,
     'value': {'relaunch': 1,
      'absence': 1,
      'rateManagement': 0,
      'energyDemandStatus': 1}},
    {'name': 'core:OperatingModeState',
     'type': 11,
     'value': {'relaunch': 'off', 'absence': 'off'}},
    {'name': 'io:DHWModeState', 'type': 3, 'value': 'manualEcoActive'},
    {'name': 'core:TemperatureState', 'type': 2, 'value': 50.0},
    {'name': 'core:TargetTemperatureState', 'type': 2, 'value': 50.0},
    {'name': 'core:BoostModeDurationState', 'type': 1, 'value': 0},
    {'name': 'io:AwayModeDurationState', 'type': 3, 'value': '0'},
    {'name': 'core:ManufacturerNameState', 'type': 3, 'value': 'Atlantic'},
    {'name': 'io:DHWCapacityState', 'type': 1, 'value': 200}
                  ]
        """


class ClimateController(BaseDevice):
    def __init__(self, url, name):
        super().__init__(url, name)
        self.state = None

        self.is_on = True

        self.temperature = None
        self.target_temperature = None
        self.min_temp = 7.0
        self.eco_temp = 17.0
        self.comfort_temp = 19.0

        self.battery_state = None

        self.preset = None
        self.preset_mode = None

        self.to_update = None

    def register_update_notification(self, function):
        self.to_update = function

    def set_mode(self, mode):
        return self.url, generate_command("setActiveMode", mode)

    def set_auto_mode(self):
        return self.set_mode("auto")

    def set_manu_mode(self):
        return self.set_mode("manu")

    def set_operating_mode(self, mode):
        return self.url, generate_command("setOperatingMode", mode)

    def set_cooling_mode(self):
        return self.set_operating_mode("cooling")

    def set_heating_mode(self):
        return self.set_operating_mode("heating")

    def set_comfort_temp(self, temperature):
        return self.url, generate_command("setComfortTemperature", temperature)

    def set_eco_temp(self, temperature):
        return self.url, generate_command("setEcoTemperature", temperature)

    def set_manu_temp_mode(self, mode):
        assert mode in ['comfort', 'eco', 'free', 'secured']
        return self.url, generate_command("setManuAndSetPointModes", mode)

    def load_state(self, raw_state):
        for state in raw_state['states']:
            name = state['name']
            value = state['value']
            if name == 'core:OnOffState':
                self.is_on = value == 'on'

            elif name == 'ovp:HeatingTemperatureInterfaceSetPointModeState':
                self.preset = value

            elif name == 'ovp:HeatingTemperatureInterfaceActiveModeState':
                self.preset_mode = value

            elif name == 'ovp:HeatingTemperatureInterfaceOperatingModeState':
                self.state = value

            elif name == 'core:TargetTemperatureState':
                self.target_temperature = value

            elif name == 'core:SecuredPositionTemperatureState':
                self.min_temp = value

            elif name == 'core:EcoRoomTemperatureState':
                self.eco_temp = value

            elif name == 'core:ComfortRoomTemperatureState':
                self.comfort_temp = value

            elif name == 'core:BatteryState':
                self.battery_state = value

            # thermostat
            elif name == "core:TemperatureState":
                self.temperature = value
