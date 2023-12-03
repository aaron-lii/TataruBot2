# -*- coding: utf-8 -*-
"""
一些通用功能
"""

import io
import json
import os
import random

import aiohttp
import emoji
from PIL import Image, ImageFont, ImageDraw
from aiohttp_socks import ProxyConnector
from nonebot import logger, get_driver
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import Depends
from nonebot.params import CommandArg

"""
读取插件配置文件，没有则创建默认配置
"""
# 当前目录
this_dir = os.path.split(os.path.realpath(__file__))[0]
json_path = "./tatarubot2_conf.json"

# 读取最新默认配置文件
with open(os.path.join(this_dir, "../data/plugins_conf.json"), "r", encoding="utf-8") as f_r:
    plugins_new_dict = json.load(f_r)

if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f_r:
        plugins_dict = json.load(f_r)
    if ("conf_ver" not in plugins_dict) or \
            (plugins_new_dict["conf_ver"]["ver"] != plugins_dict["conf_ver"]["ver"]):
        logger.error("配置文件有大改动，请删除机器人目录下 tatarubot2_conf.json 文件，再重启机器人。"
                     "最新配置版本号为：" + plugins_new_dict["conf_ver"]["ver"])
        plugins_dict = None
else:
    plugins_dict = plugins_new_dict
    with open(json_path, "w", encoding="utf-8") as f_w:
        json.dump(plugins_dict, f_w, ensure_ascii=False, indent=2)

if plugins_dict:
    proxy_url = plugins_dict["proxy"]["url"]
else:
    proxy_url = None


def get_conf_dict():
    return plugins_dict


""" aiohttp功能封装 """


async def aiohttp_get(url_input, res_type="json", time_out=15, header_plus=None, proxy=False):
    agent = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 '
             'Safari/537.36 QIHU 360SE',
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
             'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 '
             'Safari/537.36']
    headers = {'Connection': 'close', 'User-Agent': agent[random.randint(0, len(agent) - 1)]}

    if isinstance(header_plus, dict):
        for key, val in header_plus.items():
            headers[key] = val

    if proxy:
        connector = ProxyConnector.from_url(proxy_url)
    else:
        connector = None

    timeout = aiohttp.ClientTimeout(total=time_out)
    async with aiohttp.ClientSession(timeout=timeout, headers=headers, connector=connector) as session:
        res = await session.get(url_input)
        if res.status != 200:
            return None
        if res_type == "json":
            return await res.json()
        elif res_type == "bytes":
            return await res.read()
        elif res_type == "text":
            return await res.text()


""" 文字转图片 """
fontSize = 20  # 文字大小
max_width = 25  # 行宽
# ttf_path = os.path.join(this_dir, "../data/songti.ttf")
ttf_path = os.path.join(this_dir, "../data/simhei.ttf")
font = ImageFont.truetype(ttf_path, size=fontSize)


def str2img(text, width_now=max_width):
    # 匹配图片宽度，特殊字符、字母、数字占位会比中文少一半
    k = 0
    text_new = ""
    for char_one in text:
        if char_one == "\n":
            # if len(text_new) > 1 and text_new[-1] != "\n":
            if len(text_new) > 1:
                text_new += char_one
            k = 0
            continue
        if len(char_one.encode()) > 1:
            k = k + 2
        else:
            k = k + 1
        text_new += char_one
        if k >= 2 * width_now:
            text_new += "\n"
            k = 0

    lines = text_new.split('\n')

    # 背景颜色
    im = Image.new("RGB", ((int(width_now * 22)), (len(lines) + 1) * (fontSize + 2)), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    # 文字颜色
    dr.text((10, 10), text_new, font=font, fill=(0, 0, 0))
    # 保存
    img_bytes = io.BytesIO()
    im.save(img_bytes, format='JPEG')
    img_bytes = img_bytes.getvalue()
    return img_bytes


""" 获取随机emoji """
emoji_list = []
for key, val in emoji.EMOJI_DATA.items():
    emoji_list.append(key)
emoji_len = len(emoji_list) - 1


def get_emoji():
    emoji_i = random.randint(0, emoji_len)
    return emoji_list[emoji_i]


default_command_start = next(iter(get_driver().config.command_start))


def NoArg():
    """ 防止命令前缀为空时误触发 """

    async def dep(matcher: Matcher, args=CommandArg()):
        if len(args) != 0:
            await matcher.finish()

    return Depends(dep)
