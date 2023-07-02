# -*- coding: utf-8 -*-
"""
暖暖
"""

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

import re
import traceback

from tatarubot2.plugins.utils import aiohttp_get, str2img, logger, NoArg, default_command_start

this_command = "暖暖"
nuannuan = on_command(this_command, priority=5)

# 腾讯文档地址
qq_doc = "https://docs.qq.com/sheet/DY2lCeEpwemZESm5q?tab=dewveu&c=A1A0A0"


async def nuannuan_help():
    return default_command_start + this_command + "：本周时尚品鉴作业"


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

    bili_url = re.search(r"https://www.bilibili.com/video/[^\']*", r).group()

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
    try:
        bili_url = await get_bili_url()
        msg = await get_bili_detail(bili_url)

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
