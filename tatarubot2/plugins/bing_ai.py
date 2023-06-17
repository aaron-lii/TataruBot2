# -*- coding: utf-8 -*-
import asyncio
import re

from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from nonebot import on_command, logger
from nonebot.adapters import Message, Event
from nonebot.params import CommandArg

from tatarubot2.plugins.utils import get_conf_dict

this_command = "bing"
bing_ai = on_command(this_command, priority=5)


async def bing_help():
    return this_command + " 聊天内容：和我聊天吧，会记忆聊天上下文\n" + \
        this_command + " 重置/reset：重置聊天内容，忘记之前的聊天"


conf_dict = get_conf_dict()
use_proxy = conf_dict["proxy"]["enable"]
proxy_url = conf_dict["proxy"]["url"]

locked = False
bot = asyncio.run(Chatbot.create(proxy=proxy_url if use_proxy else None))


async def chat(msg: str):
    # nonebot在一个响应器未执行完时会ignore重复的消息，这个锁是为了保险
    global locked, bot
    if locked:
        return "我正在忙，请稍后再试"
    locked = True
    try:
        response = await bot.ask(prompt=msg, conversation_style=ConversationStyle.precise, locale="zh-cn",
                                 simplify_response=True)
        # print(json.dumps(response, indent=2))
        res = response["text"]
        # await bot.close()
        return re.sub(r'\[[^]]*]', "", res)
    finally:
        locked = False


async def reset_bot():
    global bot
    await bot.reset()
    return "我已经忘记了所有的事情"


@bing_ai.handle()
async def handle_first_receive(event: Event, args: Message = CommandArg()):
    chat_msg = args.extract_plain_text().strip()

    if not chat_msg:
        await bing_ai.finish("你想和我聊天吗？")
    try:
        if chat_msg == "重置" or chat_msg == "reset":
            return_str = await reset_bot()
        else:
            return_str = await chat(chat_msg)
    except Exception as e:
        logger.error(e)
        return_str = "我好像出了点问题，等我修好再聊吧"
    await bing_ai.finish(return_str)
