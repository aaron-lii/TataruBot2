"""
招募版
"""


from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

import re

from tatarubot2.plugins.utils import aiohttp_get, str2img, default_command_start

this_command = "招募 "
party_finder = on_command(this_command, priority=5)


party_finder_url = "https://xivpf.littlenightmare.top/listings"


async def party_finder_run(data_centre=""):
    all_info = await aiohttp_get(party_finder_url, res_type="text")

    data_centre_list = re.findall(r"data-centre=\".*?\"", all_info)
    duty_list = re.findall(r"<div class=\"duty .*?</div>", all_info)
    description_list = re.findall(r"<div class=\"description\">.*?</div>", all_info)
    meta_list = re.findall(r"class=\"text\">.*?</span>", all_info)

    text_list = []
    index_now = 1
    for i in range(len(data_centre_list)):
        # 过滤非指定大区
        if data_centre not in data_centre_list[i]:
            continue

        data_centre_now = data_centre_list[i].split("\"")[1].replace("\"", "")
        duty_now = duty_list[i].split(">", 1)[1].replace("</div>", "")
        description_now = description_list[i].split(">", 1)[1].replace("</div>", "")
        if "</span>" in description_now:
            description_now = description_now.split("</span>", 1)[1]
        creator_now = meta_list[i * 4].split(">", 1)[1].replace("</span>", "")
        world_now = meta_list[i * 4 + 1].split(">", 1)[1].replace("</span>", "")
        expires_now = meta_list[i * 4 + 2].split(">", 1)[1].replace("</span>", "")
        updated_now = meta_list[i * 4 + 3].split(">", 1)[1].replace("</span>", "")

        full_index = '%03d' % index_now
        text_now = "{} ============================================\n".format(full_index)
        text_now += "[" + data_centre_now + "] "
        text_now += duty_now + "\n"
        text_now += "------------------------------------------------\n"
        text_now += description_now + "\n"
        text_now += "------------------------------------------------\n"
        text_now += creator_now + ", " + \
                      world_now + "\n" +\
                      expires_now + ", " +\
                      updated_now + "\n"
        text_now +="------------------------------------------------\n\n"

        index_now += 1
        text_list.append(text_now)

    if not text_list:
        return "当前无人上传招募信息"

    msg_list = []
    for i in range(0, len(text_list), 40):
        final_text = "  \n  \n  \n" \
                     "    【 招 募 板 】 {} ~ {}\n\n".format(str(i + 1),
                                                           str(min(i + 40, len(text_list))))
        final_text += "".join(text_list[i: i + 40])
        img_bytes = str2img(final_text)
        msg_list.append(MessageSegment.image(img_bytes))

    msg = Message(msg_list)

    return msg


@party_finder.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(" ", 1)
    if len(args) <= 1:
        await party_finder.finish("查招募版格式： " + default_command_start + this_command +
                                  " 大区名称")

    data_centre_list = ["陆行鸟", "莫古力", "猫小胖", "豆豆柴"]
    if len(args) > 1 and args[1] not in data_centre_list:
        await party_finder.finish("大区名称有误，限定" + str(data_centre_list))

    state["party_finder_info"] = args[1]


@party_finder.got("party_finder_info")
async def handle_item(bot: Bot, event: Event, state: T_State):
    msg = await party_finder_run(state["party_finder_info"])

    await party_finder.finish(msg)