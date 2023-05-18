from pathlib import Path

from PIL import ImageFont

FONT_ORIGIN_PATH = Path(__file__).parent / 'starrail_origin.ttf'


def starrail_font_origin(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_ORIGIN_PATH), size=size)


sr_font_12 = starrail_font_origin(12)
sr_font_14 = starrail_font_origin(14)
sr_font_15 = starrail_font_origin(15)
sr_font_18 = starrail_font_origin(18)
sr_font_20 = starrail_font_origin(20)
sr_font_22 = starrail_font_origin(22)
sr_font_23 = starrail_font_origin(23)
sr_font_24 = starrail_font_origin(24)
sr_font_25 = starrail_font_origin(25)
sr_font_26 = starrail_font_origin(26)
sr_font_28 = starrail_font_origin(28)
sr_font_30 = starrail_font_origin(30)
sr_font_32 = starrail_font_origin(32)
sr_font_34 = starrail_font_origin(34)
sr_font_36 = starrail_font_origin(36)
sr_font_38 = starrail_font_origin(38)
sr_font_40 = starrail_font_origin(40)
sr_font_42 = starrail_font_origin(42)
sr_font_44 = starrail_font_origin(44)
sr_font_50 = starrail_font_origin(50)
sr_font_58 = starrail_font_origin(58)
sr_font_60 = starrail_font_origin(60)
sr_font_62 = starrail_font_origin(62)
sr_font_70 = starrail_font_origin(70)
sr_font_84 = starrail_font_origin(84)
