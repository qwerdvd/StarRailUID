import re

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.error_reply import UID_HINT

from ..utils.convert import get_uid
from .draw_abyss_card import draw_abyss_img

sv_srabyss = SV('sr查询深渊')


@sv_srabyss.on_command(
    ('sr查询深渊', 'srsy', 'sr查询上期深渊', 'srsqsy', 'sr上期深渊', 'sr深渊'), block=True
)
async def send_srabyss_info(bot: Bot, ev: Event):
    name = ''.join(re.findall('[\u4e00-\u9fa5]', ev.text))
    if name:
        return

    await bot.logger.info('开始执行[sr查询深渊信息]')
    uid = await get_uid(bot, ev)
    if uid is None:
        return await bot.send(UID_HINT)
    await bot.logger.info('[sr查询深渊信息]uid: {}'.format(uid))

    if 'sq' in ev.command or '上期' in ev.command:
        schedule_type = '2'
    else:
        schedule_type = '1'
    await bot.logger.info('[sr查询深渊信息]深渊期数: {}'.format(schedule_type))

    if ev.text in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']:
        floor = (
            ev.text.replace('一', '1')
            .replace('二', '2')
            .replace('三', '3')
            .replace('四', '4')
            .replace('五', '5')
            .replace('六', '6')
            .replace('七', '7')
            .replace('八', '8')
            .replace('九', '9')
            .replace('十', '10')
        )
    else:
        floor = ev.text
    if floor and floor.isdigit():
        floor = int(floor)
    else:
        floor = None
    # print(floor)
    await bot.logger.info('[sr查询深渊信息]深渊层数: {}'.format(floor))
    # data = GsCookie()
    # raw_abyss_data = await data.get_spiral_abyss_data(uid, schedule_type)
    # print(raw_abyss_data)
    im = await draw_abyss_img(ev.user_id, uid, floor, schedule_type)
    await bot.send(im)
