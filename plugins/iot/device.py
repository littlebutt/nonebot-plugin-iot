import abc
from typing import Dict, ClassVar


class IotDevice(abc.ABC, metaclass=type):

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def rigister(self) -> None:
        raise NotImplementedError


class IotDeviceFactory:
    __iot_device_map: Dict[str, IotDevice] = dict()

    @classmethod
    def set_device(cls, target_cls: ClassVar[IotDevice]):
        cls.__iot_device_map[target_cls.__name__] = target_cls()

    @classmethod
    def get_device(cls, target_cls: str):
        if target_cls in cls.__iot_device_map:
            return cls.__iot_device_map[target_cls]
        else:
            raise KeyError("cannot find target IoT device")