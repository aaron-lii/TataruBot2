# -*- coding: utf-8 -*-
"""
查物价 本地目录
"""

import os

from tatarubot2.plugins.market import *


this_command = "新价格 "
market_new = on_command(this_command, priority=5)


# 加载字典
item_dict = {}
this_dir = os.path.split(os.path.realpath(__file__))[0]
json_path = os.path.join(this_dir, "../data/item_dict.json")
with open(json_path, "r", encoding="utf-8") as f_r:
    for line in f_r.readlines():
        item_dict = eval(line)


async def market_new_help():
    return this_command + "大区 物品名：查物价异常时可以尝试这个版本"


async def get_market_data(server_name, item_name, hq=False):
    # new_item_name, item_id = get_item_id(item_name, "cn")
    if item_name not in item_dict:
        new_item_name, item_id = "", -1
    else:
        new_item_name, item_id = item_name, int(item_dict[item_name])

    msg = ""
    if item_id < 0:
        msg = '所查询物品"{}"不存在'.format(item_name)
        return msg

    # if item_id < 0:
    #     item_name = item_name.replace("_", " ")
    #     name_lang = ""
    #     for lang in ["ja", "fr", "de"]:
    #         if item_name.endswith("|{}".format(lang)):
    #             item_name = item_name.replace("|{}".format(lang), "")
    #             name_lang = lang
    #             break
    #     new_item_name, item_id = get_item_id(item_name, name_lang)
    #     if item_id < 0:
    #         msg = '所查询物品"{}"不存在'.format(item_name)
    #         return msg
    url = "https://universalis.app/api/{}/{}".format(server_name, item_id)
    print("market url:{}".format(url))
    # r = requests.get(url, timeout=time_out, headers=get_headers())
    r = await session.get(url)
    if r.status != 200:
        if r.status == 404:
            msg = "请确认所查询物品可交易且不可在NPC处购买\n"
        msg += "Error of HTTP request (code {}):\n{}".format(r.status_code, r.text)
        return msg
    j = await r.json()
    msg = "{} 的 {}{} 数据如下：\n".format(server_name, new_item_name, "(HQ)" if hq else "")
    listing_cnt = 0
    for listing in j["listings"]:
        if hq and not listing["hq"]:
            continue
        retainer_name = listing["retainerName"]
        if "dcName" in j:
            retainer_name += "({})".format(localize_world_name(listing["worldName"]))
        msg += "{:,}x{} = {:,} {} {}\n".format(
            listing["pricePerUnit"],
            listing["quantity"],
            listing["total"],
            "HQ" if listing["hq"] else "  ",
            retainer_name,
        )
        listing_cnt += 1
        if listing_cnt >= 10:
            break
    TIMEFORMAT_YMDHMS = "%Y-%m-%d %H:%M:%S"
    last_upload_time = time.strftime(
        TIMEFORMAT_YMDHMS, time.localtime(j["lastUploadTime"] / 1000)
    )
    msg += "更新时间:{}".format(last_upload_time)
    if listing_cnt == 0:
        msg = "未查询到数据，咋回事呢？"
    return msg


@market_new.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(" ", 1)
    if len(args) < 2:
        await market.finish("查物价格式： " + this_command + " 大区 物品名\n不写大区默认豆豆柴")
    args = args[1]
    if args:
        state["market_info"] = args  # 如果用户发送了参数则直接赋值


@market_new.got("market_info")
async def handle_item(bot: Bot, event: Event, state: T_State):
    item_info = state["market_info"].split(" ", 1)
    # 没有服务器则默认狗区
    if len(item_info) == 1:
        server_name = "豆豆柴"
        item_name = item_info[0]
    else:
        server_name = item_info[0]
        item_name = item_info[1]

    if server_name in ("陆行鸟", "莫古力", "猫小胖", "豆豆柴"):
        pass
    elif server_name == "鸟":
        server_name = "陆行鸟"
    elif server_name == "猪":
        server_name = "莫古力"
    elif server_name == "猫":
        server_name = "猫小胖"
    elif server_name == "狗":
        server_name = "豆豆柴"
    else:
        pass
        # server = Server.objects.filter(name=server_name)
        # if not server.exists():
        #     msg = '找不到服务器"{}"'.format(server_name)
        #     return msg

    hq = "hq" in item_name or "HQ" in item_name
    if hq:
        item_name = item_name.replace("hq", "", 1)
        item_name = item_name.replace("HQ", "", 1)
    item_name = handle_item_name_abbr(item_name)

    msg = "发生甚么事了？"
    # for _ in range(retry_num):
    try:
        msg = await get_market_data(server_name, item_name, hq)
        # break
    except Exception as e:
        # await market.finish(str(e))
        msg = str(e)
        time.sleep(0.5)

    await market_new.finish(msg)


