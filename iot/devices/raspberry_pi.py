import asyncio
import json
import os
import threading
from typing import Any, Dict

from dotenv import load_dotenv
from paho.mqtt import publish, subscribe
from nonebot import logger, get_bot, on_message, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.rule import to_me
from paho.mqtt.client import MQTTMessage

from iot.device import IotDevice, IotDeviceFactory


@IotDeviceFactory.set_device
class RaspberryPi(IotDevice):
    @property
    def name(self) -> str:
        return 'RaspberryPi'

    def rigister(self) -> None:
        config = self.load_config()
        emit_message = on_message(rule=to_me())

        @emit_message.handle()
        async def _(event: GroupMessageEvent):
            logger.info("Message from " + str(event.user_id))
            message = event.message.extract_plain_text()
            topic = 'self/qq'
            publish.single(topic=topic,
                           payload=json.dumps({
                               "topic": topic,
                               "device": "qq",
                               "verbose": "false",
                               "message": event.sender.nickname + "对你说" + message
                           }),
                           hostname=config['rpi_hostname'] if 'rpi_hostname' in config else '127.0.0.1',
                           port=int(config['rpi_port']) if 'rpi_port' in config else 1883)
            logger.info("Message from " + str(event.user_id) + " sent to MQTT Server")

        def __callback(client: Any, userdata: Any, mqtt_message: "MQTTMessage") -> None:
            """

            :param client: MQTT Client
            :param userdata: UserData
            :param mqtt_message: MQTTMessage, including topic and payload
            :return: None
            """
            logger.info(f"MQTT message received: topic {mqtt_message.topic} payload: {str(mqtt_message.payload)}")
            message_obj = json.loads(mqtt_message.payload)
            target = message_obj['target']
            content = message_obj['content']
            bot = get_bot()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            task = asyncio.ensure_future(bot.get_friend_list())
            asyncio.get_event_loop().run_until_complete(task)
            friend_list = task.result()
            for friend in friend_list:
                if friend['nickname'] == target:
                    bot.send_private_msg(user_id=int(friend['user_id']), message=Message(content))
                    logger.info(f"Message from topic {mqtt_message.topic} sent to QQ friend {target}")
                    return
            task = asyncio.ensure_future(bot.get_group_list())
            asyncio.get_event_loop().run_until_complete(task)
            group_list = task.result()
            for group in group_list:
                if group['group_name'] == target:
                    bot.send_group_msg(group_id=target, message=Message(content))
                    logger.info(f"Message from topic {mqtt_message.topic} sent to QQ group {target}")
                    return
            logger.warning("Fail to send message to QQ target " + target)

        def __thread():
            subscribe.callback(topics="qq/nonebot", callback=__callback,
                               hostname=config['rpi_hostname'] if 'rpi_hostname' in config else '127.0.0.1',
                               port=int(config['rpi_port']) if 'rpi_port' in config else 1883)

        message_thread = threading.Thread(target=__thread)
        message_thread.start()

    def load_config(self) -> Dict[str, str]:
        load_dotenv()
        return dict(os.environ)

