from .utils import get_conf_dict

plugins_dict = get_conf_dict()

"""
加载指定插件
"""
if plugins_dict:
    if plugins_dict["chat_ai"]["enable"]:
        from .chat_ai import *
        openai.api_key = plugins_dict["chat_ai"]["api_key"]
    if plugins_dict["ff_weibo"]["enable"]:
        from .ff_weibo import *
    if plugins_dict["house"]["enable"]:
        from .house import *
    if plugins_dict["item"]["enable"]:
        from .item import *
    if plugins_dict["logs_dps"]["enable"]:
        from .logs_dps import *
    if plugins_dict["lottery"]["enable"]:
        from .lottery import *
    if plugins_dict["market"]["enable"]:
        from .market import *
    if plugins_dict["nuannuan"]["enable"]:
        from .nuannuan import *
    if plugins_dict["precious"]["enable"]:
        from .precious import *
    if plugins_dict["weather"]["enable"]:
        from .weather import *
    if plugins_dict["dungeon_note"]["enable"]:
        from .dungeon_note import *
    if plugins_dict["calendar"]["enable"]:
        from .calendar import *
    if plugins_dict["bot_help"]["enable"]:
        from .bot_help import *
    if plugins_dict["party_finder"]["enable"]:
        from .party_finder import *
    if plugins_dict["tarot"]["enable"]:
        from .tarot import *