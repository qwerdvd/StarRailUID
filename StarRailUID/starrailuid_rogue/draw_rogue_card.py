import math
from pathlib import Path
from typing import List, Union, Optional

from PIL import Image, ImageDraw
from gsuid_core.logger import logger
from gsuid_core.utils.error_reply import get_error

from .utils import get_icon
from ..utils.convert import GsCookie
from ..utils.image.convert import convert_img
from ..utils.image.image_tools import get_qq_avatar, draw_pic_with_ring
from ..sruid_utils.api.mys.models import (
    RogueAvatar,
    RogueMiracles,
    RogueBuffitems,
)
from ..utils.fonts.starrail_fonts import (
    sr_font_22,
    sr_font_28,
    sr_font_34,
    sr_font_42,
)

TEXT_PATH = Path(__file__).parent / 'texture2D'
white_color = (255, 255, 255)
gray_color = (175, 175, 175)
img_bg = Image.open(TEXT_PATH / 'bg.jpg')
level_cover = Image.open(TEXT_PATH / 'level_cover.png').convert("RGBA")
char_bg_4 = Image.open(TEXT_PATH / 'char4_bg.png').convert("RGBA")
char_bg_5 = Image.open(TEXT_PATH / 'char5_bg.png').convert("RGBA")
content_center = Image.open(TEXT_PATH / 'center.png').convert("RGBA")

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

progresslist = {
    1: '第一世界',
    2: '第二世界',
    3: '第三世界',
    4: '第四世界',
    5: '第五世界',
    6: '第六世界',
    7: '第七世界',
}

difficultylist = {
    1: 'Ⅰ',
    2: 'Ⅱ',
    3: 'Ⅲ',
    4: 'Ⅳ',
    5: 'Ⅴ',
    6: 'Ⅵ',
}

bufflist = {
    120: '存护',
    121: '记忆',
    122: '虚无',
    123: '丰饶',
    124: '巡猎',
    125: '毁灭',
    126: '欢愉',
}


async def get_abyss_star_pic(star: int) -> Image.Image:
    star_pic = Image.open(TEXT_PATH / f'star{star}.png')
    return star_pic


async def _draw_rogue_buff(
    buffs: List[RogueBuffitems],
    buff_icon: str,
    buff_name: str,
    floor_pic: Image.Image,
    buff_height: int,
):
    draw_height = 0
    floor_pic_draw = ImageDraw.Draw(floor_pic)
    buff_icon_img = Image.open(TEXT_PATH / f'{buff_icon}.png')
    buff_icon_img = buff_icon_img.resize((40, 40))
    floor_pic.paste(buff_icon_img, (95, 400 + buff_height), buff_icon_img)
    floor_pic_draw.text(
        (140, 425 + buff_height),
        f'{buff_name}:',
        font=sr_font_28,
        fill=gray_color,
        anchor='lm',
    )
    draw_height = draw_height + 40
    buff_num = len(buffs)
    need_middle = math.ceil(buff_num / 3)
    draw_height = draw_height + need_middle * 55
    zb_list = []
    for m in range(need_middle):
        for n in range(3):
            zb_list.append([m, n])
    jishu = 0
    for item in buffs:
        if item['is_evoluted'] is True:
            is_evoluted = 1
        else:
            is_evoluted = 0
        buff_bg = Image.open(
            TEXT_PATH / f'zhufu_{item["rank"]}_{is_evoluted}.png'
        )
        buff_bg = buff_bg.resize((233, 35))
        z_left = 90 + 240 * zb_list[jishu][1]
        z_top = buff_height + 450 + 55 * zb_list[jishu][0]
        jishu = jishu + 1
        floor_pic.paste(buff_bg, (z_left, z_top), mask=buff_bg)
        floor_pic_draw.text(
            (z_left + 115, z_top + 18),
            item['name'],
            font=sr_font_22,
            fill=white_color,
            anchor='mm',
        )
    return draw_height


async def _draw_rogue_miracles(
    miracles: List[RogueMiracles],
    floor_pic: Image.Image,
    buff_height: int,
):
    miracles_num = len(miracles)
    need_middle = math.ceil(miracles_num / 8)
    zb_list = []
    for m in range(need_middle):
        for n in range(8):
            zb_list.append([m, n])
    jishu = 0
    for miracle in miracles:
        miracles_icon = (await get_icon(miracle['icon'])).resize((80, 80))
        z_left = 90 + 90 * zb_list[jishu][1]
        z_top = buff_height + 470 + 90 * zb_list[jishu][0]
        jishu = jishu + 1
        floor_pic.paste(miracles_icon, (z_left, z_top), mask=miracles_icon)


async def _draw_rogue_card(
    char: RogueAvatar,
    talent_num: str,
    floor_pic: Image.Image,
    index_char: int,
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
        (75 + 185 * index_char, 130),
        char_bg,
    )


async def draw_rogue_img(
    qid: Union[str, int],
    uid: str,
    floor: Optional[int] = None,
    schedule_type: str = '3',
) -> Union[bytes, str]:
    # 获取Cookies
    data = GsCookie()
    # retcode = await data.get_cookie(uid)
    # if retcode:
    # return retcode
    # raw_data = data.raw_data
    raw_rogue_data = await data.get_rogue_data(uid, '3')
    # print(raw_rogue_data)

    if isinstance(raw_rogue_data, int):
        return get_error(raw_rogue_data)

    # 获取数据
    # if raw_data:
    # char_data = raw_data['avatars']
    # else:
    # return '没有获取到角色数据'
    # char_temp = {}

    # 计算背景图尺寸
    if schedule_type == '3':
        rogue_detail = raw_rogue_data['current_record']['records']
    else:
        rogue_detail = raw_rogue_data['last_record']['records']

    # 记录打的宇宙列表
    detail_list = []
    based_h = 657
    for index_floor, detail in enumerate(rogue_detail):
        # 100+70+170
        # 头+底+角色
        detail_h = 340
        progress = detail['progress']
        detail_list.append(progress)
        # 祝福
        if len(detail['base_type_list']) > 0:
            buff_h = 60
            for buff in detail['buffs']:
                buff_h = buff_h + 50
                buff_num = len(buff['items'])
                buff_h = buff_h + math.ceil(buff_num / 3) * 55
        else:
            buff_h = 0
        detail_h = detail_h + buff_h

        # 奇物
        if len(detail['miracles']) > 0:
            miracles_h = 60
            miracles_num = len(detail['miracles'])
            miracles_h = miracles_h + math.ceil(miracles_num / 8) * 90
        else:
            miracles_h = 0
        detail_h = detail_h + miracles_h
        rogue_detail[index_floor]['detail_h'] = detail_h
        rogue_detail[index_floor]['start_h'] = based_h
        if floor:
            if progress == floor:
                detail_h = detail_h
            else:
                detail_h = 0
        based_h = based_h + detail_h
    print(based_h)
    # 获取查询者数据
    if floor:
        if floor > 6:
            return '世界不能大于第六世界!'
        if floor not in detail_list:
            return '你还没有挑战该模拟宇宙!'
    else:
        if raw_rogue_data['current_record']['basic']['finish_cnt'] == 0:
            return '你还没有挑战本期模拟宇宙!\n可以使用[sr上期模拟宇宙]命令查询上期~'

    # 获取背景图片各项参数
    based_w = 900
    img = Image.new("RGB", (based_w, based_h), (10, 18, 49))
    img.paste(img_bg, (0, 0))
    # img = img.crop((0, 0, based_w, based_h))
    rogue_title = Image.open(TEXT_PATH / 'head.png')
    img.paste(rogue_title, (0, 0), rogue_title)

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
    rogue_data = Image.open(TEXT_PATH / 'data.png')
    img.paste(rogue_data, (0, 500), rogue_data)

    # 技能树激活
    img_draw.text(
        (165, 569),
        f'{raw_rogue_data["basic_info"]["unlocked_skill_points"]}',
        white_color,
        sr_font_42,
        'mm',
    )
    img_draw.text(
        (165, 615),
        '已激活技能树',
        gray_color,
        sr_font_28,
        'mm',
    )

    # 奇物解锁
    img_draw.text(
        (450, 569),
        f'{raw_rogue_data["basic_info"]["unlocked_miracle_num"]}',
        white_color,
        sr_font_42,
        'mm',
    )
    img_draw.text(
        (450, 615),
        '已解锁奇物',
        gray_color,
        sr_font_28,
        'mm',
    )

    # 祝福解锁
    img_draw.text(
        (730, 569),
        f'{raw_rogue_data["basic_info"]["unlocked_buff_num"]}',
        white_color,
        sr_font_42,
        'mm',
    )
    img_draw.text(
        (730, 615),
        '已解锁祝福',
        gray_color,
        sr_font_28,
        'mm',
    )

    for index_floor, detail in enumerate(rogue_detail):
        if floor:
            if floor == detail['progress']:
                index_floor = 0
            else:
                continue

        floor_pic = Image.open(TEXT_PATH / 'detail_bg.png').convert("RGBA")
        floor_pic = floor_pic.resize((900, detail['detail_h']))

        floor_top_pic = Image.open(TEXT_PATH / 'floor_bg_top.png').convert(
            "RGBA"
        )
        floor_pic.paste(floor_top_pic, (0, 0), floor_top_pic)

        floor_center_pic = Image.open(
            TEXT_PATH / 'floor_bg_center.png'
        ).convert("RGBA")
        floor_center_pic = floor_center_pic.resize(
            (900, detail['detail_h'] - 170)
        )
        floor_pic.paste(floor_center_pic, (0, 100), floor_center_pic)

        floor_bot_pic = Image.open(TEXT_PATH / 'floor_bg_bot.png').convert(
            "RGBA"
        )
        floor_pic.paste(
            floor_bot_pic, (0, detail['detail_h'] - 70), floor_bot_pic
        )

        floor_name = progresslist[detail['progress']]
        difficulty_name = difficultylist[detail['difficulty']]

        time_array = detail['finish_time']
        time_str = f"{time_array['year']}-{time_array['month']}"
        time_str = f"{time_str}-{time_array['day']}"
        time_str = f"{time_str} {time_array['hour']}:{time_array['minute']}"
        floor_pic_draw = ImageDraw.Draw(floor_pic)
        floor_pic_draw.text(
            (450, 60),
            f'{floor_name} {difficulty_name}',
            white_color,
            sr_font_42,
            'mm',
        )
        floor_pic_draw.text(
            (93, 120),
            f'挑战时间：{time_str}',
            gray_color,
            sr_font_22,
            'lm',
        )
        floor_pic_draw.text(
            (800, 120),
            f'当前积分：{detail["score"]}',
            gray_color,
            sr_font_22,
            'rm',
        )

        # 角色
        for index_char, char in enumerate(detail['final_lineup']):
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
            await _draw_rogue_card(
                char,
                0,  # type: ignore
                floor_pic,
                index_char,
            )

        # 祝福
        buff_height = 0
        if len(detail['base_type_list']) > 0:
            floor_pic_draw.text(
                (93, 370),
                '获得祝福',
                white_color,
                sr_font_34,
                'lm',
            )
            floor_pic.paste(content_center, (0, 390), content_center)
            for buff in detail['buffs']:
                buff_icon = bufflist[buff['base_type']['id']]
                buff_name = buff['base_type']['name']
                buffs = buff['items']
                draw_height = await _draw_rogue_buff(
                    buffs,
                    buff_icon,
                    buff_name,
                    floor_pic,
                    buff_height,
                )
                buff_height = buff_height + draw_height

        # 奇物
        if len(detail['miracles']) > 0:
            floor_pic_draw.text(
                (93, 370 + buff_height + 60),
                '获得奇物',
                white_color,
                sr_font_34,
                'lm',
            )
            floor_pic.paste(
                content_center, (0, 370 + buff_height + 80), content_center
            )
            await _draw_rogue_miracles(
                detail['miracles'],
                floor_pic,
                buff_height,
            )

        img.paste(floor_pic, (0, detail['start_h']), floor_pic)
        # await _draw_floor_card(
        # level_star,
        # floor_pic,
        # img,
        # index_floor,
        # floor_name,
        # round_num,
        # )

    res = await convert_img(img)
    logger.info('[查询模拟宇宙]绘图已完成,等待发送!')
    return res
