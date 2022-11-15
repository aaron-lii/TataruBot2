# -*- coding: utf-8 -*-
"""
自定义回复
"""

from nonebot import on_regex
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event


this_command = "闭嘴。|烦。"
auto_response = on_regex(this_command, priority=5)


# async def precious_help():
#     return this_command + "：帮你选藏宝洞的门"


async def response_detail(word):
    return "不许" + word[:-1] + "！"


@auto_response.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args in this_command:
        ans = await response_detail(args)
        await auto_response.finish(ans)
    else:
        return
