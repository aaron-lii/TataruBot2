# -*- coding:utf-8 -*-
"""
看空房子
"""

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import time

from tatarubot2.plugins.utils import aiohttp_get, default_command_start

this_command = "房子 "
house = on_command(this_command, priority=5)



url = "https://house.ffxiv.cyou/api/sales?server={}&ts={}"

server_dict = {"红玉海": 1167,
               "神意之地": 1081,
               "拉诺西亚": 1042,
               "幻影群岛": 1044,
               "萌芽池": 1060,
               "宇宙和音": 1173,
               "沃仙曦染": 1174,
               "晨曦王座": 1175,
               "白银乡": 1172,
               "白金幻象": 1076,
               "神拳痕": 1171,
               "潮风亭": 1170,
               "旅人栈桥": 1113,
               "拂晓之间": 1121,
               "龙巢神殿": 1166,
               "梦羽宝境": 1176,
               "紫水栈桥": 1043,
               "延夏": 1169,
               "静语庄园": 1106,
               "摩杜纳": 1045,
               "海猫茶屋": 1177,
               "柔风海湾": 1178,
               "琥珀原": 1179,
               "水晶塔": 1192,
               "银泪湖": 1183,
               "太阳海岸": 1180,
               "伊修加德": 1186,
               "红茶川": 1201}

area_list = ["海都", "森都", "沙都", "白银", "雪都"]
size_list = ["S", "M", "L"]


async def house_help():
    return default_command_start + this_command + "服务器名 主城名 房子大小：查询空房。主城名为：森都、海都、沙都、白银、雪都。房子大小为：S、M、L"


async def run(args):
    if args[0] not in server_dict:
        server_list = []
        for key, val in server_dict.items():
            server_list.append(key)
        await house.finish("检查一下服务器名称呀：\n" + str(server_list))

    if args[1] not in area_list:
        await house.finish("检查一下主城名称呀：\n" + str(area_list))
    if args[2].upper() not in size_list:
        await house.finish("检查一下房屋大小呀：\n" + str(size_list))
    # r = requests.get(url.format(str(server_dict[args[0]]), str(int(time.time()))), timeout=time_out, headers=get_headers()).json()
    r = await aiohttp_get(url.format(str(server_dict[args[0]]), str(int(time.time()))))

    result_list = []
    area_i = area_list.index(args[1])
    size_i = size_list.index(args[2].upper())

    for item in r:
        if item["Area"] == area_i and item["Size"] == size_i:
            result_list.append(area_list[item["Area"]] + str(item["Slot"] + 1) + "区" +
                               str(item["ID"]) + "号，" + size_list[item["Size"]] +
                               "，价格：" + str(item["Price"] // 10000) + "万")

    if not result_list:
        await house.finish("没空房子了")
        return
    else:
        for i in range(len(result_list) // 20 + 1):
            await house.send("\n".join(result_list[i * 20: i * 20 + 20]))
            time.sleep(0.5)

        await house.finish()



@house.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(" ")
    if len(args) < 4:
        await house.finish("看空房格式： " + default_command_start + this_command +
                           "服务器名 主城名 房子大小。主城名为：森都、海都、沙都、白银、雪都。房子大小为：S、M、L")
    args = args[1:]
    if args:
        state["item_info"] = args  # 如果用户发送了参数则直接赋值


@house.got("item_info")
async def handle_house(bot: Bot, event: Event, state: T_State):
    await run(state["item_info"])