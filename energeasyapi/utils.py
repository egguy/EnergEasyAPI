from typing import Dict

from energeasyapi.devices import Shutter, WaterHeater, BaseDevice, ClimateController

equipment_type_class = {
    "io:RollerShutterGenericIOComponent": Shutter,
    "io:AtlanticDomesticHotWaterProductionV2_AEX_IOComponent": WaterHeater,
    "io:DHWCumulatedElectricalEnergyConsumptionIOSystemDeviceSensor": None,
    "ovp:SomfyHeatingTemperatureInterfaceOVPComponent": ClimateController,
    "ovp:HeatingTemperatureInterfaceTemperatureSensor": ClimateController,
    "internal:PodV2Component": None,  # EnergeasyBox
}


class DevicesContainer(object):
    devices: Dict[str, BaseDevice]

    def __init__(self):
        self.devices = {}

    def add(self, eqp_raw_data: dict):
        # Normalize URL Help with sub device like a climate control + thermostat
        base_url = eqp_raw_data['deviceURL']
        urls = eqp_raw_data['deviceURL'].split("#")
        url = urls[0]

        if url in self.devices:
            # Refresh state
            self.devices[url].load_state(eqp_raw_data)
            return
        else:
            if len(urls) == 2 and urls[1] != "1":
                # prevent adding io://...../....#2 before #1
                return

        # find device type and parse data
        name = eqp_raw_data["label"]
        device_type = eqp_raw_data["controllableName"]
        device_class = equipment_type_class.get(device_type, None)
        if not device_class:
            return

        device: BaseDevice = device_class(base_url, name)
        device.load_state(eqp_raw_data)
        self.devices[url] = device

    def list_devices(self):
        return self.devices.values()
