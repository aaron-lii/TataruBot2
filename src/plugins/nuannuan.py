# -*- coding: utf-8 -*-
"""
暖暖
"""

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import requests
import re
import traceback

this_command = "暖暖"
nuannuan = on_command(this_command, priority=5)


async def nuannuan_help():
    return this_command + "：本周时尚品鉴作业"


def get_video_id(mid):
    try:
        # 获取用户信息最新视频的前五个，避免第一个视频不是攻略ps=5处修改
        url = f"https://api.bilibili.com/x/space/arc/search?mid={mid}&order=pubdate&pn=1&ps=5"
        r = requests.get(url, timeout=3).json()
        video_list = r["data"]["list"]["vlist"]
        for i in video_list:
            if re.match(r"【FF14\/时尚品鉴】第\d+期 满分攻略", i["title"]):
                return i["bvid"]
    except:
        traceback.print_exc()
    return None


def extract_nn(bvid):
    try:
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        r = requests.get(url, timeout=3).json()
        if r["code"] == 0:
            url = f"https://www.bilibili.com/video/{bvid}"
            title = r["data"]["title"]
            desc = r["data"]["desc"]
            text = desc.replace("个人攻略网站", "游玩C攻略站")
            image = r["data"]["pic"]
            res_data = {
                "url": url,
                "title": title,
                "content": text,
                "image": image,
            }
            # return res_data
            return text + "\n" + url
    except:
        traceback.print_exc()
    return None


async def get_qq_doc():
    try:
        url = f"https://www.youwanc.com/"
        r = requests.get(url, timeout=5).text
        qq_doc = re.search(r"https://docs.qq.com/[^\"]*", r)
        if qq_doc:
            msg = "暖暖看qq文档： " + qq_doc.group()
        else:
            msg = "查看qq文档出了点问题？"
    except Exception as e:
        msg = "Error: {}".format(type(e))
        traceback.print_exc()

    await nuannuan.finish(msg)


async def run():
    try:
        # 获取视频av号(aid)
        bvid = get_video_id(15503317)
        # 获取数据
        res_data = extract_nn(bvid)
        if not res_data:
            msg = "无法查询到有效数据，请稍后再试"
        else:
            # msg = [{"type": "text", "data": res_data}]
            # msg = [{"type": "text", "data": {"text": res_data}}]
            msg = res_data
            # if receive.get("message", "").endswith("image"):
            #     res_str = "\n".join([res_data["title"], res_data["content"]])
            # msg = text2img(res_str)
            # msg += res_data["url"]
            # print(msg)
    except Exception as e:
        msg = "Error: {}".format(type(e))
        traceback.print_exc()

    await nuannuan.finish(msg)


@nuannuan.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args != this_command:
        return

    # await run()
    await get_qq_doc()
