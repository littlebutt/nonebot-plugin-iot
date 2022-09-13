from typing import Dict, Optional, List, Callable

from dotenv import load_dotenv
from fastapi import Response
from pydantic import BaseModel
from nonebot import get_asgi, logger, get_bot
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import Message
import os
from fastapi import FastAPI

from plugins.iot.device import IotDevice, IotDeviceFactory

class AliGenieRequestData(BaseModel):
    userOpenId: Optional[str]
    deviceOpenId: Optional[str]
    city: Optional[str]
    screenStatus: Optional[str]
    deviceUnionIds: Optional[str]
    userUnionIds: Optional[str]
    ...


class AliGenieSlotEntity(BaseModel):
    intentParameterId: int
    intentParameterName: str
    originalValue: str
    standardValue: str
    liveTime: int
    slotNorm: Optional[str]
    createTimeStamp: int
    fromContext: Optional[bool]
    score: Optional[float]
    slotSource: Optional[str]
    ...


class AliGenieSkillSession(BaseModel):
    skillSessionId: Optional[str]
    newSession: Optional[bool]
    attributes: Optional[Dict]
    ...


class AliGenieRequest(BaseModel):
    sessionId: str
    utterance: str
    token: Optional[str]
    requestData: Optional[AliGenieRequestData]
    botId: int
    domainId: int
    skillId: int
    skillName: str
    intentId: int
    intentName: str
    slotEntities: Optional[List[AliGenieSlotEntity]]
    selectIndexList: Optional[List[int]]
    confirmStatus: Optional[str]
    device: Optional[Dict]
    requestId: str
    skillSession: AliGenieSkillSession
    conversationRecords: Optional[List]
    skillNluInfo: Optional[Dict]
    ...


class AliGenieAskInfo(BaseModel):
    parameterName: str
    intentId: str


class AliGenieReturnValue(BaseModel):
    reply: Optional[str]
    resultType: str
    executeCode: str
    askedInfos: Optional[List[AliGenieAskInfo]]


class AliGenieResponse(BaseModel):
    returnCode: str = '0'
    returnErrorSolution: Optional[str]
    returnMessage: Optional[str]
    returnValue: AliGenieReturnValue


@IotDeviceFactory.set_device
class AliGenie(IotDevice):
    """
    天猫精灵设备：
    目前实现的功能有语音发送私聊消息和群消息，只支持FastApi驱动器
    """

    @property
    def name(self) -> str:
        return "AliGenie"

    def rigister(self) -> None:
        """
        注册天猫精灵握手句柄和内置语音发送消息句柄
        :return: None
        """
        config = self.load_config()
        asgi = get_asgi()
        if not isinstance(asgi, FastAPI):
            raise NotImplementedError("Only FastAPI support")

        @asgi.get(config['authentication_path'])
        async def _():
            logger.info("Authentication from AliGenie")
            return Response(content=config["authentication_response"], media_type='text/plain')

        @asgi.post('/', response_model=AliGenieResponse)
        async def _(request: AliGenieRequest) -> AliGenieResponse:
            logger.info(f"Request from AliGenie: request = {request.json()}")
            if request.intentName == 'dialog':
                intent_id = request.intentId
                logger.info(f"Senario dialog hit: intentId = {intent_id}")
                target = None
                content = None
                for slot_entity in request.slotEntities:
                    if slot_entity.intentParameterName == 'target':
                        target = slot_entity.standardValue
                        logger.info(f"Field target hit: target = {target}")
                    if slot_entity.intentParameterName == 'content':
                        content = slot_entity.standardValue
                        logger.info(f"Field content hit: content = {content}")
                if target is None:
                    ask_info = AliGenieAskInfo(parameterName='target', intentId=intent_id)
                    return_value = AliGenieReturnValue(reply="请问要发送给谁呢", executeCode='SUCCESS',
                                                       resultType='ASK_INF', askedInfos=[ask_info])
                    response = AliGenieResponse(returnValue=return_value)
                    logger.warning(f"Field target miss")
                    return response
                if content is None:
                    ask_info = AliGenieAskInfo(parameterName='content', intentId=intent_id)
                    return_value = AliGenieReturnValue(reply="请问要发送什么内容呢", executeCode='SUCCESS',
                                                       resultType='ASK_INF', askedInfos=[ask_info])
                    response = AliGenieResponse(returnValue=return_value)
                    logger.warning(f"Field content miss")
                    return response
                bot = get_bot()
                await self.send(bot, target, content)
                logger.info(f"Message send")
                return_value = AliGenieReturnValue(reply="好的，已发送命令", resultType='RESULT',
                                                   executeCode='SUCCESS')
                response = AliGenieResponse(returnValue=return_value)
                return response

    @staticmethod
    def custom_api(func: Callable[[AliGenieRequest], AliGenieResponse]) -> None:
        """
        自定义API句柄，由天猫精灵平台触发后响应
        :param func: 需要处理天猫精灵的Request的方法
        :return: None
        """
        asgi = get_asgi()
        asgi.post(func, path='/')

    async def send(self, bot: Bot, target: str, content: str) -> bool:
        friend_list = await bot.get_friend_list()
        for friend in friend_list:
            if friend['nickname'] == target:
                await bot.send_private_msg(user_id=int(friend['user_id']), message=Message(content))
                return True
        group_list = await bot.get_group_list()
        for group in group_list:
            if group['group_name'] == target:
                await bot.send_group_msg(group_id=group['group_id'], message=Message(content))
                return True
        logger.error(f"Fail to send message: target={target}, content={content}")
        return False

    def load_config(self) -> Dict[str, str]:
        load_dotenv()
        iot_device_config = dict()
        iot_device_config['version'] = os.environ.get('ALI_GENIE_VERSION')
        iot_device_config['authentication_path'] = os.environ.get('ALI_GENIE_AUTHENTICATION_PATH')
        iot_device_config['authentication_response'] = os.environ.get('ALI_GENIE_AUTHENTICATION_RESPONSE')
        if iot_device_config['authentication_path'] is None or iot_device_config['authentication_response'] is None:
            raise KeyError("Crucial info missing, please check .env files")
        return iot_device_config