# -*- coding: utf-8 -*-
"""
一些通用功能
"""

import aiohttp
import random


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
        if res_type == "json":
            return await res.json()
        elif res_type == "bytes":
            return await res.read()
        elif res_type == "text":
            return await res.text()