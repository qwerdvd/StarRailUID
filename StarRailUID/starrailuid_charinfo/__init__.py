import re

# import json
from typing import Tuple

from PIL import Image
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from .to_card import api_to_card
from ..utils.convert import get_uid
from ..utils.error_reply import UID_HINT
from ..utils.image.convert import convert_img
from .draw_char_img import draw_char_info_img
from ..utils.resource.RESOURCE_PATH import TEMP_PATH

sv_char_info_config = SV('sr面板设置', pm=2)
sv_get_char_info = SV('sr面板查询', priority=10)
sv_get_sr_original_pic = SV('sr查看面板原图', priority=5)


@sv_get_char_info.on_prefix('sr查询')
async def send_char_info(bot: Bot, ev: Event):
    im = await _get_char_info(bot, ev, ev.text)
    if isinstance(im, str):
        await bot.send(im)
    elif isinstance(im, Tuple):
        if isinstance(im[0], Image.Image):
            img = await convert_img(im[0])
        else:
            img = im[0]
        await bot.send(img)
        if im[1]:
            with open(TEMP_PATH / f'{ev.msg_id}.jpg', 'wb') as f:
                f.write(im[1])
    elif isinstance(im, Image.Image):
        await bot.send(await convert_img(im))
    elif isinstance(im, bytes):
        await bot.send(await convert_img(im))
    elif im is None:
        return
    else:
        await bot.send('发生未知错误')


async def _get_char_info(bot: Bot, ev: Event, text: str):
    # 获取角色名
    msg = ''.join(re.findall('[\u4e00-\u9fa5 ]', text))
    if not msg:
        return
    await bot.logger.info('开始执行[查询角色面板]')
    # 获取uid
    uid = await get_uid(bot, ev)
    if uid is None:
        return await bot.send(UID_HINT)
    await bot.logger.info('[查询角色面板]uid: {}'.format(uid))

    im = await draw_char_info_img(msg, uid, ev.image)
    return im


@sv_get_char_info.on_command('sr强制刷新')
async def send_card_info(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    if uid is None:
        return await bot.send(UID_HINT)
    await bot.logger.info('[sr强制刷新]uid: {}'.format(uid))
    im = await api_to_card(uid)
    await bot.logger.info(f'UID{uid}获取角色数据成功！')
    await bot.send(im)
