# -*- coding: utf-8 -*-
"""
查物价 本地目录
"""

import os
import json

from tatarubot2.plugins.market import *


this_command = "新价格 "
market_new = on_command(this_command, priority=5)


# 加载字典
item_dict = {}
this_dir = os.path.split(os.path.realpath(__file__))[0]
json_path = os.path.join(this_dir, "../data/item_dict.json")
with open(json_path, "r", encoding="utf-8") as f_r:
    item_dict = json.load(f_r)


async def market_new_help():
    return default_command_start + this_command + "大区 物品名：查物价异常时可以尝试这个版本"


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
    j = await aiohttp_get(url, proxy=use_proxy)
    # if r.status != 200:
    #     if r.status == 404:
    #         msg = "请确认所查询物品可交易且不可在NPC处购买\n"
    #     msg += "Error of HTTP request (code {}):\n{}".format(r.status_code, r.text)
    #     return msg
    # j = await r.json()
    msg = "{} 的 {}{} 数据如下：\n".format(server_name, new_item_name, "(HQ)" if hq else "")
    listing_cnt = 0
    for listing in j["listings"]:
        if hq and not listing["hq"]:
            continue
        retainer_name = listing["retainerName"]
        if "dcName" in j:
            retainer_name += "({})".format(listing["worldName"])
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
        await market.finish("查物价格式： " + default_command_start + this_command + " 大区 物品名\n不写大区默认豆豆柴")
    args = args[1]
    if args:
        state["market_info"] = args  # 如果用户发送了参数则直接赋值


@market_new.got("market_info")
async def handle_item(bot: Bot, event: Event, state: T_State):
    item_info = state["market_info"].split(" ", 1)
    # 命令中没有指定服务器则从配置文件中读取
    if len(item_info) == 1:
        server_name = default_dc
        item_name = item_info[0]
    else:
        server_name = item_info[0]
        item_name = item_info[1]

    if not server_name.strip():
        # 命令和配置文件中都没有指定服务器则默认狗区
        server_name = "豆豆柴"
    if server_name in supported_dc or server_name in supported_server:
        pass
    elif server_name in server_alias:
        # 别名, 如 "狗"->"豆豆柴"
        server_name = server_alias[server_name]
    else:
        await market.finish('未知的大区/服务器:"{}"'.format(server_name))

    hq = "hq" in item_name or "HQ" in item_name
    if hq:
        item_name = item_name.replace("hq", "", 1)
        item_name = item_name.replace("HQ", "", 1)
    item_name = handle_item_name_abbr(item_name)

    try:
        msg = await get_market_data(server_name, item_name, hq)
        logger.info(msg)
        if use_pic:
            img_bytes = str2img(msg)
            msg = Message([MessageSegment.image(img_bytes)])
        else:
            msg = get_emoji() + msg + get_emoji()
    except Exception as e:
        print(e)
        msg = "可能是物价网站暂时访问不了"
        time.sleep(0.5)

    await market_new.finish(msg)


