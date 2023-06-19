# -*- coding: utf-8 -*-
"""
查物品
"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import re
import base64
import json
import logging
import traceback
import time
import os

from tatarubot2.plugins.utils import aiohttp_get, logger, default_command_start

this_command = "物品 "
item = on_command(this_command, priority=5)


async def item_help():
    return default_command_start + this_command + "物品名：查询物品信息"


# 加载字典 用于本地获取物品id
this_dir = os.path.split(os.path.realpath(__file__))[0]
json_path = os.path.join(this_dir, "../data/item_dict.json")
with open(json_path, "r", encoding="utf-8") as f_r:
    item_dict = json.load(f_r)


# GARLAND = "https://ffxiv.cyanclay.xyz"
GARLAND = "https://garlandtools.cn"
FF14WIKI_BASE_URL = "https://ff14.huijiwiki.com"
FF14WIKI_API_URL = "https://cdn.huijiwiki.com/ff14/api.php"
CAFEMAKER = "https://cafemaker.wakingsands.com"
XIVAPI = "https://xivapi.com"

XIV_TAG_REGEX = re.compile(r"<(.*?)>")
GT_CORE_DATA_CN = None
GT_CORE_DATA_GLOBAL = None
NODE_NAME_BY_TYPE = {
    0: "矿脉",
    1: "石场",
    2: "良材",
    3: "草场",
    4: "鱼影",
    5: "鱼影"
}

FISH_SHADOW_SIZE = {
    'S': '小型',
    'M': '中型',
    'L': '大型',
    'Map': '宝藏地图'
}

FISH_SHADOW_SPEED = {
    'Slow': '慢',
    'Average': '中速',
    'Fast': '快',
    'Very Fast': '非常快',
    'V. Fast': '非常快'
}


def craft_garland_url(item_category, item_id, name_lang):
    is_cn = (name_lang == "chs")
    return "{}/db/doc/{}/{}/3/{}.json".format(
        GARLAND if is_cn else "https://garlandtools.org",
        item_category,
        name_lang,
        item_id
    )


def parse_xiv_html(string):
    global XIV_TAG_REGEX

    def handle_tag(tag_match):
        tag = tag_match.group(1)
        return '\n' if tag == "br" else ""

    return XIV_TAG_REGEX.sub(handle_tag, string)


async def gt_core(key: str, lang: str):
    global GT_CORE_DATA_CN, GT_CORE_DATA_GLOBAL
    if lang == "chs":
        if GT_CORE_DATA_CN is None:
            # GT_CORE_DATA_CN = requests.get(craft_garland_url("core", "data", "chs"), timeout=time_out, headers=get_headers()).json()
            GT_CORE_DATA_CN = await aiohttp_get(craft_garland_url("core", "data", "chs"))
            # GT_CORE_DATA_CN = await GT_CORE_DATA_CN.json()
        GT_CORE_DATA = GT_CORE_DATA_CN
    else:
        if GT_CORE_DATA_GLOBAL is None:
            # GT_CORE_DATA_GLOBAL = requests.get(craft_garland_url("core", "data", "en"), timeout=time_out, headers=get_headers()).json()
            GT_CORE_DATA_GLOBAL = await aiohttp_get(craft_garland_url("core", "data", "en"))
            # GT_CORE_DATA_GLOBAL = await GT_CORE_DATA_GLOBAL.json()
        GT_CORE_DATA = GT_CORE_DATA_GLOBAL
    req = GT_CORE_DATA
    for par in key.split('.'):
        req = req[par]
    return req


async def parse_item_garland(item_id, name_lang):
    if name_lang == "cn":
        name_lang = "chs"

    # j = requests.get(craft_garland_url("item", item_id, name_lang), timeout=time_out, headers=get_headers()).json()
    j = await aiohttp_get(craft_garland_url("item", item_id, name_lang))
    # j = await j.json()

    result = []
    # index partials
    partials = {}
    for p in j["partials"] if "partials" in j.keys() else []:
        partials[(p["type"], p["id"])] = p["obj"]

    item = j["item"]
    # start processing
    if "icon" in item.keys():
        image_url = f"{GARLAND}/files/icons/item/{item['icon'] if str(item['icon']).startswith('t/') else 't/' + str(item['icon'])}.png"
        # image = requests.get(image_url, headers=get_headers())
        # print(image_url)
        image = await aiohttp_get(image_url, res_type="bytes")
        # image = await image.read()
        base64_str = base64.b64encode(image).decode("utf-8")
        # result.append(f"[CQ:image,file=base64://{base64_str}]")
        result.append(f"base64://{base64_str}")

    result.append(item["name"])
    result.append(await gt_core(f"item.categoryIndex.{item['category']}.name", name_lang))
    result.append(f"物品等级 {item['ilvl']}")
    if "equip" in item.keys():
        result.append(f"装备等级 {item['elvl']}")

    if "jobCategories" in item.keys():
        result.append(item['jobCategories'])

    if "description" in item.keys():
        result.append(parse_xiv_html(item['description']))

    hasSource = False

    def format_limit_time(times):
        limitTimes = "\n艾欧泽亚时间 "
        for time in times:
            limitTimes += f"{time}时 "
        limitTimes += "开放采集"
        return limitTimes

    if "nodes" in item.keys():
        global NODE_NAME_BY_TYPE
        hasSource = True
        result.append(f"·采集")
        for nodeIndex in item["nodes"]:
            node = partials[("node", str(nodeIndex))]
            result.append("  -- {} {} {} {}{}".format(
                await gt_core(f"locationIndex.{node['z']}.name", name_lang),
                node["n"],
                "{}{}".format(
                    "" if 'lt' not in node.keys() else node['lt'],
                    NODE_NAME_BY_TYPE[int(node['t'])]
                ),
                f"({node['c'][0]}, {node['c'][1]})",
                "" if 'ti' not in node.keys() else format_limit_time(node['ti'])
            ))
        result.append("")

    if "fishingSpots" in item.keys():
        hasSource = True
        result.append(f"·钓鱼")
        for spotIndex in item['fishingSpots']:
            spot = partials[("fishing", str(spotIndex))]
            result.append("  -- {} {} {} {}".format(
                await gt_core(f"locationIndex.{spot['z']}.name", name_lang),
                spot['n'],
                f"{spot['c']} {spot['l']}级",
                "" if 'x' not in spot.keys() else f"({spot['x']}, {spot['y']})"
            ))
        result.append("")

    if "fish" in item.keys():
        result.append(f"·钓法/刺鱼指引")
        for fishGroup in item['fish']['spots']:
            if "spot" in fishGroup.keys():
                result.append(f"  {fishGroup['hookset']} {fishGroup['tug']}")
                if "predator" in fishGroup.keys():
                    result.append("- 需求捕鱼人之识")
                    for predator in fishGroup['predator']:
                        result.append("  - {} *{}".format(
                            partials[("item", str(predator["id"]))]['n'],
                            predator['amount']
                        ))
                if "baits" in fishGroup.keys():
                    result.append("- 可用鱼饵")
                    for baitChains in fishGroup['baits']:
                        chain = ""
                        for bait in baitChains:
                            if not len(chain) == 0:
                                chain += " -> "
                            chain += partials[('item', str(bait))]['n']
                        result.append(f"  - {chain}")
                if "during" in fishGroup.keys():
                    result.append(f"- 限ET {fishGroup['during']['start']}时至{fishGroup['during']['end']}时")
                if "weather" in fishGroup.keys():
                    w = " ".join(fishGroup['weather'])
                    if "transition" in fishGroup.keys():
                        w = w + " -> " + " ".join(fishGroup['transition'])
                    result.append(f"- 限{w}")
            elif "node" in fishGroup.keys():
                result.append(f"- 鱼影大小 {FISH_SHADOW_SIZE[fishGroup['shadow']]}")
                result.append(f"- 鱼影速度 {FISH_SHADOW_SPEED[fishGroup['speed']]}")
                pass
        result.append("")

    if "reducedFrom" in item.keys():
        hasSource = True
        result.append(f"·精选")
        for itemIndex in item["reducedFrom"]:
            result.append("- {}".format(partials[("item", str(itemIndex))]['n']))
        result.append("")

    if "craft" in item.keys():
        hasSource = True
        result.append(f"·制作")
        for craft in item["craft"]:
            result.append("  -- {} {}".format(
                (await gt_core(f"jobs", name_lang))[craft["job"]]["name"],
                f"{craft['lvl']}级"
            ))
            result.append("  材料:")
            for ingredient in craft["ingredients"]:
                if ingredient["id"] < 20:
                    continue
                result.append("   - {} {}个".format(
                    partials[("item", str(ingredient["id"]))]["n"],
                    ingredient["amount"]
                ))
        result.append("")

    if "vendors" in item.keys():
        hasSource = True
        result.append(f"·商店贩售 {item['price']}金币")
        i = 0
        for vendor in item["vendors"]:
            if i > 4:
                result.append(f"等共计{len(item['vendors'])}个商人售卖")
                break
            vendor_partial = partials["npc", str(vendor)]
            result.append("  -- {} {} {}".format(
                vendor_partial["n"],
                await gt_core(f"locationIndex.{vendor_partial['l']}.name", name_lang) if 'l' in vendor_partial.keys() else "",
                f"({vendor_partial['c'][0]}, {vendor_partial['c'][1]})" if 'c' in vendor_partial.keys() else ""
            ))
            i += 1
        pass

    if "tradeCurrency" in item.keys() or "tradeShops" in item.keys():
        hasSource = True
        tradeCurrency = []
        tradeShops = []
        try:
            tradeCurrency = item["tradeCurrency"]
        except KeyError:
            # ignore
            pass
        try:
            tradeShops = item["tradeShops"]
        except KeyError:
            # ignore
            pass
        trades = tradeCurrency + tradeShops
        i = 0
        for trade in trades:
            if i > 4:
                result.append(f"等共计{len(trades)}种购买方式")
                break

            shop_name = trade["shop"]
            result.append("·{}".format(
                "商店交易" if shop_name == "Shop" else shop_name,
            ))

            j = 0
            for vendor in trade["npcs"]:
                if j > 2:
                    result.append(f"等共计{len(trade['npcs'])}个商人交易")
                    break
                vendor_partial = partials["npc", str(vendor)]
                result.append("  -- {} {} {}".format(
                    vendor_partial["n"],
                    await gt_core(f"locationIndex.{vendor_partial['l']}.name", name_lang) if 'l' in vendor_partial.keys() else "",
                    f"({vendor_partial['c'][0]}, {vendor_partial['c'][1]})" if 'c' in vendor_partial.keys() else ""
                ))
                j += 1
            j = 0
            for listing in trade["listings"]:
                if j > 2:
                    result.append(f"等共计{len(trade['listings'])}种兑换方式")
                    break
                listing_str = ""
                currency_str = ""
                k = 0
                for listingItem in listing["item"]:
                    if k > 2:
                        result.append(f"等共计{len(listing['item'])}项商品兑换")
                        break
                    listing_str += "- {}{} *{}\n".format(
                        item["name"] if str(listingItem["id"]) == str(item_id) else
                        partials[("item", str(listingItem["id"]))]['n'],
                        'HQ' if 'hq' in listingItem.keys() else '',
                        listingItem['amount']
                    )
                    k += 1
                k = 0
                for currency in listing["currency"]:
                    if k > 2:
                        result.append(f"等共计{len(listing['currency'])}项商品兑换")
                        break
                    currency_str += "- {}{} *{}\n".format(
                        item["name"] if str(currency["id"]) == str(item_id) else
                        partials[("item", str(currency["id"]))]['n'],
                        'HQ' if 'hq' in currency.keys() else '',
                        currency['amount']
                    )
                result.append("使用\n{}兑换获得\n{}".format(currency_str, listing_str))

    if "drops" in item.keys():
        hasSource = True
        result.append(f"·怪物掉落")
        for mobIndex in item["drops"]:
            mob = partials[("mob", str(mobIndex))]
            result.append("  -- {} {}".format(
                mob['n'],
                await gt_core(f"locationIndex.{mob['z']}.name", name_lang)
            ))
        result.append("")

    if "instances" in item.keys():
        hasSource = True
        result.append(f"·副本获取")
        i = 0
        for dutyIndex in item["instances"]:
            if i > 4:
                result.append(f"等共计{len(item['instances'])}个副本获取")
                break
            duty = partials[("instance", str(dutyIndex))]
            result.append("  -- {}级 {}".format(
                duty['min_lvl'], duty['n']
            ))
            i += 1
        result.append("")

    if "quests" in item.keys():
        hasSource = True
        result.append(f"·任务奖励")
        i = 0
        for questIndex in item["quests"]:
            if i > 4:
                result.append(f"等共计{len(item['instance'])}个任务奖励")
                break
            quest = partials[("quest", str(questIndex))]
            result.append("  -- {}\n{}".format(
                quest["n"], f"https://garlandtools.cn/db/#quest/{quest['i']}"
            ))
            i += 1
        result.append("")

    if not hasSource:
        result.append("获取方式较麻烦/没查到，烦请打开网页查看！")

    status = ""

    if "unique" in item.keys():
        status += f"独占 "

    if "tradeable" in item.keys():
        status += f"{'' if bool(item['tradeable']) else '不'}可交易 "

    if "unlistable" in item.keys():
        status += f"{'不' if bool(item['unlistable']) else ''}可在市场上交易 "

    if "reducible" in item.keys():
        status += f"{'' if bool(item['reducible']) else '不'}可精选 "

    if "storable" in item.keys():
        status += f"{'' if bool(item['storable']) else '不'}可放入收藏柜 "

    if not status.isspace():
        result.append(status)

    result.append(f"https://garlandtools.{'cn' if name_lang == 'chs' else 'org'}/db/#item/{item_id}")

    # return "\n".join(result)
    return result


async def get_xivapi_item(item_name, name_lang=""):
    api_base = CAFEMAKER if name_lang == "cn" else XIVAPI
    url = api_base + "/search?indexes=Item&string=" + item_name
    if name_lang:
        url = url + "&language=" + name_lang
    # r = requests.get(url, timeout=time_out, headers=get_headers())
    j = await aiohttp_get(url)
    # j = await r.json()
    return j, url


async def search_item(name, FF14WIKI_BASE_URL, FF14WIKI_API_URL, url_quote=True):
    try:
        # 优先搜索本地物品id
        # todo 本地搜索暂时没有支持模糊匹配
        if name in item_dict:
            logger.info("使用本地物品id搜索 " + name)
            try:
                return await parse_item_garland(item_dict[name], "cn")
            except Exception as e:
                return f"搜索失败！{repr(e)}"

        logger.info("使用网络id搜索 " + name)
        name_lang = None
        for lang in ["cn", "en", "ja", "fr", "de"]:
            j, search_url = await get_xivapi_item(name, lang)
            if j.get("Results"):
                name_lang = lang
                break
        if name_lang is None:
            return False
        api_base = CAFEMAKER if name_lang == "cn" else XIVAPI
        res_num = j["Pagination"]["ResultsTotal"]

        try:
            return await parse_item_garland(j["Results"][0]["ID"], name_lang)
        except Exception as e:
            return f"搜索失败！{repr(e)}"

    # except requests.exceptions.ReadTimeout:
    #     res_data = "%s 的搜索请求超时了" % name
    # except json.decoder.JSONDecodeError:
    #     print(j.text)
    except Exception as e:
        return f"物品名搜索失败！{repr(e)}"


async def run(name):
    msg = "发生甚么事了？"
    # for _ in range(retry_num):
    try:
        res_data = await search_item(name, FF14WIKI_BASE_URL, FF14WIKI_API_URL)

        if isinstance(res_data, dict):
            msg = Message([MessageSegment(type="share", data=res_data)])

            # msg = str(res_data)
        elif isinstance(res_data, list):
            msg = Message([MessageSegment(type="image", data={"file": res_data[0]}),
                           MessageSegment(type="text", data={"text": "\n".join(res_data[1:])})])
        elif isinstance(res_data, str):
            msg = res_data
        else:
            msg = '在最终幻想XIV中没有找到"{}"'.format(name)

        # break
    except Exception as e:
        msg = "Error: {}".format(str(e))
        traceback.print_exc()
        logging.error(e)
        time.sleep(0.5)

    await item.finish(msg)


@item.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(" ", 1)
    if len(args) < 2:
        await item.finish("查物品格式： " + default_command_start + this_command + " 物品名")
    args = args[1]
    if args:
        state["item_info"] = args  # 如果用户发送了参数则直接赋值


@item.got("item_info")
async def handle_item(bot: Bot, event: Event, state: T_State):
    await run(state["item_info"])
