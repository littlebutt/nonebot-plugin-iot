from .device import IotDeviceFactory


class Iot:

    @staticmethod
    def start(device: str):
        IotDeviceFactory.get_device(device).rigister()
