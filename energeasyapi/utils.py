from typing import Dict

from energeasyapi.devices import Shutter, WaterHeater, BaseDevice, ClimateController

equipment_type_class = {
    "io:RollerShutterGenericIOComponent": Shutter,
    "io:AtlanticDomesticHotWaterProductionV2_AEX_IOComponent": WaterHeater,
    "io:DHWCumulatedElectricalEnergyConsumptionIOSystemDeviceSensor": None,
    "ovp:SomfyHeatingTemperatureInterfaceOVPComponent": ClimateController,
    "internal:PodV2Component": None,  # EnergeasyBox
}


class DevicesContainer(object):
    devices: Dict[str, BaseDevice]

    def __init__(self):
        self.devices = {}

    def add(self, eqp_raw_data: dict):
        url = eqp_raw_data['deviceURL']

        if url in self.devices:
            # Refresh state
            self.devices[url].load_state(eqp_raw_data)
            return

        # find device type and parse data
        name = eqp_raw_data["label"]
        device_type = eqp_raw_data["controllableName"]
        device_class = equipment_type_class.get(device_type, None)
        if not device_class:
            return

        device: BaseDevice = device_class(url, name)
        device.load_state(eqp_raw_data)
        self.devices[url] = device

    def list_devices(self):
        return self.devices.values()
