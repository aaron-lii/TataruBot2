# -*- coding: utf-8 -*-
"""
暖暖
"""

from bilibili_api import user

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from datetime import datetime

import json
import os
import re
import traceback

from tatarubot2.plugins.utils import aiohttp_get, str2img, logger, NoArg, default_command_start

this_command = "暖暖"
nuannuan = on_command(this_command, priority=5)

# 腾讯文档地址
qq_doc = "https://docs.qq.com/sheet/DY2lCeEpwemZESm5q?tab=dewveu&c=A1A0A0"

# 游玩C哩酱 bilibili 用户id
bil_id = 15503317


async def nuannuan_help():
    return default_command_start + this_command + "：本周时尚品鉴作业"

def get_current_period() -> int:
    base = datetime(2018, 5, 16, 16, 0, 0)
    curr = datetime.now()
    if curr < base:
        raise ValueError("当前系统时间早于2018年10月16日，请修正系统时间")
    dt = datetime.now() - base
    period = dt.days // 7 + 38
    return period

async def get_bili_url():
    """ 从腾讯文档获取当期b站地址 """
    table_id = "DY2lCeEpwemZESm5q"
    sheet_id = "dewveu"
    headers = {'referer': "https://docs.qq.com/sheet/{}?tab={}".format(table_id, sheet_id),
               'authority': "docs.qq.com",
               'accept': "*/*"}

    r = await aiohttp_get('https://docs.qq.com/dop-api/opendoc?tab={}&id={}&outformat=1&normal=1'.format(sheet_id, table_id),
                          res_type="json",
                          header_plus=headers)
    r = str(r)

    try:
        bili_url = re.search(r"https://www.bilibili.com/video/[^\']*", r).group()
    except AttributeError:
        period = get_current_period()
        prefix = f"【FF14/时尚品鉴】第{period}期"
        u = user.User(bil_id)
        videos = await u.get_videos(ps=5, pn=1)
        for v in videos["list"]["vlist"]:
            if v["title"].startswith(prefix):
                bili_url = f"https://www.bilibili.com/video/{v["bvid"]}"
                break
        else:
            raise ValueError("找不到最新一期bilibili视频链接")

    logger.info(bili_url)

    return bili_url


async def get_bili_detail(bili_url):
    """ 获取bilibili详细页 """
    r = await aiohttp_get(bili_url, res_type="text")

    res = re.search(r"<span class=\"desc-info-text\".*?</span>", r, flags=re.S).group()

    # res = res.replace("<span class=\"desc-info-text\">", "")
    res = res.split("\n", 1)[1]
    res = res.replace("</span>", "")

    return res


async def get_nuannuan():
    this_dir = os.path.split(os.path.realpath(__file__))[0]
    cache_path = os.path.join(this_dir, "../cache/nuannaun.json")
    period = get_current_period()

    if os.path.exists(cache_path):
        with open(cache_path, mode="r") as fp:
            cache = json.load(fp)
        if msg := cache.get(str(period)) is not None:
            img_bytes = str2img(msg)
            await nuannuan.finish(msg)

    try:
        bili_url = await get_bili_url()
        msg = await get_bili_detail(bili_url)

        with open(cache_path, mode="w") as fp:
            json.dump({str(period): msg}, fp)

        img_bytes = str2img(msg)
        msg = Message([MessageSegment.image(img_bytes)])
    except Exception as e:
        # msg = "Error: {}".format(type(e))
        msg = "暖暖获取失败，请看qq文档： " + qq_doc
        traceback.print_exc()

    await nuannuan.finish(msg)



@nuannuan.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State, _=NoArg()):
    await get_nuannuan()
