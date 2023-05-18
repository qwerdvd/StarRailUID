# flake8: noqa
OLD_URL = "https://api-takumi.mihoyo.com"
NEW_URL = 'https://api-takumi-record.mihoyo.com'

STAR_RAIL_SIGN_INFO_URL = f'{OLD_URL}/event/luna/info'
STAR_RAIL_SIGN_LIST_URL = f'{OLD_URL}/event/luna/home'
STAR_RAIL_SIGN_EXTRA_INFO_URL = f'{OLD_URL}/event/luna/extra_info'
STAR_RAIL_SIGN_EXTRA_REWARD_URL = f'{OLD_URL}/event/luna/extra_reward'
STAR_RAIL_SIGN_URL = f'{OLD_URL}/event/luna/sign'
STAR_RAIL_MONTH_INFO_URL = f'{OLD_URL}/event/srledger/month_info'  # 开拓阅历接口
STAR_RAIL_MONTH_DETAIL_URL = (
    f'{OLD_URL}/event/srledger/month_detail'  # 开拓阅历详情接口
)

STAR_RAIL_NOTE_URL = f'{NEW_URL}/game_record/app/hkrpg/api/note'  # 实时便签接口
STAR_RAIL_INDEX_URL = f'{NEW_URL}/game_record/app/hkrpg/api/index'  # 角色橱窗接口
STAR_RAIL_AVATAR_BASIC_URL = (
    f'{NEW_URL}/game_record/app/hkrpg/api/avatar/basic'  # 全部角色接口
)
STAR_RAIL_ROLE_BASIC_INFO_URL = (
    f'{NEW_URL}/game_record/app/hkrpg/api/role/basicInfo'  # 角色基础信息接口
)
STAR_RAIL_AVATAR_INFO_URL = (
    f'{NEW_URL}/game_record/app/hkrpg/api/avatar/info'  # 角色详细信息接口
)

CHALLENGE_INFO_URL = f'{NEW_URL}/game_record/app/hkrpg/api/challenge'

STAR_RAIL_GACHA_LOG_URL = f'{OLD_URL}/common/gacha_record/api/getGachaLog'

GET_FP_URL = 'https://public-data-api.mihoyo.com/device-fp/api/getFp'
# CREATE_QRCODE = f'{OLD_URL}/event/bbs_sign_reward/gen_auth_code'

_API = locals()
