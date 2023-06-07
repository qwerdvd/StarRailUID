import asyncio
from pathlib import Path
from typing import Dict, List, Union, Optional

from PIL import Image, ImageDraw
from gsuid_core.utils.error_reply import get_error

from ..utils.mys_api import mys_api
from .utils import get_icon, wrap_list
from ..utils.image.convert import convert_img
from ..utils.fonts.starrail_fonts import sr_font_24, sr_font_30, sr_font_36
from ..sruid_utils.api.mys.models import Stats, RoleBasicInfo, AvatarListItem

TEXT_PATH = Path(__file__).parent / 'texture2D'

bg1 = Image.open(TEXT_PATH / 'bg1.png')
bg2 = Image.open(TEXT_PATH / 'bg2.png')
bg3 = Image.open(TEXT_PATH / 'bg3.png')
user_avatar = (
    Image.open(TEXT_PATH / "200101.png").resize((220, 220)).convert("RGBA")
)
char_bg_4 = Image.open(TEXT_PATH / 'rarity4_bg.png').convert("RGBA")
char_bg_5 = Image.open(TEXT_PATH / 'rarity5_bg.png').convert("RGBA")
circle = Image.open(TEXT_PATH / 'char_weapon_bg.png').convert("RGBA")

bg_color = (248, 248, 248)
white_color = (255, 255, 255)
color_color = (40, 18, 7)
first_color = (22, 8, 31)

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


async def get_role_img(uid: str) -> Union[bytes, str]:
    im = await draw_role_card(uid)
    return im


def _lv(level: int) -> str:
    return f"Lv.0{level}" if level < 10 else f"Lv.{level}"


async def _draw_card_1(
    sr_uid: str, role_basic_info: RoleBasicInfo, stats: Stats
) -> Image.Image:
    # 名称
    nickname = role_basic_info['nickname']

    # 基本状态
    active_days = stats['active_days']
    avater_num = stats['avatar_num']
    achievement_num = stats['achievement_num']
    chest_num = stats['chest_num']
    level = role_basic_info['level']

    # 忘却之庭
    abyss_process = stats['abyss_process']

    img_bg1 = bg1.copy()
    bg1_draw = ImageDraw.Draw(img_bg1)

    # 写Nickname
    bg1_draw.text(
        (400, 85), nickname, font=sr_font_36, fill=white_color, anchor='mm'
    )
    # 写UID
    bg1_draw.text(
        (400, 165),
        f"UID {sr_uid}",
        font=sr_font_30,
        fill=white_color,
        anchor='mm',
    )
    # 贴头像
    img_bg1.paste(user_avatar, (286, 213), mask=user_avatar)

    # 写基本信息
    bg1_draw.text(
        (143, 590),
        str(active_days),
        font=sr_font_36,
        fill=white_color,
        anchor='mm',
    )  # 活跃天数
    bg1_draw.text(
        (270, 590),
        str(avater_num),
        font=sr_font_36,
        fill=white_color,
        anchor='mm',
    )  # 解锁角色
    bg1_draw.text(
        (398, 590),
        str(achievement_num),
        font=sr_font_36,
        fill=white_color,
        anchor='mm',
    )  # 达成成就
    bg1_draw.text(
        (525, 590),
        str(chest_num),
        font=sr_font_36,
        fill=white_color,
        anchor='mm',
    )  # 战利品开启
    bg1_draw.text(
        (666, 590), str(level), font=sr_font_36, fill=white_color, anchor='mm'
    )  # 开拓等级

    # 画忘却之庭
    bg1_draw.text(
        (471, 722),
        abyss_process,
        font=sr_font_30,
        fill=first_color,
        anchor='mm',
    )

    return img_bg1


async def _draw_avatar_card(
    avatar: AvatarListItem, equips: Dict[int, Optional[str]]
) -> Image.Image:
    char_bg = (char_bg_4 if avatar['rarity'] == 4 else char_bg_5).copy()
    char_draw = ImageDraw.Draw(char_bg)
    char_icon = await get_icon(avatar['icon'])
    element_icon = elements[avatar['element']]

    char_bg.paste(char_icon, (4, 8), mask=char_icon)
    char_bg.paste(element_icon, (81, 10), mask=element_icon)

    if equip := equips[avatar['id']]:
        char_bg.paste(circle, (0, 0), mask=circle)
        equip_icon = (await get_icon(equip)).resize((48, 48))
        char_bg.paste(equip_icon, (9, 80), mask=equip_icon)

    char_draw.text(
        (60, 146),
        _lv(avatar['level']),
        font=sr_font_24,
        fill=color_color,
        anchor='mm',
    )
    return char_bg


async def _draw_line(
    avatars: List[AvatarListItem], equips: Dict[int, Optional[str]]
) -> Image.Image:
    line = bg2.copy()
    x = 70
    char_bgs: List[Image.Image] = await asyncio.gather(
        *[_draw_avatar_card(avatar, equips) for avatar in avatars]
    )
    for char_bg in char_bgs:
        line.paste(char_bg, (x, 0), mask=char_bg)
        x += 135
    return line


async def _draw_card_2(
    avatars: List[AvatarListItem], equips: Dict[int, Optional[str]]
) -> Image.Image:
    # 角色部分 每五个一组
    lines = await asyncio.gather(
        *[
            _draw_line(five_avatars, equips)
            for five_avatars in wrap_list(avatars, 5)
        ]
    )
    img_card_2 = Image.new("RGBA", (800, len(lines) * 200))

    y = 0
    for line in lines:
        img_card_2.paste(line, (0, y), mask=line)
        y += 200
    return img_card_2


async def draw_role_card(sr_uid: str) -> Union[bytes, str]:
    role_basic_info = await mys_api.get_role_basic_info(sr_uid)
    role_index = await mys_api.get_role_index(sr_uid)

    if isinstance(role_index, int):
        return get_error(role_index)
    if isinstance(role_basic_info, int):
        role_basic_info = {}
        role_basic_info['nickname'] = "开拓者"
        role_basic_info['level'] = 0
        # return get_error(role_basic_info)

    stats = role_index['stats']
    avatars = role_index['avatar_list']

    detail = await mys_api.get_avatar_info(sr_uid, avatars[0]['id'])
    if isinstance(detail, int):
        return get_error(detail)

    # 角色武器
    details = detail['avatar_list']
    equips: Dict[int, Optional[str]] = {}
    for detail in details:
        equip = detail['equip']
        equips[detail['id']] = equip['icon'] if equip is not None else None

    # 绘制总图
    img1, img2 = await asyncio.gather(
        *[
            _draw_card_1(sr_uid, role_basic_info, stats),
            _draw_card_2(avatars, equips),
        ]
    )
    img2: Image.Image
    height = img2.size[1]
    img = Image.new("RGBA", (800, 880 + height), bg_color)
    img.paste(img1, (0, 0))
    img.paste(img2, (0, 810))
    img.paste(bg3, (0, height + 810))
    return await convert_img(img)
