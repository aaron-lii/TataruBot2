# -*- coding: utf-8 -*-
"""
近期活动日历
"""

from nonebot import get_driver
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot import logger

import os
import asyncio
from datetime import datetime
from icalendar import Calendar

from tatarubot2.plugins.utils import aiohttp_get, get_conf_dict, NoArg, default_command_start

this_command = "日历"
calendar = on_command(this_command, priority=5)

conf_dict = get_conf_dict()
use_proxy = conf_dict["proxy"]["enable"]

# 订阅地址
url = "https://p66-caldav.icloud.com/published/2/MTAyMTk3MTMxMjExMDIxOXsjasy" \
      "7WUO0EcKVz7qGEuVjjTlRkgd6WOZM171uxP_u-QM51M24lHzRlAQir-oodDRRTzZeusSLbw0snkZoqI4"

# 当前目录
this_dir = os.path.split(os.path.realpath(__file__))[0]
ics_path = os.path.join(this_dir, "../data/calendar.ics")
# 记录上次同步日历时间
last_download_time = 0

async def calendar_help():
    return default_command_start + this_command + "：获取FF近期活动日历"


""" 此处添加任务 每一段时间同步一次日历 """
async def download_calendar():
    logger.info("开启日历自动更新")
    while True:
        try:
            res = await aiohttp_get(url, res_type="bytes", proxy=use_proxy)
            if res is not None:
                with open(ics_path, "wb") as f_w:
                    f_w.write(res)
                global last_download_time
                last_download_time = datetime.now()
                logger.info("日历更新 成功")
            else:
                logger.info("日历更新 失败")
        except Exception as e:
            logger.error("日历更新连接错误" + str(e))
        await asyncio.sleep(60 * 60)

""" nb启动时运行 """
driver = get_driver()
@driver.on_startup
async def auto_download():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(download_calendar())
    else:
        logger.warning("日历自动更新似乎有问题")


def res_format(info_item):
    """ 处理格式 """
    end_info = str(info_item[0]).strip().split("+", 1)[0].rsplit(":", 1)[0].replace("-", ".")
    start_info = str(info_item[1]).strip().split("+", 1)[0].rsplit(":", 1)[0].replace("-", ".")
    summary_info = str(info_item[2]).strip()
    res = "* " + summary_info + "\n  " + start_info + " 至 " + end_info
    return res


async def run():
    # 读取本地日历文件
    with open(ics_path, "rb") as ics_f:
        gcal = Calendar.from_ical(ics_f.read())

    time_info = datetime.now()

    warn_ics = []
    week_ics = []
    feature_ics = []

    for component in gcal.walk():
        if component.name == "VEVENT":
            start_date_info = component.get('dtstart').dt
            end_data_info = component.get('dtend').dt

            if type(end_data_info) == type(time_info.date()):
                end_date = end_data_info
                start_date = start_date_info
            else:
                end_date = end_data_info.date()
                start_date = start_date_info.date()
                start_date_info = start_date_info.date()
                end_data_info = end_data_info.date()

            # 只记录今后的日历
            if end_date < time_info.date():
                continue

            info_item = [end_data_info, start_date_info,
                         component.get('summary'), component.get('DESCRIPTION')]

            if (end_date - time_info.date()).days <= 2:
                warn_ics.append(info_item)
            elif (end_date - time_info.date()).days <= 7:
                week_ics.append(info_item)
            else:
                feature_ics.append(info_item)

    warn_ics.sort()
    week_ics.sort()
    feature_ics.sort()
    res = "今天是 " + str(time_info.date()).replace("-", ".") + "\n"
    if warn_ics:
        res += "【近2天结束】\n"
        for item in warn_ics:
            res += res_format(item) + "\n"
    if week_ics:
        res += "【近7天内】\n"
        for item in week_ics:
            res += res_format(item) + "\n"
    if feature_ics:
        res += "【未来活动】\n"
        for item in feature_ics:
            res += res_format(item) + "\n"

    if last_download_time != 0:
        res += "\n日历更新时间: " + str(last_download_time).split(".")[0].replace("-", ".")
    else:
        res += "\n日历更新时间: 未知"

    await calendar.finish(res)


@calendar.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State, _=NoArg()):
    await run()

