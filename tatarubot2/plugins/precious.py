# -*- coding: utf-8 -*-
"""
挖宝
"""

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import random


this_command = "选门"
precious = on_command(this_command, priority=5)


async def precious_help():
    return this_command + "：帮你选藏宝洞的门"


async def random_left_right():
    result = []
    for _ in range(5):
        if random.random() > 0.5:
            result.append("右")
        else:
            result.append("左")
    return " ".join(result)


@precious.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args == this_command:
        left_right_str = await random_left_right()
        await precious.finish("塔塔露在藏宝洞中横冲直撞！\n" + left_right_str)
    else:
        return
