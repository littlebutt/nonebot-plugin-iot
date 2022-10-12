import nonebot
from nonebot.adapters.onebot.v11 import Adapter

from iot.core import Iot
from iot.devices import raspberry_pi

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(Adapter)
config = driver.config
Iot.start("RaspberryPi")

if __name__ == "__main__":
    nonebot.run()