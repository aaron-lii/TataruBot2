# -*- coding: utf-8 -*-
"""
查副本攻略
"""

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

import re

from tatarubot2.plugins.utils import aiohttp_get, str2img, default_command_start

this_command = "攻略 "
dungeon_note = on_command(this_command, priority=5)

url = "https://ff14.org/duty"

async def dungeon_note_help():
    return default_command_start + this_command + "(副本等级) 副本名关键字 (文本)：查简单副本攻略，括号内为可选参数，默认输出图片攻略"

async def run(dungeon_info):
    # 获取所有攻略页面列表
    note_dict = {}
    r = await aiohttp_get(url, res_type="text")
    pattern = re.compile(r'/duty/.*?</a>', re.S)
    res_list = pattern.findall(r)
    for line in res_list[:-3]:
        page_id = line.split(".htm", 1)[0].replace("/duty/", "")
        d_level = line.split("[", 1)[1].split("]", 1)[0]
        d_name = line.split("] ", 1)[1].split("\n", 1)[0]
        if d_level in note_dict:
            note_dict[d_level][d_name] = page_id
        else:
            note_dict[d_level] = {d_name: page_id}

    # 处理输入文本 获得子页面id
    dungeon_info = dungeon_info.split(" ")
    page_id_now = []
    dungeon_level = None
    is_text = False
    if len(dungeon_info) == 1:
        dungeon_name = dungeon_info[0]
    elif len(dungeon_info) == 2:
        if dungeon_info[0].isdigit():
            dungeon_level = dungeon_info[0]
            dungeon_name = dungeon_info[1]
        elif "文本" == dungeon_info[1]:
            dungeon_name = dungeon_info[0]
            is_text = True
    else:
        if dungeon_info[0].isdigit():
            dungeon_level = dungeon_info[0]
            dungeon_name = dungeon_info[1]
        if "文本" == dungeon_info[2]:
            is_text = True

    # 先根据副本名字搜一遍
    for level_info, d_info in note_dict.items():
        for key, val in d_info.items():
            if dungeon_name in key:
                page_id_now.append([level_info, key, val])
    if not page_id_now:
        return "副本名没搜到鸭"

    # 如果有等级再搜一遍
    page_id_new = []
    if len(page_id_now) > 1 and dungeon_level:
        for page_now in page_id_now:
            if dungeon_level == page_now[0]:
                page_id_new.append(page_now)
        if len(page_id_new) > 0:
            page_id_now = page_id_new

    if len(page_id_now) > 1:
        res_text = "是哪个副本呢？重新告诉我哦~\n"
        for page_now in page_id_now:
            res_text += page_now[0] + " " + page_now[1] + "、"
        return res_text[:-1]

    # 获取具体攻略
    r = await aiohttp_get(url + "/" + page_id_now[0][-1] + ".htm", res_type="text")
    pattern = re.compile(r'<p>.*?</p>|<h\d.*?</h\d>')
    res_list = pattern.findall(r)
    res_text = ""
    for text_now in res_list:
        text_now = re.sub(r'<.*?>', '', text_now)
        res_text += text_now + "\n"

    if not is_text:
        img_bytes = str2img(res_text)
        res_text = Message([MessageSegment.image(img_bytes)])

    return res_text


@dungeon_note.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(" ", 1)
    if len(args) < 2:
        await dungeon_note.finish("查攻略格式：" + this_command + "(副本等级) 副本名关键字 (文本)。"
                                                              "括号内为可选参数，默认输出图片攻略。")
    args = args[1]
    if args:
        state["dungeon_info"] = args  # 如果用户发送了参数则直接赋值


@dungeon_note.got("dungeon_info")
async def handle_dungeon_note(bot: Bot, event: Event, state: T_State):
    res = await run(state["dungeon_info"])
    await dungeon_note.finish(res)