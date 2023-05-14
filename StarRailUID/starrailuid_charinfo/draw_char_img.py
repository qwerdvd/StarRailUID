import re
import json
import math
from pathlib import Path
from typing import Dict, Union, Optional

from mpmath import mp, nstr
from PIL import Image, ImageDraw
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import draw_text_by_line

from .mono.Character import Character
from ..utils.error_reply import CHAR_HINT
from ..utils.map.SR_MAP_PATH import RelicId2Rarity
from ..utils.excel.read_excel import light_cone_ranks
from ..utils.map.name_covert import alias_to_char_name
from ..utils.fonts.first_world import fw_font_28, fw_font_120
from ..utils.resource.RESOURCE_PATH import (
    RELIC_PATH,
    SKILL_PATH,
    PLAYER_PATH,
    WEAPON_PATH,
    CHAR_PORTRAIT,
)
from ..utils.fonts.starrail_fonts import (
    sr_font_20,
    sr_font_23,
    sr_font_24,
    sr_font_26,
    sr_font_28,
    sr_font_34,
    sr_font_38,
)

mp.dps = 14

TEXT_PATH = Path(__file__).parent / 'texture2D'

bg_img = Image.open(TEXT_PATH / "bg.png")
white_color = (213, 213, 213)

NUM_MAP = {0: '零', 1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七'}

RANK_MAP = {
    1: '_rank1.png',
    2: '_rank2.png',
    3: '_ultimate.png',
    4: '_rank4.png',
    5: '_skill.png',
    6: '_rank6.png',
}

skill_type_map = {
    'Normal': ('普攻', 'basic_atk'),
    'BPSkill': ('战技', 'skill'),
    'Ultra': ('终结技', 'ultimate'),
    '': ('天赋', 'talent'),
    'MazeNormal': 'dev_连携',
    'Maze': ('秘技', 'technique'),
}


RELIC_POS = {
    '1': (26, 1162),
    '2': (367, 1162),
    '3': (700, 1162),
    '4': (26, 1593),
    '5': (367, 1593),
    '6': (700, 1593),
}


async def draw_char_info_img(raw_mes: str, sr_uid: str, url: Optional[str]):
    # 获取角色名
    char_name = ' '.join(re.findall('[\u4e00-\u9fa5]+', raw_mes))

    char_data = await get_char_data(sr_uid, char_name)
    if isinstance(char_data, str):
        return char_data
    char = await cal_char_info(char_data)

    # 放角色立绘
    char_info = bg_img.copy()
    char_img = Image.open(CHAR_PORTRAIT / f'{char.char_id}.png').resize(
        (1050, 1050)
    )
    char_info.paste(char_img, (-220, -130), char_img)

    # 放属性图标
    attr_img = Image.open(TEXT_PATH / f'IconAttribute{char.char_element}.png')
    char_info.paste(attr_img, (540, 166), attr_img)

    # 放角色名
    char_img_draw = ImageDraw.Draw(char_info)
    char_img_draw.text(
        (620, 207), char.char_name, (255, 255, 255), sr_font_38, 'lm'
    )
    char_name_len = sr_font_38.getsize(char.char_name)[0]

    # 放等级
    char_img_draw.text(
        (620 + char_name_len + 50, 212),
        f'LV.{str(char.char_level)}',
        white_color,
        sr_font_24,
        'mm',
    )

    # 放星级
    rarity_img = Image.open(
        TEXT_PATH / f'LightCore_Rarity{char.char_rarity}.png'
    ).resize((306, 72))
    char_info.paste(rarity_img, (490, 233), rarity_img)

    # 放命座
    rank_img = Image.open(TEXT_PATH / 'ImgNewBg.png')
    rank_img_draw = ImageDraw.Draw(rank_img)
    rank_img_draw.text(
        (70, 44), f'{NUM_MAP[char.char_rank]}命', white_color, sr_font_28, 'mm'
    )
    char_info.paste(rank_img, (722, 225), rank_img)

    # 放uid
    char_img_draw.text(
        (995, 715),
        f'uid {sr_uid}',
        white_color,
        fw_font_28,
        'rm',
        stroke_width=1,
    )

    # 放属性列表
    attr_bg = Image.open(TEXT_PATH / 'attr_bg.png')
    attr_bg_draw = ImageDraw.Draw(attr_bg)
    # 生命值
    hp = mp.mpf(char.base_attributes.get('hp'))
    add_hp = mp.mpf(
        char.add_attr['HPDelta'] if char.add_attr.get('HPDelta') else 0
    ) + hp * mp.mpf(
        char.add_attr['HPAddedRatio']
        if char.add_attr.get('HPAddedRatio')
        else 0
    )
    hp = int(mp.floor(hp))
    add_hp = int(mp.floor(add_hp))
    attr_bg_draw.text(
        (413, 31), f'{hp + add_hp}', white_color, sr_font_26, 'rm'
    )
    attr_bg_draw.text(
        (428, 31),
        f'(+{str(round(add_hp))})',
        (95, 251, 80),
        sr_font_26,
        anchor='lm',
    )
    # 攻击力
    attack = mp.mpf(char.base_attributes['attack'])
    add_attack = mp.mpf(
        char.add_attr['AttackDelta'] if char.add_attr.get('AttackDelta') else 0
    ) + attack * mp.mpf(
        char.add_attr['AttackAddedRatio']
        if char.add_attr.get('AttackAddedRatio')
        else 0
    )
    atk = int(mp.floor(attack))
    add_attack = int(mp.floor(add_attack))
    attr_bg_draw.text(
        (413, 31 + 48),
        f'{atk + add_attack}',
        white_color,
        sr_font_26,
        'rm',
    )
    attr_bg_draw.text(
        (428, 31 + 48),
        f'(+{str(round(add_attack))})',
        (95, 251, 80),
        sr_font_26,
        anchor='lm',
    )
    # 防御力
    defence = mp.mpf(char.base_attributes['defence'])
    add_defence = mp.mpf(
        char.add_attr.get('DefenceDelta')
        if char.add_attr.get('DefenceDelta')
        else 0
    ) + defence * mp.mpf(
        char.add_attr.get('DefenceAddedRatio')
        if char.add_attr.get('DefenceAddedRatio')
        else 0
    )
    defence = int(mp.floor(defence))
    add_defence = int(mp.floor(add_defence))
    attr_bg_draw.text(
        (413, 31 + 48 * 2),
        f'{defence + add_defence}',
        white_color,
        sr_font_26,
        'rm',
    )
    attr_bg_draw.text(
        (428, 31 + 48 * 2),
        f'(+{str(round(add_defence))})',
        (95, 251, 80),
        sr_font_26,
        anchor='lm',
    )
    # 速度
    speed = mp.mpf(char.base_attributes['speed'])
    add_speed = mp.mpf(
        char.add_attr['SpeedDelta'] if char.add_attr.get('SpeedDelta') else 0
    )
    speed = int(mp.floor(speed))
    add_speed = int(mp.floor(add_speed))
    attr_bg_draw.text(
        (413, 31 + 48 * 3),
        f'{speed + add_speed}',
        white_color,
        sr_font_26,
        'rm',
    )
    attr_bg_draw.text(
        (428, 31 + 48 * 3),
        f'(+{str(round(add_speed))})',
        (95, 251, 80),
        sr_font_26,
        anchor='lm',
    )
    # 暴击率
    critical_chance = mp.mpf(char.base_attributes['CriticalChance'])
    critical_chance_base = mp.mpf(
        char.add_attr['CriticalChanceBase']
        if char.add_attr.get('CriticalChanceBase')
        else 0
    )
    critical_chance = (critical_chance + critical_chance_base) * 100
    critical_chance = nstr(critical_chance, 3)
    attr_bg_draw.text(
        (500, 31 + 48 * 4),
        f'{critical_chance}%',
        white_color,
        sr_font_26,
        'rm',
    )
    # 暴击伤害
    critical_damage = mp.mpf(char.base_attributes['CriticalDamage'])
    critical_damage_base = mp.mpf(
        char.add_attr['CriticalDamageBase']
        if char.add_attr.get('CriticalDamageBase')
        else 0
    )
    critical_damage = (critical_damage + critical_damage_base) * 100
    critical_damage = nstr(critical_damage, 4)
    attr_bg_draw.text(
        (500, 31 + 48 * 5),
        f'{critical_damage}%',
        white_color,
        sr_font_26,
        'rm',
    )
    # 效果命中
    status_probability_base = (
        mp.mpf(
            char.add_attr.get('StatusProbabilityBase')
            if char.add_attr.get('StatusProbabilityBase')
            else 0
        )
        * 100
    )
    status_probability = nstr(status_probability_base, 3)
    attr_bg_draw.text(
        (500, 31 + 48 * 6),
        f'{status_probability}%',
        white_color,
        sr_font_26,
        'rm',
    )
    # 效果抵抗
    status_resistance_base = (
        mp.mpf(
            char.add_attr['StatusResistanceBase']
            if char.add_attr.get('StatusResistanceBase')
            else 0
        )
        * 100
    )
    status_resistance = nstr(status_resistance_base, 3)
    attr_bg_draw.text(
        (500, 31 + 48 * 7),
        f'{status_resistance}%',
        white_color,
        sr_font_26,
        'rm',
    )
    char_info.paste(attr_bg, (475, 300), attr_bg)

    # 命座
    for rank in range(0, 6):
        rank_bg = Image.open(TEXT_PATH / 'mz_bg.png')
        rank_no_bg = Image.open(TEXT_PATH / 'mz_no_bg.png')
        if rank < char.char_rank:
            rank_img = Image.open(
                SKILL_PATH / f'{char.char_id}{RANK_MAP[rank + 1]}'
            ).resize((50, 50))
            rank_bg.paste(rank_img, (19, 19), rank_img)
            char_info.paste(rank_bg, (20 + rank * 80, 630), rank_bg)
        else:
            rank_img = (
                Image.open(SKILL_PATH / f'{char.char_id}{RANK_MAP[rank + 1]}')
                .resize((50, 50))
                .convert("RGBA")
            )
            rank_img.putalpha(
                rank_img.getchannel('A').point(
                    lambda x: round(x * 0.45) if x > 0 else 0
                )
            )
            rank_no_bg.paste(rank_img, (19, 19), rank_img)
            char_info.paste(rank_no_bg, (20 + rank * 80, 630), rank_no_bg)

    # 技能
    skill_bg = Image.open(TEXT_PATH / 'skill_bg.png')
    i = 0
    for skill in char.char_skill:
        skill_attr_img = Image.open(TEXT_PATH / f'skill_attr{i + 1}.png')
        skill_panel_img = Image.open(TEXT_PATH / 'skill_panel.png')
        skill_img = Image.open(
            SKILL_PATH / f'{char.char_id}_'
            f'{skill_type_map[skill["skillAttackType"]][1]}.png'
        ).resize((55, 55))
        skill_panel_img.paste(skill_img, (18, 15), skill_img)
        skill_panel_img.paste(skill_attr_img, (80, 10), skill_attr_img)
        skill_panel_img_draw = ImageDraw.Draw(skill_panel_img)
        skill_panel_img_draw.text(
            (108, 25),
            f'{skill_type_map[skill["skillAttackType"]][0]}',
            white_color,
            sr_font_26,
            'lm',
        )
        skill_panel_img_draw.text(
            (89, 55),
            f'Lv.{skill["skillLevel"]}',
            white_color,
            sr_font_26,
            'lm',
        )
        skill_panel_img_draw.text(
            (75, 90),
            f'{skill["skillName"]}',
            (105, 105, 105),
            sr_font_20,
            'mm',
        )
        skill_bg.paste(skill_panel_img, (50 + 187 * i, 35), skill_panel_img)
        i += 1
    char_info.paste(skill_bg, (0, 710), skill_bg)

    # 武器
    if char.equipment != {}:
        weapon_bg = Image.open(TEXT_PATH / 'weapon_bg.png')
        weapon_id = char.equipment['equipmentID']
        weapon_img = Image.open(WEAPON_PATH / f'{weapon_id}.png').resize(
            (270, 240)
        )
        weapon_bg.paste(weapon_img, (20, 50), weapon_img)
        weapon_bg_draw = ImageDraw.Draw(weapon_bg)
        weapon_bg_draw.text(
            (345, 47),
            f'{char.equipment["equipmentName"]}',
            white_color,
            sr_font_34,
            'lm',
        )
        weapon_name_len = sr_font_34.getsize(char.equipment["equipmentName"])[
            0
        ]
        # 放阶
        rank_img = Image.open(TEXT_PATH / 'ImgNewBg.png')
        rank_img_draw = ImageDraw.Draw(rank_img)
        rank_img_draw.text(
            (70, 44),
            f'{NUM_MAP[char.equipment["equipmentRank"]]}阶',
            white_color,
            sr_font_28,
            'mm',
        )
        weapon_bg.paste(rank_img, (weapon_name_len + 330, 2), rank_img)

        rarity_img = Image.open(
            TEXT_PATH
            / f'LightCore_Rarity{char.equipment["equipmentRarity"]}.png'
        ).resize((306, 72))
        weapon_bg.paste(rarity_img, (223, 55), rarity_img)
        weapon_bg_draw.text(
            (498, 90),
            f'Lv.{char.equipment["equipmentLevel"]}',
            white_color,
            sr_font_28,
            'mm',
        )

        # 武器技能
        desc = light_cone_ranks[str(char.equipment['equipmentID'])]['desc']
        desc_params = light_cone_ranks[str(char.equipment['equipmentID'])][
            'params'
        ][char.equipment['equipmentRank'] - 1]
        for i in range(0, len(desc_params)):
            temp = math.floor(desc_params[i] * 1000) / 10
            desc = desc.replace(f'#{i + 1}[i]%', f'{str(temp)}%')
        for i in range(0, len(desc_params)):
            desc = desc.replace(f'#{i + 1}[i]', str(desc_params[i]))
        draw_text_by_line(
            weapon_bg, (286, 115), desc, sr_font_24, '#F9F9F9', 372
        )
        char_info.paste(weapon_bg, (-10, 870), weapon_bg)
    else:
        char_img_draw.text(
            (525, 1005),
            'No light cone!',
            white_color,
            fw_font_120,
            'mm',
        )

    # 遗器
    if char.char_relic:
        weapon_rank_bg = Image.open(TEXT_PATH / 'rank_bg.png')
        char_info.paste(weapon_rank_bg, (690, 880), weapon_rank_bg)
        relic_score = 0

        for relic in char.char_relic:
            rarity = RelicId2Rarity[str(relic["relicId"])]
            relic_img = Image.open(TEXT_PATH / f'yq_bg{rarity}.png')
            if str(relic["SetId"])[0] == '3':
                relic_piece_img = Image.open(
                    RELIC_PATH / f'{relic["SetId"]}_{relic["Type"] - 5}.png'
                )
            else:
                relic_piece_img = Image.open(
                    RELIC_PATH / f'{relic["SetId"]}_{relic["Type"] - 1}.png'
                )
            relic_piece_new_img = relic_piece_img.resize(
                (105, 105), Image.Resampling.LANCZOS
            ).convert("RGBA")
            relic_img.paste(
                relic_piece_new_img, (200, 90), relic_piece_new_img
            )
            rarity_img = Image.open(
                TEXT_PATH / f'LightCore_Rarity'
                f'{RelicId2Rarity[str(relic["relicId"])]}.png'
            ).resize((200, 48))
            relic_img.paste(rarity_img, (-10, 80), rarity_img)
            relic_img_draw = ImageDraw.Draw(relic_img)
            if len(relic['relicName']) <= 5:
                main_name = relic['relicName']
            else:
                main_name = relic['relicName'][:2] + relic['relicName'][4:]
            relic_img_draw.text(
                (30, 70),
                main_name,
                (255, 255, 255),
                sr_font_34,
                anchor='lm',
            )

            # 主属性
            main_value = mp.mpf(relic['MainAffix']['Value'])
            main_name: str = relic['MainAffix']['Name']
            main_level: int = relic['Level']

            if main_name in ['攻击力', '生命值', '防御力', '速度']:
                mainValueStr = nstr(main_value, 3)
            else:
                mainValueStr = str(math.floor(main_value * 1000) / 10) + '%'

            mainNameNew = (
                main_name.replace('百分比', '')
                .replace('伤害加成', '伤加成')
                .replace('属性伤害', '伤害')
            )

            relic_img_draw.text(
                (35, 150),
                mainNameNew,
                (255, 255, 255),
                sr_font_28,
                anchor='lm',
            )
            relic_img_draw.text(
                (35, 195),
                '+{}'.format(mainValueStr),
                (255, 255, 255),
                sr_font_28,
                anchor='lm',
            )
            relic_img_draw.text(
                (180, 105),
                '+{}'.format(str(main_level)),
                (255, 255, 255),
                sr_font_23,
                anchor='mm',
            )

            for index, i in enumerate(relic['SubAffixList']):
                subName: str = i['Name']
                subValue = mp.mpf(i['Value'])
                subProperty = i['Property']
                if subProperty == 'CriticalDamageBase':
                    relic_score += subValue
                if subProperty == 'CriticalChanceBase':
                    relic_score += subValue * 2
                if subName in ['攻击力', '生命值', '防御力', '速度']:
                    subValueStr = nstr(subValue, 3)
                else:
                    subValueStr = nstr(subValue * 100, 3) + '%'
                subNameStr = subName.replace('百分比', '').replace('元素', '')
                # 副词条文字颜色
                relic_color = (255, 255, 255)

                relic_img_draw.text(
                    (47, 237 + index * 47),
                    '{}'.format(subNameStr),
                    relic_color,
                    sr_font_26,
                    anchor='lm',
                )
                relic_img_draw.text(
                    (290, 237 + index * 47),
                    '{}'.format(subValueStr),
                    relic_color,
                    sr_font_26,
                    anchor='rm',
                )

            char_info.paste(
                relic_img, RELIC_POS[str(relic["Type"])], relic_img
            )
        if relic_score > 1:
            relic_value_level = Image.open(TEXT_PATH / 'CommonIconS.png')
            char_info.paste(relic_value_level, (780, 963), relic_value_level)
        elif relic_score > 0.6:
            relic_value_level = Image.open(TEXT_PATH / 'CommonIconA.png')
            char_info.paste(relic_value_level, (780, 963), relic_value_level)
        elif relic_score > 0.3:
            relic_value_level = Image.open(TEXT_PATH / 'CommonIconB.png')
            char_info.paste(relic_value_level, (780, 963), relic_value_level)
        elif relic_score > 0:
            relic_value_level = Image.open(TEXT_PATH / 'CommonIconC.png')
            char_info.paste(relic_value_level, (780, 963), relic_value_level)

    else:
        char_img_draw.text(
            (525, 1565),
            'No relic!',
            white_color,
            fw_font_120,
            'mm',
        )

    # 发送图片
    res = await convert_img(char_info)
    logger.info('[sr面板]绘图已完成,等待发送!')
    return res


async def cal_char_info(char_data: dict):
    char = Character(char_data)
    await char.get_equipment_info()
    await char.get_char_attribute_bonus()
    await char.get_relic_info()
    return char


async def get_char_data(
    sr_uid: str, char_name: str, enable_self: bool = True
) -> Union[Dict, str]:
    player_path = PLAYER_PATH / str(sr_uid)
    SELF_PATH = player_path / 'SELF'
    char_name = await alias_to_char_name(char_name)
    char_path = player_path / f'{char_name}.json'
    char_self_path = SELF_PATH / f'{char_name}.json'
    if char_path.exists():
        path = char_path
    elif enable_self and char_self_path.exists():
        path = char_self_path
    else:
        return CHAR_HINT.format(char_name)

    with open(path, 'r', encoding='utf8') as fp:
        char_data = json.load(fp)
    return char_data
