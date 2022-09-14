import nonebot
from nonebot.adapters.onebot.v11 import Adapter

from iot.core import Iot
from iot.devices import ali_genie

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(Adapter)
config = driver.config
Iot.start("AliGenie")

if __name__ == "__main__":
    nonebot.run()