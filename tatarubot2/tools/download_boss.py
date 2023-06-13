# -*- coding: utf-8 -*-

import requests
import json
import re
import time


def get_zone_name(quest_id, text):
    """ 获取任务名 """
    pattern = re.compile(r'<a href="/zone/rankings/{}" class="zone-name">.*?</a>'.format(quest_id))
    res = pattern.findall(text)
    res_name = res[0].replace('<a href="/zone/rankings/{}" class="zone-name">'.format(quest_id), '').replace('</a>', '')
    return res_name

def get_boss_name(text):
    """ 获取boss名 """
    pattern = re.compile(r'setBoss\(.*?, this\)".*?<span class="boss-text">.*?</span>')
    res = pattern.findall(text)
    res_final = res[1:]
    res_list = []
    for j in range(len(res_final)):
        boss_id = res_final[j].split(", this", 1)[0].replace("setBoss(", "")
        boss_id = int(boss_id)
        boss_name = res_final[j].split('boss-text">', 1)[1].replace('</span>', '')
        res_list.append((boss_id, boss_name))
    return res_list

def get_region(server, text):
    """ 获取版本号 """
    region_list = []
    if server == "cn":
        pattern = re.compile(r'setRegion\(.*?, this\)">标准.*?</a>')
        res = pattern.findall(text)
        if res:
            for res_now in res:
                region_id = res_now.split(", this)", 1)[0]
                region_id = region_id.replace("setRegion(", "")
                region_id = region_id
                region_name = res_now.split('">', 1)[1]
                region_name = region_name.replace("</a>", "")
                region_list.append(region_name + "###" + region_id)
        else:
            region_list = ["-1###1"]
    else:
        pattern = re.compile(r'setRegion\(.*?, this\)">Standard.*?</a>')
        res = pattern.findall(text)
        if res:
            for res_now in res:
                region_id = res_now.split(", this)", 1)[0]
                region_id = region_id.replace("setRegion(", "")
                region_id = region_id
                region_name = res_now.split('">', 1)[1]
                region_name = region_name.replace("</a>", "")
                region_list.append(region_name + "###" + region_id)
        else:
            region_list = ["-1###1"]

    return region_list


def run():
    with open("tatarubot2/data/boss.json", "r", encoding="utf-8") as f_r:
        data_boss = json.load(f_r)

    url = "https://{}.fflogs.com/zone/statistics/{}"

    new_list = []

    for i in range(1, 100):
        time.sleep(1)
        savage = 100
        patch = 0

        url_now = url.format("www", str(i))
        r = requests.get(url_now, timeout=60)
        if r.status_code == 404:
            continue

        if "difficulty-101" in r.text:
            savage = 101

        zone_name_en = get_zone_name(i, r.text)
        boss_name_en_list = get_boss_name(r.text)
        region_en = get_region("en", r.text)

        url_now = url.format("cn", str(i))
        r = requests.get(url_now, timeout=60)
        zone_name_cn = get_zone_name(i, r.text)
        boss_name_cn_list = get_boss_name(r.text)
        region_cn = get_region("cn", r.text)

        for j in range(len(boss_name_en_list)):
            boss_name_en_now = boss_name_en_list[j]
            boss_name_cn_now = boss_name_cn_list[j]

            boss_dict = None

            boss_exist = False
            for k in range(len(data_boss)):
                if boss_name_en_now[0] == data_boss[k]["pk"]:
                    boss_exist = True
                    nick_name = data_boss[k]["nickname"]
                    boss_dict = {"pk": boss_name_en_now[0],
                                 "quest": i,
                                 "zone_name": zone_name_en,
                                 "cn_zone_name": zone_name_cn,
                                 "name": boss_name_en_now[1],
                                 "cn_name": boss_name_cn_now[1],
                                 "nickname": nick_name,
                                 "patch": patch,
                                 "savage": savage,
                                 "region": region_en,
                                 "cn_region": region_cn,
                                 }
                    break

            if not boss_exist:
                boss_dict = {"pk": boss_name_en_now[0],
                             "quest": i,
                             "zone_name": zone_name_en,
                             "cn_zone_name": zone_name_cn,
                             "name": boss_name_en_now[1],
                             "cn_name": boss_name_cn_now[1],
                             "nickname": [],
                             "patch": patch,
                             "savage": savage,
                             "region": region_en,
                             "cn_region": region_cn,
                             }

            if boss_dict:
                new_list.append(boss_dict)
                print(boss_dict)

    with open("tatarubot2/tools/new_boss.json", "w", encoding="utf-8") as f_w:
        json.dump(new_list, f_w, ensure_ascii=False, indent=2)







if __name__ == "__main__":
    run()