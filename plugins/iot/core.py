from typing import List

from plugins.iot.device import IotDevice, IotDeviceFactory


class Iot:

    @staticmethod
    def start(device: str):
        IotDeviceFactory.get_device(device).rigister()
