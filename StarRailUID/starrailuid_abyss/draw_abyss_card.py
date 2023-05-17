import asyncio
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw
from gsuid_core.logger import logger

from .utils import get_icon
from ..utils.convert import GsCookie
from ..utils.colors import first_color
from ..utils.image.convert import convert_img
from ..sruid_utils.api.mys.models import AbyssAvatar

# )
from ..utils.image.image_tools import (
    get_color_bg,
    get_qq_avatar,
    draw_pic_with_ring,
)
from ..utils.fonts.starrail_fonts import (
    sr_font_22,
    sr_font_26,
    sr_font_32,
    sr_font_36,
)

# from gsuid_core.utils.error_reply import get_error

# from ..utils.resource.download_url import download_file
# from ..utils.resource.generate_char_card import create_single_char_card
# from ..utils.resource.RESOURCE_PATH import (
# CHAR_ICON_PATH,

TEXT_PATH = Path(__file__).parent / 'texture2D'

char_bg_4 = Image.open(TEXT_PATH / 'rarity4_bg.png').convert("RGBA")
char_bg_5 = Image.open(TEXT_PATH / 'rarity5_bg.png').convert("RGBA")

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
    char_card_draw = ImageDraw.Draw(char_bg)
    char_icon = (await get_icon(char['icon'])).resize((140, 160))

    element_icon = elements[char['element']]

    char_bg.paste(char_icon, (4, 8), mask=char_icon)
    char_bg.paste(element_icon, (100, 10), mask=element_icon)
    # 不存在自动下载
    # if not char_pic_path.exists():
    # await create_single_char_card(char_id)
    # talent_pic = await get_talent_pic(int(talent_num))
    # talent_pic = talent_pic.resize((90, 45))
    # char_card.paste(talent_pic, (137, 260), talent_pic)
    char_card_draw.text(
        (70, 185),
        f'Lv.{char["level"]}',
        font=sr_font_26,
        fill=first_color,
        anchor='mm',
    )
    floor_pic.paste(
        char_bg,
        (75 + 219 * index_char, 120 + index_part * 230),
        char_bg,
    )


async def _draw_floor_card(
    level_star: int,
    floor_pic: Image.Image,
    img: Image.Image,
    time_str: str,
    index_floor: int,
    floor_name: str,
    round_num: int,
):
    star_pic = await get_abyss_star_pic(level_star)
    floor_pic.paste(star_pic, (729, 20), star_pic)
    floor_pic_draw = ImageDraw.Draw(floor_pic)
    floor_pic_draw.text(
        (75, 45),
        floor_name,
        font=sr_font_32,
        fill=first_color,
        anchor='lm',
    )
    floor_pic_draw.text(
        (75, 90),
        time_str,
        font=sr_font_22,
        fill=first_color,
        anchor='lm',
    )
    floor_pic_draw.text(
        (875, 90),
        f'使用轮 - {round_num}',
        font=sr_font_22,
        fill=first_color,
        anchor='rm',
    )
    img.paste(floor_pic, (0, 600 + index_floor * 600), floor_pic)


async def draw_abyss_img(
    qid: Union[str, int],
    uid: str,
    schedule_type: str = '1',
) -> Union[bytes, str]:
    # 获取Cookies
    data = GsCookie()
    retcode = await data.get_cookie(uid)
    if retcode:
        return retcode
    # raw_data = data.raw_data
    raw_abyss_data = await data.get_spiral_abyss_data(uid, schedule_type)
    # print(raw_abyss_data)

    # 获取数据
    # if isinstance(raw_abyss_data, int):
    # return get_error(raw_abyss_data)
    # if raw_data:
    # char_data = raw_data['avatars']
    # else:
    # return '没有获取到角色数据'
    # char_temp = {}

    # 获取查询者数据
    # if floor:
    # floor = floor - 9
    # if floor < 0:
    # return '楼层不能小于9层!'
    # if len(raw_abyss_data['floors']) >= floor + 1:
    # floors_data = raw_abyss_data['floors'][floor]
    # else:
    # return '你还没有挑战该层!'
    # else:
    # if len(raw_abyss_data['floors']) == 0:
    # return '你还没有挑战本期深渊!\n可以使用[上期深渊]命令查询上期~'
    # floors_data = raw_abyss_data['floors'][-1]
    if raw_abyss_data['max_floor'] == '':
        return '你还没有挑战本期深渊!\n可以使用[上期深渊]命令查询上期~'
    # if floors_data['levels'][-1]['battles']:
    # is_unfull = False
    # else:
    # is_unfull = True

    # 获取背景图片各项参数
    based_w = 950
    # based_h = 900 if is_unfull else 2000
    based_h = 1200
    img = await get_color_bg(based_w, based_h, '_abyss')
    abyss_title = Image.open(TEXT_PATH / 'abyss_title.png')
    img.paste(abyss_title, (0, 0), abyss_title)

    # 获取头像
    _id = str(qid)
    if _id.startswith('http'):
        char_pic = await get_qq_avatar(avatar_url=_id)
    else:
        char_pic = await get_qq_avatar(qid=qid)
    char_pic = await draw_pic_with_ring(char_pic, 320)

    img.paste(char_pic, (320, 50), char_pic)

    # 解析数据
    # damage_rank = raw_abyss_data['damage_rank']
    # defeat_rank = raw_abyss_data['defeat_rank']
    # take_damage_rank = raw_abyss_data['take_damage_rank']
    # normal_skill_rank = raw_abyss_data['normal_skill_rank']
    # energy_skill_rank = raw_abyss_data['energy_skill_rank']
    # 挑战次数 raw_abyss_data['total_battle_times']

    # 绘制抬头
    img_draw = ImageDraw.Draw(img)
    img_draw.text((475, 415), f'UID {uid}', first_color, sr_font_36, 'mm')

    img_draw.text(
        (316, 480),
        f'最深抵达 - {raw_abyss_data["max_floor"]}',
        first_color,
        sr_font_32,
        'lm',
    )

    star_num_pic = Image.open(TEXT_PATH / 'star.png')
    img.paste(star_num_pic, (91, 485), star_num_pic)

    img_draw.text(
        (145, 505),
        f'X {raw_abyss_data["star_num"]}',
        first_color,
        sr_font_36,
        'lm',
    )

    img_draw.text(
        (316, 525),
        f'挑战次数 - {raw_abyss_data["battle_num"]}',
        first_color,
        sr_font_26,
        'lm',
    )

    task = []
    for index_floor, level in enumerate(raw_abyss_data['all_floor_detail']):
        floor_pic = Image.open(TEXT_PATH / 'abyss_floor.png')
        level_star = level['star_num']
        floor_name = level['name']
        round_num = level['round_num']
        time_array = level['node_1']['challenge_time']
        time_str = f"{time_array['year']}-{time_array['month']}-{time_array['day']}"
        time_str = f"{time_str} {time_array['hour']}:{time_array['minute']}"
        for index_part in [0, 1]:
            node_num = index_part + 1
            node = f'node_{node_num}'
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
                task.append(
                    _draw_abyss_card(
                        char,
                        0,  # type: ignore
                        floor_pic,
                        index_char,
                        index_part,
                    )
                )
        await asyncio.gather(*task)
        task.clear()
        task.append(
            _draw_floor_card(
                level_star,
                floor_pic,
                img,
                time_str,
                index_floor,
                floor_name,
                round_num,
            )
        )
        await asyncio.gather(*task)

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
    # img_draw.text(title_xy, _name, first_color, gs_font_20, 'lm')
    # img_draw.text(val_xy, _val, first_color, gs_font_26, 'lm')

    # 过滤数据
    # raw_abyss_data['floors'] = [
    # i for i in raw_abyss_data['floors'] if i['index'] >= 9
    # ]

    # 绘制缩略信息
    # for num in range(4):
    # omit_bg = Image.open(TEXT_PATH / 'abyss_omit.png')
    # omit_draw = ImageDraw.Draw(omit_bg)
    # omit_draw.text((56, 34), f'第{num+9}层', first_color, gs_font_32, 'lm')
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
