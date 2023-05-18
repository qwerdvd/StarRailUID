from pathlib import Path
from typing import Union, Optional

from PIL import Image, ImageDraw
from gsuid_core.logger import logger
from gsuid_core.utils.error_reply import get_error

from .utils import get_icon
from ..utils.convert import GsCookie
from ..utils.image.convert import convert_img
from ..sruid_utils.api.mys.models import AbyssAvatar
from ..utils.image.image_tools import get_qq_avatar, draw_pic_with_ring
from ..utils.fonts.starrail_fonts import (
    sr_font_22,
    sr_font_28,
    sr_font_30,
    sr_font_34,
    sr_font_42,
)

abyss_list = {
    '1': '琥珀恩赐其一',
    '2': '琥珀恩赐其二',
    '3': '琥珀恩赐其三',
    '4': '琥珀恩赐其四',
    '5': '琥珀恩赐其五',
    '6': '琥珀恩赐其六',
    '7': '琥珀恩赐其七',
    '8': '琥珀恩赐其八',
    '9': '琥珀恩赐其九',
    '10': '琥珀恩赐其十',
}

TEXT_PATH = Path(__file__).parent / 'texture2D'
white_color = (255, 255, 255)
gray_color = (175, 175, 175)
img_bg = Image.open(TEXT_PATH / 'bg.jpg')
level_cover = Image.open(TEXT_PATH / 'level_cover.png').convert("RGBA")
char_bg_4 = Image.open(TEXT_PATH / 'char4_bg.png').convert("RGBA")
char_bg_5 = Image.open(TEXT_PATH / 'char5_bg.png').convert("RGBA")

star_yes = Image.open(TEXT_PATH / 'star.png').convert("RGBA")
star_gray = Image.open(TEXT_PATH / 'star_gray.png').convert("RGBA")

elements = {
    "ice": Image.open(TEXT_PATH / "IconNatureColorIce.png").convert("RGBA"),
    "fire": Image.open(TEXT_PATH / "IconNatureColorFire.png").convert("RGBA"),
    "imaginary": Image.open(
        TEXT_PATH / "IconNatureColorImaginary.png"
    ).convert("RGBA"),
    "quantum": Image.open(TEXT_PATH / "IconNatureColorQuantum.png").convert(
        "RGBA"
    ),
    "lightning": Image.open(TEXT_PATH / "IconNatureColorThunder.png").convert(
        "RGBA"
    ),
    "wind": Image.open(TEXT_PATH / "IconNatureColorWind.png").convert("RGBA"),
    "physical": Image.open(TEXT_PATH / "IconNaturePhysical.png").convert(
        "RGBA"
    ),
}


async def get_abyss_star_pic(star: int) -> Image.Image:
    star_pic = Image.open(TEXT_PATH / f'star{star}.png')
    return star_pic


async def _draw_abyss_card(
    char: AbyssAvatar,
    talent_num: str,
    floor_pic: Image.Image,
    index_char: int,
    index_part: int,
):
    # char_id = char['id']
    # # 确认角色头像路径
    # char_pic_path = CHAR_ICON_PATH / f'{char_id}.png'
    char_bg = (char_bg_4 if char['rarity'] == 4 else char_bg_5).copy()
    char_icon = (await get_icon(char['icon'])).resize((151, 170))
    element_icon = elements[char['element']]
    char_bg.paste(char_icon, (24, 16), mask=char_icon)
    char_bg.paste(level_cover, (0, 0), mask=level_cover)
    char_bg.paste(element_icon, (135, 30), mask=element_icon)
    # 不存在自动下载
    # if not char_pic_path.exists():
    # await create_single_char_card(char_id)
    # talent_pic = await get_talent_pic(int(talent_num))
    # talent_pic = talent_pic.resize((90, 45))
    # char_card.paste(talent_pic, (137, 260), talent_pic)
    char_card_draw = ImageDraw.Draw(char_bg)
    char_card_draw.text(
        (100, 165),
        f'等级 {char["level"]}',
        font=sr_font_22,
        fill=white_color,
        anchor='mm',
    )
    floor_pic.paste(
        char_bg,
        (75 + 185 * index_char, 130 + index_part * 219),
        char_bg,
    )


async def _draw_floor_card(
    level_star: int,
    floor_pic: Image.Image,
    img: Image.Image,
    index_floor: int,
    floor_name: str,
    round_num: int,
):
    for index_num in [0, 1, 2]:
        star_num = index_num + 1
        if star_num <= level_star:
            star_pic = star_yes.copy()
        else:
            star_pic = star_gray.copy()
        floor_pic.paste(star_pic, (103 + index_num * 50, 25), star_pic)
    floor_pic_draw = ImageDraw.Draw(floor_pic)
    floor_pic_draw.text(
        (450, 60),
        floor_name,
        font=sr_font_42,
        fill=white_color,
        anchor='mm',
    )
    floor_pic_draw.text(
        (802, 60),
        f'使用轮: {round_num}',
        font=sr_font_28,
        fill=gray_color,
        anchor='rm',
    )
    img.paste(floor_pic, (0, 657 + index_floor * 570), floor_pic)


async def draw_abyss_img(
    qid: Union[str, int],
    uid: str,
    floor: Optional[int] = None,
    schedule_type: str = '1',
) -> Union[bytes, str]:
    # 获取Cookies
    data = GsCookie()
    # retcode = await data.get_cookie(uid)
    # if retcode:
    # return retcode
    # raw_data = data.raw_data
    raw_abyss_data = await data.get_spiral_abyss_data(uid, schedule_type)
    # print(raw_abyss_data)

    if isinstance(raw_abyss_data, int):
        return get_error(raw_abyss_data)

    # 获取数据
    # if raw_data:
    # char_data = raw_data['avatars']
    # else:
    # return '没有获取到角色数据'
    # char_temp = {}

    # 获取查询者数据
    if floor:
        floor_num = 1
        if floor > 10:
            return '楼层不能大于10层!'
        if len(raw_abyss_data['all_floor_detail']) < floor:
            return '你还没有挑战该层!'
    else:
        if raw_abyss_data['max_floor'] == '':
            return '你还没有挑战本期深渊!\n可以使用[sr上期深渊]命令查询上期~'
        floor_num = len(raw_abyss_data['all_floor_detail'])

    # 获取背景图片各项参数
    based_w = 900
    if floor_num >= 3:
        based_h = 2367
    else:
        based_h = 657 + 570 * floor_num
    img = img_bg.copy()
    img = img.crop((0, 0, based_w, based_h))
    abyss_title = Image.open(TEXT_PATH / 'head.png')
    img.paste(abyss_title, (0, 0), abyss_title)

    # 获取头像
    _id = str(qid)
    if _id.startswith('http'):
        char_pic = await get_qq_avatar(avatar_url=_id)
    else:
        char_pic = await get_qq_avatar(qid=qid)
    char_pic = await draw_pic_with_ring(char_pic, 250)

    img.paste(char_pic, (325, 132), char_pic)

    # 绘制抬头
    img_draw = ImageDraw.Draw(img)
    img_draw.text((450, 442), f'UID {uid}', white_color, sr_font_28, 'mm')

    # 总体数据
    abyss_data = Image.open(TEXT_PATH / 'data.png')
    img.paste(abyss_data, (0, 500), abyss_data)

    # 最深抵达
    img_draw.text(
        (220, 565),
        f'{raw_abyss_data["max_floor"]}',
        white_color,
        sr_font_34,
        'lm',
    )
    # 挑战次数
    img_draw.text(
        (220, 612),
        f'{raw_abyss_data["battle_num"]}',
        white_color,
        sr_font_34,
        'lm',
    )

    star_num_pic = Image.open(TEXT_PATH / 'star.png')
    img.paste(star_num_pic, (615, 557), star_num_pic)

    img_draw.text(
        (695, 590),
        f'{raw_abyss_data["star_num"]}/30',
        white_color,
        sr_font_42,
        'lm',
    )

    for index_floor, level in enumerate(raw_abyss_data['all_floor_detail']):
        if index_floor >= 3:
            break
        floor_pic = Image.open(TEXT_PATH / 'floor_bg.png')
        level_star = level['star_num']
        floor_name = level['name']
        round_num = level['round_num']
        for index_part in [0, 1]:
            node_num = index_part + 1
            node = f'node_{node_num}'
            # 节点1
            time_array = level[node]['challenge_time']
            time_str = f"{time_array['year']}-{time_array['month']}"
            time_str = f"{time_str}-{time_array['day']}"
            time_str = (
                f"{time_str} {time_array['hour']}:{time_array['minute']}:00"
            )
            floor_pic_draw = ImageDraw.Draw(floor_pic)
            floor_pic_draw.text(
                (112, 120 + index_part * 219),
                f'节点{node_num}',
                white_color,
                sr_font_30,
                'lm',
            )
            floor_pic_draw.text(
                (201, 120 + index_part * 219),
                f'{time_str}',
                gray_color,
                sr_font_22,
                'lm',
            )

            for index_char, char in enumerate(level[node]['avatars']):
                # 获取命座
                # if char["id"] in char_temp:
                # talent_num = char_temp[char["id"]]
                # else:
                # for i in char_data:
                # if i["id"] == char["id"]:
                # talent_num = str(
                # i["actived_constellation_num"]
                # )
                # char_temp[char["id"]] = talent_num
                # break
                await _draw_abyss_card(
                    char,
                    0,  # type: ignore
                    floor_pic,
                    index_char,
                    index_part,
                )
        await _draw_floor_card(
            level_star,
            floor_pic,
            img,
            index_floor,
            floor_name,
            round_num,
        )

    # title_data = {
    # '最强一击!': damage_rank[0],
    # '最多击破!': defeat_rank[0],
    # '承受伤害': take_damage_rank[0],
    # '元素战技': energy_skill_rank[0],
    # }
    # for _index, _name in enumerate(title_data):
    # _char = title_data[_name]
    # _char_id = _char['avatar_id']
    # char_side_path = TEXT_PATH / f'{_char_id}.png'
    # # if not char_side_path.exists():
    # # await download_file(_char['avatar_icon'], 3, f'{_char_id}.png')
    # char_side = Image.open(char_side_path)
    # char_side = char_side.resize((75, 75))
    # intent = _index * 224
    # title_xy = (115 + intent, 523)
    # val_xy = (115 + intent, 545)
    # _val = str(_char['value'])
    # img.paste(char_side, (43 + intent, 484), char_side)
    # img_draw.text(title_xy, _name, white_color, gs_font_20, 'lm')
    # img_draw.text(val_xy, _val, white_color, gs_font_26, 'lm')

    # 过滤数据
    # raw_abyss_data['floors'] = [
    # i for i in raw_abyss_data['floors'] if i['index'] >= 9
    # ]

    # 绘制缩略信息
    # for num in range(4):
    # omit_bg = Image.open(TEXT_PATH / 'abyss_omit.png')
    # omit_draw = ImageDraw.Draw(omit_bg)
    # omit_draw.text((56, 34), f'第{num+9}层', white_color, gs_font_32, 'lm')
    # omit_draw.rounded_rectangle((165, 19, 225, 49), 20, red_color)
    # if len(raw_abyss_data['floors']) - 1 >= num:
    # _floor = raw_abyss_data['floors'][num]
    # if _floor['star'] == _floor['max_star']:
    # _color = red_color
    # _text = '全满星'
    # else:
    # _gap = _floor['max_star'] - _floor['star']
    # _color = blue_color
    # _text = f'差{_gap}颗'
    # if not is_unfull:
    # _timestamp = int(
    # _floor['levels'][-1]['battles'][-1]['timestamp']
    # )
    # _time_array = time.localtime(_timestamp)
    # _time_str = time.strftime('%Y-%m-%d %H:%M:%S', _time_array)
    # else:
    # _time_str = '请挑战后查看时间数据!'
    # else:
    # _color = gray_color
    # _text = '未解锁'
    # _time_str = '请挑战后查看时间数据!'
    # omit_draw.rounded_rectangle((165, 19, 255, 49), 20, _color)
    # omit_draw.text((210, 34), _text, white_color, gs_font_26, 'mm')
    # omit_draw.text((54, 65), _time_str, sec_color, gs_font_22, 'lm')
    # pos = (20 + 459 * (num % 2), 613 + 106 * (num // 2))
    # img.paste(omit_bg, pos, omit_bg)

    # if is_unfull:
    # hint = Image.open(TEXT_PATH / 'hint.png')
    # img.paste(hint, (0, 830), hint)
    # else:
    # task = []
    # floor_num = floors_data['index']
    # for index_floor, level in enumerate(floors_data['levels']):
    # floor_pic = Image.open(TEXT_PATH / 'abyss_floor.png')
    # level_star = level['star']
    # timestamp = int(level['battles'][0]['timestamp'])
    # time_array = time.localtime(timestamp)
    # time_str = time.strftime('%Y-%m-%d %H:%M:%S', time_array)
    # for index_part, battle in enumerate(level['battles']):
    # for index_char, char in enumerate(battle['avatars']):
    # # 获取命座
    # if char["id"] in char_temp:
    # talent_num = char_temp[char["id"]]
    # else:
    # for i in char_data:
    # if i["id"] == char["id"]:
    # talent_num = str(
    # i["actived_constellation_num"]
    # )
    # char_temp[char["id"]] = talent_num
    # break
    # task.append(
    # _draw_abyss_card(
    # char,
    # talent_num,  # type: ignore
    # floor_pic,
    # index_char,
    # index_part,
    # )
    # )
    # await asyncio.gather(*task)
    # task.clear()
    # task.append(
    # _draw_floor_card(
    # level_star,
    # floor_pic,
    # img,
    # time_str,
    # index_floor,
    # floor_num,
    # )
    # )
    # await asyncio.gather(*task)

    res = await convert_img(img)
    logger.info('[查询深渊信息]绘图已完成,等待发送!')
    return res
