import json
from pathlib import Path
from typing import Union
from datetime import datetime

from PIL import Image, ImageDraw
from gsuid_core.logger import logger

from ..utils.mys_api import mys_api
from ..utils.error_reply import get_error
from ..utils.image.convert import convert_img
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.fonts.starrail_fonts import sr_font_20, sr_font_28, sr_font_34

TEXT_PATH = Path(__file__).parent / 'texture2d'

monthly_bg = Image.open(TEXT_PATH / 'monthly_bg.png')
avatar_default = Image.open(TEXT_PATH / '200101.png')

first_color = (29, 29, 29)
second_color = (67, 61, 56)
second_color2 = (98, 98, 98)
black_color = (54, 54, 54)
white_color = (213, 213, 213)

COLOR_MAP = {
    '每日活跃': (248, 227, 157),
    '活动奖励': (99, 231, 176),
    '冒险奖励': (114, 205, 251),
    '模拟宇宙奖励': (160, 149, 248),
    '忘却之庭奖励': (221, 119, 250),
    '邮件奖励': (244, 110, 104),
    '其他': (255, 242, 200),
    'Daily Activity': (248, 227, 157),
    'Events': (99, 231, 176),
    'Adventure': (114, 205, 251),
    'moni': (160, 149, 248),
    'Spiral Abyss': (221, 119, 250),
    'Quests': (244, 110, 104),
    'Other': (255, 242, 200),
}


async def draw_note_img(sr_uid: str) -> Union[bytes, str]:
    path = PLAYER_PATH / str(sr_uid)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # 获取当前时间
    now = datetime.now()
    current_year_mon = now.strftime('%Y-%m')
    add_month = ''
    if int(now.month) < 10:
        add_month = '0'
    now_month = str(now.year) + str(add_month) + str(now.month)
    print(now_month)
    # 获取数据
    data = await mys_api.get_award(sr_uid, now_month)
    if isinstance(data, int):
        return get_error(data)

    # 保存数据
    with open(
        path / f'monthly_{current_year_mon}.json', 'w', encoding='utf-8'
    ) as f:
        save_data = json.dumps(
            {
                'data_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'data': data,
            },
            ensure_ascii=False,
        )
        f.write(save_data)

    # 获取上月数据
    last_month = now.month - 1
    last_year = now.year
    if last_month == 0:
        last_month = 12
        last_year -= 1
    last_year_mon = f'{last_year}-{last_month:02d}'
    last_monthly_path = path / f'monthly_{last_year_mon}.json'
    if last_monthly_path.exists():
        with open(last_monthly_path, 'r', encoding='utf-8') as f:
            last_monthly_data = json.load(f)
            last_monthly_data = last_monthly_data['data']
    else:
        add_month = ''
        if int(last_month) < 10:
            add_month = '0'
        find_last_month = str(last_year) + str(add_month) + str(last_month)
        print(find_last_month)
        last_monthly_data = await mys_api.get_award(sr_uid, find_last_month)

    # nickname and level
    role_basic_info = await mys_api.get_role_basic_info(sr_uid)
    if isinstance(role_basic_info, int):
        return get_error(role_basic_info)
    nickname = role_basic_info['nickname']

    day_hcoin = data['day_data']['current_hcoin']
    day_rails_pass = data['day_data']['current_rails_pass']
    lastday_hcoin = 0
    lastday_rails_pass = 0
    if int(sr_uid[0]) < 6:
        lastday_hcoin = data['day_data']['last_hcoin']
        lastday_rails_pass = data['day_data']['last_rails_pass']
    month_hcoin = data['month_data']['current_hcoin']
    month_rails_pass = data['month_data']['current_rails_pass']
    lastmonth_hcoin = data['month_data']['last_hcoin']
    lastmonth_rails_pass = data['month_data']['last_rails_pass']

    day_hcoin_str = await int_carry(day_hcoin)
    day_rails_pass_str = await int_carry(day_rails_pass)
    month_hcoin_str = await int_carry(month_hcoin)
    month_rails_pass_str = await int_carry(month_rails_pass)
    lastday_hcoin_str = await int_carry(lastday_hcoin)
    lastday_rails_pass_str = await int_carry(lastday_rails_pass)
    lastmonth_hcoin_str = await int_carry(lastmonth_hcoin)
    lastmonth_rails_pass_str = await int_carry(lastmonth_rails_pass)

    img = monthly_bg.copy()
    avatar_img = avatar_default.copy()
    char_pic = avatar_img.convert('RGBA').resize(
        (125, 125), Image.Resampling.LANCZOS  # type: ignore
    )
    img.paste(char_pic, (115, 133), char_pic)
    img_draw = ImageDraw.Draw(img)

    # 写Nickname
    img_draw.text(
        (310, 184), nickname, font=sr_font_34, fill=first_color, anchor='lm'
    )

    # 写UID
    img_draw.text(
        (267, 219),
        f'UID {sr_uid}',
        font=sr_font_20,
        fill=second_color2,
        anchor='lm',
    )

    # 写本日星琼
    img_draw.text(
        (283, 326),
        day_hcoin_str,
        font=sr_font_28,
        fill=white_color,
        anchor='lm',
    )

    # 写本月星琼
    img_draw.text(
        (513, 326),
        month_hcoin_str,
        font=sr_font_28,
        fill=white_color,
        anchor='lm',
    )

    # 写昨日星琼
    img_draw.text(
        (283, 366),
        lastday_hcoin_str,
        font=sr_font_28,
        fill=black_color,
        anchor='lm',
    )

    # 写上月星琼
    img_draw.text(
        (513, 366),
        lastmonth_hcoin_str,
        font=sr_font_28,
        fill=black_color,
        anchor='lm',
    )

    # 写本日铁票
    img_draw.text(
        (283, 431),
        day_rails_pass_str,
        font=sr_font_28,
        fill=white_color,
        anchor='lm',
    )

    # 写本月铁票
    img_draw.text(
        (513, 431),
        month_rails_pass_str,
        font=sr_font_28,
        fill=white_color,
        anchor='lm',
    )

    # 写昨日铁票
    img_draw.text(
        (283, 473),
        lastday_rails_pass_str,
        font=sr_font_28,
        fill=black_color,
        anchor='lm',
    )

    # 写上月铁票
    img_draw.text(
        (513, 473),
        lastmonth_rails_pass_str,
        font=sr_font_28,
        fill=black_color,
        anchor='lm',
    )
    xy = ((0, 0), (2100, 2100))
    temp = -90
    if not data['month_data']['group_by']:
        pie_image = Image.new("RGBA", (2100, 2100), color=(255, 255, 255, 0))
        pie_image_draw = ImageDraw.Draw(pie_image)
        pie_image_draw.ellipse(xy, fill=(128, 128, 128))
    else:
        pie_image = Image.new("RGBA", (2100, 2100), color=(255, 255, 255, 0))
        pie_image_draw = ImageDraw.Draw(pie_image)
        for index, i in enumerate(data['month_data']['group_by']):
            pie_image_draw.pieslice(
                xy,
                temp,
                temp + (i['percent'] / 100) * 360,
                COLOR_MAP[i['action_name']],
            )
            temp = temp + (i['percent'] / 100) * 360
    # 绘制蒙版圆形
    new_image = Image.new("RGBA", (2100, 2100), color=(255, 255, 255, 0))
    pie_image_draw.ellipse((150, 150, 1950, 1950), fill=(255, 255, 255, 0))

    position = (1050, 1050)
    pie_image.paste(new_image, position, mask=new_image)
    result_pie = pie_image.resize((210, 210))
    img.paste(result_pie, (138, 618), result_pie)

    if last_monthly_data:
        pie_image = Image.new("RGBA", (2100, 2100), color=(255, 255, 255, 0))
        pie_image_draw = ImageDraw.Draw(pie_image)
        for index, i in enumerate(last_monthly_data['month_data']['group_by']):
            pie_image_draw.pieslice(
                xy,
                temp,
                temp + (i['percent'] / 100) * 360,
                COLOR_MAP[i['action_name']],
            )
            temp = temp + (i['percent'] / 100) * 360
    else:
        pie_image = Image.new("RGBA", (2100, 2100), color=(255, 255, 255, 0))
        pie_image_draw = ImageDraw.Draw(pie_image)
        pie_image_draw.ellipse(xy, fill=(128, 128, 128))

    # 绘制蒙版圆形
    new_image = Image.new("RGBA", (2100, 2100), color=(255, 255, 255, 0))
    pie_image_draw.ellipse((150, 150, 1950, 1950), fill=(255, 255, 255, 0))

    position = (1050, 1050)
    pie_image.paste(new_image, position, mask=new_image)
    result_pie = pie_image.resize((210, 210))
    img.paste(result_pie, (138, 618 + 350), result_pie)

    img = await convert_img(img)
    logger.info('[开拓月历] 图片绘制完成!等待发送...')
    return img


async def int_carry(i: int) -> str:
    if i >= 100000:
        i_str = '{:.1f}W'.format(i / 10000)
    else:
        i_str = str(i)
    return i_str
