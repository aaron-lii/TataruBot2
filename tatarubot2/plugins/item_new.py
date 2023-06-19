# -*- coding: utf-8 -*-
"""
查物品 本地目录
"""

import os

from tatarubot2.plugins.item import *


this_command = "新物品 "
item_new = on_command(this_command, priority=5)


async def item_new_help():
    return default_command_start + this_command + "物品名：查物品异常时可以尝试这个版本"


# 加载字典
item_dict = {}
this_dir = os.path.split(os.path.realpath(__file__))[0]
json_path = os.path.join(this_dir, "../data/item_dict.json")
with open(json_path, "r", encoding="utf-8") as f_r:
    item_dict = json.load(f_r)


async def search_item(name, FF14WIKI_BASE_URL, FF14WIKI_API_URL, url_quote=True):
    try:
        # name_lang = None
        # for lang in ["cn", "en", "ja", "fr", "de"]:
        #     j, search_url = get_xivapi_item(name, lang)
        #     if j.get("Results"):
        #         name_lang = lang
        #         break
        # if name_lang is None:
        #     return False
        # api_base = CAFEMAKER if name_lang == "cn" else XIVAPI
        # res_num = j["Pagination"]["ResultsTotal"]

        if name not in item_dict:
            return False

        try:
            return await parse_item_garland(item_dict[name], "cn")
        except Exception as e:
            return f"搜索失败！{repr(e)}"

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
        msg = "Error: {}".format(type(e))
        traceback.print_exc()
        logging.error(e)
        time.sleep(0.5)

    await item_new.finish(msg)


@item_new.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(" ", 1)
    if len(args) < 2:
        await item.finish("查物品格式： " + default_command_start + this_command + " 物品名")
    args = args[1]
    if args:
        state["item_info"] = args  # 如果用户发送了参数则直接赋值


@item_new.got("item_info")
async def handle_item(bot: Bot, event: Event, state: T_State):
    await run(state["item_info"])
