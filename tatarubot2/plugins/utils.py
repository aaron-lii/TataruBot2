# -*- coding: utf-8 -*-
"""
一些通用功能
"""

import aiohttp
import random
import os
from PIL import Image, ImageFont, ImageDraw
import io


# 当前目录
this_dir = os.path.split(os.path.realpath(__file__))[0]


async def aiohttp_get(url_input, res_type="json", time_out=15, header_plus=None):
    """ aiohttp功能封装 """
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

    timeout = aiohttp.ClientTimeout(total=time_out)
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
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
max_width = 25 # 行宽
ttf_path = os.path.join(this_dir, "../data/songti.ttf")
font = ImageFont.truetype(ttf_path, size=fontSize)
def str2img(text):
    #匹配图片宽度，特殊字符、字母、数字占位会比中文少一半
    k = 0
    text_new = ""
    for char_one in text:
        if char_one == "\n":
            if len(text_new) > 1 and text_new[-1] != "\n":
                text_new += char_one
            k = 0
            continue
        if len(char_one.encode()) > 1:
            k = k + 2
        else:
            k = k + 1
        text_new += char_one
        if k >= 2 * max_width:
            text_new += "\n"
            k = 0

    lines = text_new.split('\n')

    # 背景颜色
    im = Image.new("RGB", ((int(max_width * 21.5)), len(lines) * (fontSize + 5)), (255,255,255))
    dr = ImageDraw.Draw(im)
    # 文字颜色
    dr.text((0, 0), text_new, font=font, fill=(0,0,0))
    # 保存
    img_bytes = io.BytesIO()
    im.save(img_bytes, format='JPEG')
    img_bytes = img_bytes.getvalue()
    return img_bytes