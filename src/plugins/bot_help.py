# -*- coding: utf-8 -*-

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

from src.plugins.item import item_help
from src.plugins.lottery import lottery_help
from src.plugins.market import market_help
from src.plugins.nuannuan import nuannuan_help
from src.plugins.precious import precious_help
from src.plugins.ff_weibo import ff_weibo_help
from src.plugins.item_new import item_new_help
from src.plugins.market_new import market_new_help
from src.plugins.house import house_help
from src.plugins.logs_dps import logs_dps_help


this_command = "帮帮忙"
bot_help = on_command(this_command, rule=to_me(), priority=5)


async def create_help():
    return_list = []
    return_list.append(await nuannuan_help())
    return_list.append(await precious_help())
    return_list.append(await lottery_help())
    return_list.append(await ff_weibo_help())
    return_list.append(await item_help())
    return_list.append(await item_new_help())
    return_list.append(await market_help())
    return_list.append(await market_new_help())
    return_list.append(await house_help())
    return_list.append(await logs_dps_help())
    return "【塔塔露现有的功能】\n\n" + "\n\n".join(return_list)


@bot_help.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args == this_command:
        return_str = await create_help()
        await bot_help.finish(return_str)
    else:
        return
