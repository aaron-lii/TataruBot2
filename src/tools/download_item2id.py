# -*- coding: utf-8 -*-

import requests
import json
import sys
sys.path.insert(0, "../../")


def run():
    # url = "https://cafemaker.wakingsands.com/Item/"
    url = "https://ffxiv.cyanclay.xyz/db/doc/item/chs/3/"
    item2id_dict = {}
    error_list = []

    i = 1
    while i < 40000:
        print(i)
        try:
            r = requests.get(url + str(i) + ".json", timeout=60)
            if r.status_code == 404:
                i += 1
                continue
            # item2id_dict[r.json()["Name_chs"]] = i
            with open("data.json", "a") as f_w:
                f_w.write(r.json()["item"]["name"] + "!!!" + str(i) + "\n")
            f_w.flush()
        except Exception as e:
            # print(e)
            error_list.append(i)

        i += 1

    while error_list:
        print(error_list)
        error_list_now = []
        for j in error_list:
            try:
                r = requests.get(url + str(i) + ".json", timeout=60)
                # item2id_dict[r.json()["Name_chs"]] = i
                with open("data.json", "a") as f_w:
                    f_w.write(r.json()["item"]["name"] + "!!!" + str(i) + "\n")
                f_w.flush()
            except Exception as e:
                error_list_now.append(i)

        error_list = error_list_now


def run2():
    item_dict = {}
    i = 0
    with open("data.json", "r") as f_r:
        for line in f_r.readlines():
            i += 1
            line = line.strip().split("!!!")
            if line[0] in item_dict:
                print(line[0], line[1], item_dict[line[0]])
            else:
                item_dict[line[0]] = line[1]

    with open("item_dict.json", "w") as f_w:
        f_w.write(str(item_dict))


if __name__ == "__main__":
    run2()
