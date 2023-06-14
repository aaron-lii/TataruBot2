# -*- coding: utf-8 -*-
import asyncio
import re

from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from nonebot import on_command
from nonebot.adapters import Message, Event
from nonebot.params import CommandArg
from nonebot.rule import to_me

from tatarubot2.plugins.utils import get_conf_dict

this_command = "bing"
bing_ai = on_command(this_command, rule=to_me(), priority=5)


conf_dict = get_conf_dict()
use_proxy = conf_dict["proxy"]["enable"]
proxy_url = conf_dict["proxy"]["url"]

locked = False
bot = asyncio.run(Chatbot.create(proxy=proxy_url if use_proxy else None))


async def chat_run(msg: str):
    # nonebot在一个响应器未执行完时会ignore重复的消息，这个锁是为了保险
    global locked
    if locked:
        return "我正在忙，请稍后再试"
    locked = True
    try:
        # bot = await Chatbot.create(proxy=proxy_url if use_proxy else None)
        response = await bot.ask(prompt=msg, conversation_style=ConversationStyle.precise, locale="zh-cn",
                                 simplify_response=False)
        # print(json.dumps(response, indent=2))
        res = msg
        for s in response['item']['messages']:
            if 'messageType' not in s:
                res = s['text']
        # await bot.close()
        return re.sub(r'\[[^]]*]', "", res)
    finally:
        locked = False


@bing_ai.handle()
async def handle_first_receive(event: Event, args: Message = CommandArg()):
    chat_msg = args.extract_plain_text().strip()
    # print(chat_msg)
    if not chat_msg:
        await bing_ai.finish("你想和我聊天吗？")

    return_str = await chat_run(chat_msg)
    await bing_ai.finish(return_str)
