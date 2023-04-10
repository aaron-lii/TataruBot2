# -*- coding: utf-8 -*-

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import openai

# 控制是否开启该功能
# on_chat = False

this_command = "问问 "
chat_ai = on_command(this_command, rule=to_me(), priority=5)

# openai.api_key = "这里填你自己的chatgpt账号aip key"

async def chat_run(args):
    # print(openai.api_key)

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是FF14里面的角色塔塔露.也是我的小助手,请简洁地回答我的问题,不需要复杂的解释."},
            {"role": "user", "content": args}
        ],
        # max_tokens=200
    )
    res = completion.choices[0].message
    if "content" in res:
        res = res["content"].strip()
    else:
        res = "不懂呢！"
    return res


@chat_ai.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    # if not on_chat:
    #     return
    args = str(event.get_message()).strip().split(this_command, 1)
    if len(args) < 2:
        return

    return_str = await chat_run(args[1])
    await chat_ai.finish(return_str)

