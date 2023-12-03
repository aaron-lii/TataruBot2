# -*- coding: utf-8 -*-

from nonebot import on_command, get_driver
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

from tatarubot2.plugins.utils import NoArg

this_command = "帮帮忙"
bot_help = on_command(this_command, rule=to_me(), priority=5)

# 获取机器人昵称
bot_name = get_driver().config.nickname
if not bot_name:
    bot_name = ""
else:
    bot_name = next(iter(bot_name))

async def create_help():
    help_text = """()括号表示可选的参数
[暖暖] 本周时尚品鉴作业
[选门] 帮你选藏宝洞的门
[仙人彩] 帮你选每周仙人仙彩数字
[看看微博] 获取FF微博新闻
[物品 物品名] 查询物品信息
[价格 (大区/服务器) 物品名] 查询板子物价，默认大区/服务器在配置文件中指定，不指定默认豆豆柴
[房子 服务器名 主城名 房子大小] 查询空房。主城名为：森都、海都、沙都、白银、雪都。房子大小为：S、M、L
[输出 boss名 职业名 (国服) (rdps) (day2)] 查询logs上对应boss和职业的dps分段，默认国际服、adps、截止最后一天
[攻略 (副本等级) 副本名关键字 (文本)] 查简单副本攻略，默认输出图片攻略
[日历] 获取FF近期活动日历
[招募 大区名] 获取指定大区招募板信息
[抽卡] 随机抽取一张FF14塔罗牌
"""

    return "  【{}现有指令】\n".format(bot_name) + help_text


@bot_help.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State, _=NoArg()):
    return_str = await create_help()
    await bot_help.finish(return_str)
