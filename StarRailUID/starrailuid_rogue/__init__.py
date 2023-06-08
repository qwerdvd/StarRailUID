import re

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.error_reply import UID_HINT

from ..utils.convert import get_uid
from ..utils.sr_prefix import PREFIX
from .draw_rogue_card import draw_rogue_img

sv_srabyss = SV('sr查询模拟宇宙')


@sv_srabyss.on_command(
    (
        f'{PREFIX}查询宇宙',
        f'{PREFIX}yz',
        f'{PREFIX}查询上期宇宙',
        f'{PREFIX}sqyz',
        f'{PREFIX}上期宇宙',
        f'{PREFIX}宇宙',
        f'{PREFIX}查询模拟宇宙',
        f'{PREFIX}上期模拟宇宙',
        f'{PREFIX}查询上期模拟宇宙',
    ),
    block=True,
)
async def send_srabyss_info(bot: Bot, ev: Event):
    name = ''.join(re.findall('[\u4e00-\u9fa5]', ev.text))
    if name:
        return

    await bot.logger.info('开始执行[sr查询模拟宇宙信息]')
    uid, user_id = await get_uid(bot, ev, True)
    if uid is None:
        return await bot.send(UID_HINT)
    await bot.logger.info('[sr查询模拟宇宙信息]uid: {}'.format(uid))

    if 'sq' in ev.command or '上期' in ev.command:
        schedule_type = '2'
    else:
        schedule_type = '3'
    await bot.logger.info('[sr查询模拟宇宙信息]模拟宇宙期数: {}'.format(schedule_type))

    if ev.text in ['一', '二', '三', '四', '五', '六']:
        floor = (
            ev.text.replace('一', '1')
            .replace('二', '2')
            .replace('三', '3')
            .replace('四', '4')
            .replace('五', '5')
            .replace('六', '6')
        )
    else:
        floor = ev.text
    if floor and floor.isdigit():
        floor = int(floor)
    else:
        floor = None
    # print(floor)
    await bot.logger.info('[sr查询模拟宇宙信息]模拟宇宙世界数: {}'.format(floor))
    # data = GsCookie()
    # raw_rogue_data = await data.get_rogue_data(uid, schedule_type)
    # print(raw_rogue_data)
    im = await draw_rogue_img(user_id, uid, floor, schedule_type)
    await bot.send(im)
