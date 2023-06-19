# -*- coding: utf-8 -*-
"""
FFweibo新闻
"""

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

# import requests
from tatarubot2.plugins.utils import aiohttp_get, NoArg, default_command_start

this_command = "看看微博"
ff_weibo = on_command(this_command, priority=5)

url = "https://m.weibo.cn/api/container/getIndex?type=uid&value=1797798792&containerid=1076031797798792"

async def ff_weibo_help():
    return default_command_start + this_command + "：获取FF微博新闻"


async def run():
    # r = requests.get(url, timeout=15).json()
    r = await aiohttp_get(url)
    # r = await r.json()

    return_list = []

    for i in range(5):
        weibo_text = r["data"]["cards"][i]["mblog"]["text"]
        weibo_time = r["data"]["cards"][i]["mblog"]["created_at"]
        weibo_url = "https://m.weibo.cn/status/" + r["data"]["cards"][i]["mblog"]["bid"]

        split1 = 0
        split2 = 0
        return_text = ""

        try:
            for word in weibo_text:
                if split1 > 0:
                    if word == ">":
                        split1 = 0
                    continue
                if split2 > 0:
                    if word =="#":
                        split2 = 0
                    continue
                if word == "<":
                    if return_text != "":
                        break
                    split1 = 1
                    continue
                elif word == "#":
                    if return_text != "":
                        break
                    split2 = 1
                    continue
                elif word.strip() == "":
                    continue
                else:
                    return_text += word

            weibo_title = return_text
            # weibo_title = weibo_text.split(r"#FF14#</span></a>")[1].split(r"<br />")[0]
        except Exception as e:
            weibo_title = "这条格式好像不对呢？"

        weibo_time = " ".join(weibo_time.split(" ")[:4])
        return_list.append("【" + str(i + 1) + "】" + weibo_title + " " + weibo_time + "\n" + weibo_url)

    await ff_weibo.finish("\n".join(return_list))


@ff_weibo.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State, _=NoArg()):
    await run()
