import os
import json

"""
读取各插件是否开启的文件，没有则创建默认配置
"""
json_path = "./tatarubot2_conf.json"

if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f_r:
        plugins_dict = json.load(f_r)
else:
    plugins_dict = {
                "chat_ai": False,
                "api_key": "这里填你自己的chatgpt账号aip key，需要魔法上网",
                "ff_weibo": True,
                "house": True,
                "item": True,
                "item_new": True,
                "logs_dps": True,
                "lottery": True,
                "market": True,
                "market_new": True,
                "nuannuan": True,
                "precious": True,
                "weather": False}
    with open("./tatarubot2_conf.json", "w", encoding="utf-8") as f_w:
        json.dump(plugins_dict, f_w, ensure_ascii=False, indent=2)

"""
加载指定插件
"""
if plugins_dict["chat_ai"]:
    from .chat_ai import *
    openai.api_key = plugins_dict["api_key"]
if plugins_dict["ff_weibo"]:
    from .ff_weibo import *
if plugins_dict["house"]:
    from .house import *
if plugins_dict["item"]:
    from .item import *
if plugins_dict["item_new"]:
    from .item_new import *
if plugins_dict["logs_dps"]:
    from .logs_dps import *
if plugins_dict["lottery"]:
    from .lottery import *
if plugins_dict["market"]:
    from .market import *
if plugins_dict["market_new"]:
    from .market_new import *
if plugins_dict["nuannuan"]:
    from .nuannuan import *
if plugins_dict["precious"]:
    from .precious import *
if plugins_dict["weather"]:
    from .weather import *

from .bot_help import *
