# -*- coding: utf-8 -*-
"""
logs上dps分段
"""

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import os
# import requests
# import aiohttp
import re
import json

from tatarubot2.plugins.utils import aiohttp_get, default_command_start

this_command = "输出 "
logs_dps = on_command(this_command, priority=5)


async def logs_dps_help():
    return default_command_start + this_command + "boss名 职业名 (国服) (rdps) (day2):\n" \
           "查询logs上对应boss和职业的dps分段，括号内为可选的参数，默认国际服、adps、截止最后一天"


# 加载职业和boss信息
this_dir = os.path.split(os.path.realpath(__file__))[0]
job_path = os.path.join(this_dir, "../data/job.json")
boss_path = os.path.join(this_dir, "../data/boss.json")
with open(job_path, "r", encoding="utf-8") as j_r:
    data_job = json.load(j_r)
with open(boss_path, "r", encoding="utf-8") as b_r:
    data_boss = json.load(b_r)


# 检查是哪个职业
def check_job(job):
    for j in data_job:
        if job == j["name"] or job == j["cn_name"] or job in j["nickname"]:
            return j
    return False


# 检查是哪个boss
def check_boss(boss):
    for b in data_boss:
        if boss == b["name"] or boss == b["cn_name"] or boss in b["nickname"]:
            return b
    return False


# 获取dps信息页面
async def get_request(cn_source, boss_dict, job_dict, dps_type):
    if cn_source:
        region_len = len(boss_dict["cn_region"])
        region_list = boss_dict["cn_region"]
    else:
        region_len = len(boss_dict["region"])
        region_list = boss_dict["region"]

    search_range = []
    if region_len > 1:
        for i in range(region_len):
            search_range.append(- i - 1)
    else:
        search_range = [-1]

    # s = requests.Session()
    # s.headers.update({"referer": "https://{}.fflogs.com".format("cn" if cn_source else "www")})
    # timeout = aiohttp.ClientTimeout(total=15)
    # session = aiohttp.ClientSession(timeout=timeout,
    #                                 headers={"referer": "https://{}.fflogs.com".format("cn" if cn_source else "www")})

    for i in search_range:
        region_id = int(region_list[i].split("###", 1)[1])
        fflogs_url = "https://{}.fflogs.com/zone/statistics/table/" \
                     "{}/dps/{}/{}/8/{}/100/1000/7/{}/Global/{}/All/0/normalized/single/0/-1/?" \
                     "keystone=15&dpstype={}".format(
            "cn" if cn_source else "www",
            boss_dict["quest"],
            boss_dict["pk"],
            boss_dict["savage"],
            region_id,
            boss_dict["patch"],
            job_dict["name"],
            dps_type,
        )
        print("fflogs url:{}".format(fflogs_url))

        # r = await session.get(fflogs_url)
        # r = await r.text()
        r = await aiohttp_get(fflogs_url, res_type="text",
                              header_plus={"referer": "https://{}.fflogs.com".format("cn" if cn_source else "www")})

        if "data.push" in r:
            return r, region_list[i].split("###", 1)[0]

    return None


# 规整化最终返回结果
def normalize_result(res_dict, cn_source, boss_dict, job_dict, dps_type, region_info):
    res = "服务器: {}  dps类型: {}\n版本: {}\n副本: {}\nboss: {}\n职业: {}  天数: {}\n".format(
        "国服" if cn_source else "国际服",
        dps_type,
        region_info,
        boss_dict["cn_zone_name"],
        boss_dict["cn_name"],
        job_dict["cn_name"],
        res_dict["day"]
    )
    res_data = "10%: {}\n25%: {}\n50%: {}\n75%: {}\n95%: {}\n99%: {}\n100%: {}".format(
        "%.2f" % res_dict["10"],
        "%.2f" % res_dict["25"],
        "%.2f" % res_dict["50"],
        "%.2f" % res_dict["75"],
        "%.2f" % res_dict["95"],
        "%.2f" % res_dict["99"],
        "%.2f" % res_dict["100"],
    )
    return res + res_data


async def crawl_dps(boss, job, day=-1, CN_source=False, dps_type="adps"):
    print("boss:{} job:{} day:{}".format(boss, job, day))
    job_dict = check_job(job)
    if not job_dict:
        return "检查职业名称是否正确"
    boss_dict = check_boss(boss)
    if not boss_dict:
        return "检查boss名称是否正确"

    r_list = await get_request(CN_source, boss_dict, job_dict, dps_type)
    if not r_list:
        return "查不到数据，怎么回事呢？"
    r = r_list[0]
    region_info = r_list[1]

    percentage_list = [10, 25, 50, 75, 95, 99, 100]
    statistics = {}
    for percentage in percentage_list:
        re_str = "series{}".format(
            "" if percentage == 100 else percentage) + r".data.push\([+-]?(0|(?:[1-9]\d*)(?:\.\d+)?)\)"
        ptn = re.compile(re_str)
        find_res = ptn.findall(r)
        statistics[str(percentage)] = list(map(lambda x: float(x), find_res))
    total_length = len(statistics['100'])
    for percentage in percentage_list:
        assert len(statistics[str(percentage)]) == total_length, "Length of parsed dps aren't consistent"
    l = 0
    r = total_length - 1

    def all_0(stat, idx):
        sum_dps = 0
        for perc in percentage_list:
            sum_dps += stat[str(perc)][idx]
        return sum_dps == 0

    while l < total_length and all_0(statistics, l):
        l += 1
    while r >= 0 and all_0(statistics, r):
        r -= 1
    if l > r or l >= total_length or r < 0:
        return "No data found"
    stat_list = []
    for idx, (p10, p25, p50, p75, p95, p99, p100) in enumerate(zip(
            statistics['10'][l:r + 1],
            statistics['25'][l:r + 1],
            statistics['50'][l:r + 1],
            statistics['75'][l:r + 1],
            statistics['95'][l:r + 1],
            statistics['99'][l:r + 1],
            statistics['100'][l:r + 1],
    ), 1):
        stat_list.append({
            'day': idx,
            '10': p10,
            '25': p25,
            '50': p50,
            '75': p75,
            '95': p95,
            '99': p99,
            '100': p100,
        })

    if not stat_list:
        return "No data found"

    if day == -1 or day >= len(stat_list):
        return normalize_result(stat_list[-1], CN_source, boss_dict, job_dict, dps_type, region_info)

    return normalize_result(stat_list[day], CN_source, boss_dict, job_dict, dps_type, region_info)


async def run(args):
    boss = args[0]
    job = args[1]

    if "国服" in args:
        CN_source = True
    else:
        CN_source = False

    if "rdps" in args:
        dps_type = "rdps"
    else:
        dps_type = "adps"

    day = -1
    if len(args) > 2:
        for arg in args[2: ]:
            if "day" in arg:
                try:
                    day = int(arg.replace("day", "")) - 1
                    break
                except:
                    await logs_dps.finish("day格式不对")
                    return

    msg = await crawl_dps(boss, job, day=day, CN_source=CN_source, dps_type=dps_type)
    print(msg)
    msg = str(msg)
    await logs_dps.finish(msg)


@logs_dps.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(" ")
    if len(args) < 3:
        await logs_dps.finish("查logs格式： " + default_command_start + this_command +
                              "boss名 职业名 (国服) (rdps) (day2)，括号内为可选参数")
    args = args[1: ]
    if args:
        state["item_info"] = args  # 如果用户发送了参数则直接赋值


@logs_dps.got("item_info")
async def handle_item(bot: Bot, event: Event, state: T_State):
    await run(state["item_info"])