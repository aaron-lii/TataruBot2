# -*- coding: utf-8 -*-
"""
简单的例子
"""

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

from tatarubot2.plugins.utils import default_command_start

this_command = "天气 "
weather = on_command(this_command, rule=to_me(), priority=5)


@weather.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if len(args) < 2:
        await weather.finish("查天气格式： " + default_command_start + this_command + " 城市")
    args = args.split(" ")[1]
    if args:
        state["city"] = args  # 如果用户发送了参数则直接赋值


@weather.got("city", prompt="你想查询哪个城市的天气呢？")
async def handle_city(bot: Bot, event: Event, state: T_State):
    city = state["city"]
    # if city not in ["上海", "北京"]:
    #     await weather.reject("你想查询的城市暂不支持，请重新输入！")
    city_weather = await get_weather(city)
    await weather.finish(city_weather)


async def get_weather(city: str):
    # return f"111"
    return f"{city}的天气是... 黄 道 陨 石！"
