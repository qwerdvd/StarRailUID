import asyncio
from pathlib import Path
from typing import List, Union, Optional

from PIL import Image, ImageDraw
from gsuid_core.utils.api.enka.models import EnkaData

from .to_data import api_to_dict
from ..utils.image.convert import convert_img
from ..utils.fonts.first_world import fw_font_28
from ..utils.map.SR_MAP_PATH import avatarId2Name
from ..utils.map.name_covert import avatar_id_to_char_star
from ..utils.fonts.starrail_fonts import sr_font_24, sr_font_30, sr_font_58
from ..utils.resource.RESOURCE_PATH import CHAR_ICON_PATH, CHAR_PREVIEW_PATH

half_color = (255, 255, 255, 120)
first_color = (29, 29, 29)
second_color = (67, 61, 56)
white_color = (247, 247, 247)
gray_color = (175, 175, 175)

# MAP_PATH = Path(__file__).parent / 'map'
TEXT_PATH = Path(__file__).parent / 'texture2D'
char_mask = Image.open(TEXT_PATH / 'char_mask.png')
char_bg_mask = Image.open(TEXT_PATH / 'char_bg_mask.png')
tag = Image.open(TEXT_PATH / 'tag.png')
footbar = Image.open(TEXT_PATH / 'footbar.png')
pic_500 = Image.open(TEXT_PATH / '500.png')


async def api_to_card(
    uid: str, enka_data: Optional[EnkaData] = None
) -> Union[str, bytes]:
    char_data_list = await api_to_dict(uid, enka_data)
    print(char_data_list)
    if isinstance(char_data_list, str):
        if ('服务器正在维护或者关闭中' in char_data_list) or ('网络不太稳定' in char_data_list):
            return await convert_img(pic_500)
        else:
            return await convert_img(pic_500)
    else:
        if char_data_list == []:
            return await convert_img(pic_500)

    img = await draw_enka_card(uid=uid, char_list=char_data_list, showfrom=1)
    return img


async def draw_enka_card(
    uid: str, char_list: Optional[List] = None, showfrom: int = 0
):
    char_data_list = []
    if 1102 in char_list:
        char_list.remove(1102)
        char_list.append(1102)
    for char in char_list:
        avatarName = avatarId2Name[str(char)]
        char_data_list.append(
            {'avatarName': avatarName, 'avatarId': str(char)}
        )
    if showfrom == 0:
        line1 = f'展柜内有 {len(char_data_list)} 个角色!'
    else:
        if char_data_list is None:
            return await convert_img(
                Image.new('RGBA', (0, 1), (255, 255, 255))
            )
        else:
            line1 = f'UID {str(uid)} 刷新成功'
    # print(char_list)
    line2 = f'可以使用 sr查询{char_data_list[0]["avatarName"]} 查询详情角色面板'
    char_num = len(char_data_list)
    if char_num <= 4:
        based_w, based_h = 1380, 926
        show_type = 1
    else:
        show_type = 0
        based_w, based_h = 1380, 660 + (char_num - 5) // 5 * 110
        if (char_num - 5) % 5 >= 4:
            based_h += 110

    img = Image.open(TEXT_PATH / 'shin-w.jpg').resize((based_w, based_h))
    img.paste(tag, (0, 0), tag)

    img_draw = ImageDraw.Draw(img, 'RGBA')

    # 写底层文字
    img_draw.text(
        (690, based_h - 16),
        '--Created by qwerdvd-Designed By Wuyi-Thank for mihomo.me--',
        (0, 0, 255),
        fw_font_28,
        'mm',
    )

    img_draw.text(
        (225, 120),
        line1,
        white_color,
        sr_font_58,
        'lm',
    )
    img_draw.text(
        (225, 175),
        line2,
        gray_color,
        sr_font_24,
        'lm',
    )
    tasks = []
    for index, char_data in enumerate(char_data_list):
        if show_type == 0:
            tasks.append(draw_enka_char(index, img, char_data))
        else:
            tasks.append(draw_mihomo_char(index, img, char_data))
    await asyncio.gather(*tasks)
    img = await convert_img(img)
    return img


async def draw_mihomo_char(index: int, img: Image.Image, char_data: dict):
    char_id = char_data['avatarId']
    char_name = char_data['avatarName']
    char_star = await avatar_id_to_char_star(str(char_id))
    char_card = Image.open(TEXT_PATH / f'char{char_star}_bg.png')
    char_temp = Image.new('RGBA', (300, 650))
    char_img = (
        Image.open(str(CHAR_PREVIEW_PATH / f'{char_id}.png'))
        .convert('RGBA')
        .resize((449, 615))
    )
    if char_name == '希儿':
        char_img = char_img.resize((449, 650))
        char_img = char_img.crop((135, 0, 379, 457))
        char_temp.paste(char_img, (32, 98), char_img)
    else:
        char_img = char_img.crop((103, 0, 347, 517))
        char_temp.paste(char_img, (32, 38), char_img)
    char_card.paste(char_temp, (0, 0), char_bg_mask)

    img_draw = ImageDraw.Draw(char_card, 'RGBA')
    img_draw.text(
        (150, 585),
        char_name,
        white_color,
        sr_font_30,
        'mm',
    )
    x = 42 + index * 325
    img.paste(char_card, (x, 199), char_card)


async def draw_enka_char(index: int, img: Image.Image, char_data: dict):
    char_id = char_data['avatarId']
    char_star = await avatar_id_to_char_star(str(char_id))
    char_card = Image.open(TEXT_PATH / f'char_card_{char_star}.png')
    char_img = (
        Image.open(str(CHAR_ICON_PATH / f'{char_id}.png'))
        .convert('RGBA')
        .resize((204, 204))
    )
    char_temp = Image.new('RGBA', (220, 220))
    char_temp.paste(char_img, (8, 8), char_img)
    char_card.paste(char_temp, (0, 0), char_mask)
    if index <= 7:
        if img.size[0] <= 1100:
            x = 60 + (index % 4) * 220
        else:
            x = 160 + (index % 4) * 220
        img.paste(
            char_card,
            (x, 187 + (index // 4) * 220),
            char_card,
        )
    elif index <= 12:
        img.paste(
            char_card,
            (50 + (index % 8) * 220, 296),
            char_card,
        )
    else:
        _i = index - 13
        x, y = 50 + (_i % 9) * 220, 512 + (_i // 9) * 220
        if _i % 9 >= 5:
            y += 110
            x = 160 + ((_i - 5) % 9) * 220
        img.paste(
            char_card,
            (x, y),
            char_card,
        )
