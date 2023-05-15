import asyncio
from io import BytesIO
from typing import List
from pathlib import Path

import aiohttp
from PIL import Image, ImageDraw
from gsuid_core.logger import logger

from ..utils.api import get_sqla
from ..utils.mys_api import mys_api
from ..utils.error_reply import get_error
from ..utils.image.convert import convert_img
from ..sruid_utils.api.mys.models import Expedition
from ..utils.fonts.starrail_fonts import (
    sr_font_22,
    sr_font_24,
    sr_font_26,
    sr_font_36,
    sr_font_50,
)

TEXT_PATH = Path(__file__).parent / 'texture2D'

note_bg = Image.open(TEXT_PATH / 'note_bg.png')
note_travel_bg = Image.open(TEXT_PATH / 'note_travel_bg.png')

based_w = 700
based_h = 1200
white_overlay = Image.new('RGBA', (based_w, based_h), (255, 251, 242, 225))

first_color = (29, 29, 29)
second_color = (98, 98, 98)
white_color = (255, 255, 255)
green_color = (15, 196, 35)
orange_color = (237, 115, 61)
red_color = (235, 61, 75)


def seconds2hours(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return '%02d:%02d:%02d' % (h, m, s)


async def download_image(url: str) -> Image.Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            img_data = await response.read()
            img = Image.open(BytesIO(img_data))
            return img


async def _draw_task_img(
    img: Image.Image,
    img_draw: ImageDraw.ImageDraw,
    index: int,
    char: Expedition,
):
    if char is not None:
        expedition_name = char['name']
        remaining_time: str = seconds2hours(char['remaining_time'])
        note_travel_img = note_travel_bg.copy()
        for i in range(2):
            avatar_url = char['avatars'][i]
            image = await download_image(avatar_url)
            char_pic = image.convert('RGBA').resize(
                (40, 40), Image.Resampling.LANCZOS  # type: ignore
            )
            note_travel_img.paste(char_pic, (495 + 68 * i, 20), char_pic)
        img.paste(note_travel_img, (0, 790 + index * 80), note_travel_img)
        if char['status'] == 'Finished':
            status_mark = '待收取'
        else:
            status_mark = str(remaining_time)
        img_draw.text(
            (120, 830 + index * 80),
            expedition_name,
            font=sr_font_22,
            fill=white_color,
            anchor='lm',
        )
        img_draw.text(
            (380, 830 + index * 80),
            status_mark,
            font=sr_font_22,
            fill=white_color,
            anchor='mm',
        )
    else:
        note_travel_img = note_travel_bg.copy()
        img.paste(note_travel_img, (0, 790 + index * 80), note_travel_img)
        img_draw.text(
            (120, 830 + index * 80),
            '等待加入探索队列...',
            font=sr_font_22,
            fill=white_color,
            anchor='lm',
        )


async def get_resin_img(bot_id: str, user_id: str):
    try:
        sqla = get_sqla(bot_id)
        uid_list: List = await sqla.get_bind_sruid_list(user_id)
        logger.info('[每日信息]UID: {}'.format(uid_list))
        # 进行校验UID是否绑定CK
        useable_uid_list = []
        for uid in uid_list:
            status = await sqla.get_user_cookie(uid)
            if status is not None:
                useable_uid_list.append(uid)
        logger.info('[每日信息]可用UID: {}'.format(useable_uid_list))
        if len(useable_uid_list) == 0:
            return '请先绑定一个可用CK & UID再来查询哦~'
        # 开始绘图任务
        task = []
        img = Image.new(
            'RGBA', (based_w * len(useable_uid_list), based_h), (0, 0, 0, 0)
        )
        for uid_index, uid in enumerate(useable_uid_list):
            task.append(_draw_all_resin_img(img, uid, uid_index))
        await asyncio.gather(*task)
        res = await convert_img(img)
        logger.info('[查询每日信息]绘图已完成,等待发送!')
    except TypeError:
        logger.exception('[查询每日信息]绘图失败!')
        res = '你绑定过的UID中可能存在过期CK~请重新绑定一下噢~'

    return res


async def _draw_all_resin_img(img: Image.Image, uid: str, index: int):
    resin_img = await draw_resin_img(uid)
    img.paste(resin_img, (700 * index, 0), resin_img)


async def seconds2hours_zhcn(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return '%02d小时%02d分' % (h, m)


async def draw_resin_img(sr_uid: str) -> Image.Image:
    # 获取数据
    daily_data = await mys_api.get_daily_data(sr_uid)

    img = note_bg.copy()

    if isinstance(daily_data, int):
        return get_error(daily_data)

    # nickname and level
    role_basic_info = await mys_api.get_role_basic_info(sr_uid)
    nickname = role_basic_info['nickname']
    level = role_basic_info['level']

    # 开拓力
    stamina = daily_data['current_stamina']
    max_stamina = daily_data['max_stamina']
    stamina_str = f'{stamina}/{max_stamina}'
    stamina_percent = stamina / max_stamina
    if stamina_percent > 0.8:
        stamina_color = red_color
    else:
        stamina_color = second_color
    stamina_recovery_time = await seconds2hours_zhcn(
        daily_data['stamina_recover_time']
    )

    img_draw = ImageDraw.Draw(img)

    # 派遣
    task_task = []
    for i in range(4):
        char = (
            daily_data['expeditions'][i]
            if i < len(daily_data['expeditions'])
            else None
        )
        task_task.append(_draw_task_img(img, img_draw, i, char))
    await asyncio.gather(*task_task)

    # 绘制树脂圆环
    ring_pic = Image.open(TEXT_PATH / 'ring.apng')
    percent = (
        round(stamina_percent * 89)
        if round(stamina_percent * 89) <= 89
        else 89
    )
    ring_pic.seek(percent)
    img.paste(ring_pic, (0, 5), ring_pic)

    # 写树脂剩余时间
    img_draw.text(
        (350, 490),
        f'还剩{stamina_recovery_time}',
        font=sr_font_24,
        fill=stamina_color,
        anchor='mm',
    )
    # 写Nickname
    img_draw.text(
        (350, 139), nickname, font=sr_font_36, fill=white_color, anchor='mm'
    )
    # 写开拓等级
    img_draw.text(
        (350, 190),
        f'开拓等级{level}',
        font=sr_font_24,
        fill=white_color,
        anchor='mm',
    )
    # 写UID
    img_draw.text(
        (350, 663),
        f'UID{sr_uid}',
        font=sr_font_26,
        fill=first_color,
        anchor='mm',
    )
    # 写树脂
    img_draw.text(
        (350, 450),
        stamina_str,
        font=sr_font_50,
        fill=first_color,
        anchor='mm',
    )

    return img
