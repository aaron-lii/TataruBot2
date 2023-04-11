# -*- coding: utf-8 -*-
"""
查物价
"""

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

# import requests
import aiohttp
from difflib import SequenceMatcher
import re
import time
import random

this_command = "价格 "
market = on_command(this_command, priority=5)

# 超时时间
# time_out = 60
# 重试次数
# retry_num = 20


# 减少requests错误
def get_headers():
    agent = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 '
             'Safari/537.36 QIHU 360SE',
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
             'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 '
             'Safari/537.36']

    headers = {'Connection': 'close', 'User-Agent': agent[random.randint(0, len(agent) - 1)]}
    return headers

timeout = aiohttp.ClientTimeout(total=60)
session = aiohttp.ClientSession(timeout=timeout, headers=get_headers())


async def market_help():
    return this_command + "大区 物品名：查询板子物价，大区不写默认豆豆柴"


def localize_world_name(world_name):
    world_dict = {
        "HongYuHai": "红玉海",
        "ShenYiZhiDi": "神意之地",
        "LaNuoXiYa": "拉诺西亚",
        "HuanYingQunDao": "幻影群岛",
        "MengYaChi": "萌芽池",
        "YuZhouHeYin": "宇宙和音",
        "WoXianXiRan": "沃仙曦染",
        "ChenXiWangZuo": "晨曦王座",
        "BaiYinXiang": "白银乡",
        "BaiJinHuanXiang": "白金幻象",
        "ShenQuanHen": "神拳痕",
        "ChaoFengTing": "潮风亭",
        "LvRenZhanQiao": "旅人栈桥",
        "FuXiaoZhiJian": "拂晓之间",
        "Longchaoshendian": "龙巢神殿",
        "MengYuBaoJing": "梦羽宝境",
        "ZiShuiZhanQiao": "紫水栈桥",
        "YanXia": "延夏",
        "JingYuZhuangYuan": "静语庄园",
        "MoDuNa": "摩杜纳",
        "HaiMaoChaWu": "海猫茶屋",
        "RouFengHaiWan": "柔风海湾",
        "HuPoYuan": "琥珀原",
        "ShuiJingTa2": "水晶塔",
        "YinLeiHu2": "银泪湖",
        "TaiYangHaiAn2": "太阳海岸",
        "YiXiuJiaDe2": "伊修加德",
        "HongChaChuan2": "红茶川",
    }
    for (k, v) in world_dict.items():
        pattern = re.compile(k, re.IGNORECASE)
        world_name = pattern.sub(v, world_name)
    return world_name


async def get_item_id(item_name, name_lang=""):
    url = "https://xivapi.com/search?indexes=Item&string=" + item_name
    if name_lang:
        url = url + "&language=" + name_lang
    if name_lang == "cn":
        url = (
            "https://cafemaker.wakingsands.com/search?indexes=Item&string=" + item_name
        )
    # r = requests.get(url, timeout=time_out, headers=get_headers())
    r = await session.get(url)
    j = await r.json()
    if len(j["Results"]) > 0:
        result = max(j["Results"], key=lambda x: SequenceMatcher(None, x["Name"], item_name).ratio())
        return result["Name"], result["ID"]
    return "", -1


async def get_market_data(server_name, item_name, hq=False):
    new_item_name, item_id = await get_item_id(item_name, "cn")
    if item_id < 0:
        item_name = item_name.replace("_", " ")
        name_lang = ""
        for lang in ["ja", "fr", "de"]:
            if item_name.endswith("|{}".format(lang)):
                item_name = item_name.replace("|{}".format(lang), "")
                name_lang = lang
                break
        new_item_name, item_id = await get_item_id(item_name, name_lang)
        if item_id < 0:
            msg = '所查询物品"{}"不存在'.format(item_name)
            return msg
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


def handle_item_name_abbr(item_name):
    if item_name.startswith("第二期重建用的") and item_name.endswith("(检)"):
        item_name = item_name.replace("(", "（").replace(")", "）")
    if item_name.startswith("第二期重建用的") and not item_name.endswith("（检）"):
        item_name = item_name + "（检）"
    if item_name.upper() == "G12":
        item_name = "陈旧的缠尾蛟革地图"
    if item_name.upper() == "G11":
        item_name = "陈旧的绿飘龙革地图"
    if item_name.upper() == "G10":
        item_name = "陈旧的瞪羚革地图"
    if item_name.upper() == "G9":
        item_name = "陈旧的迦迦纳怪鸟革地图"
    if item_name.upper() == "G8":
        item_name = "陈旧的巨龙革地图图"
    if item_name.upper() == "G7":
        item_name = "陈旧的飞龙革地图"
    return item_name


@market.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(" ", 1)
    if len(args) < 2:
        await market.finish("查物价格式： " + this_command + " 大区 物品名\n不写大区默认豆豆柴")
    args = args[1]
    if args:
        state["market_info"] = args  # 如果用户发送了参数则直接赋值


@market.got("market_info")
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

    await market.finish(msg)


