import json
import asyncio
from urllib import parse
from datetime import datetime
from typing import Dict, Optional

from ..utils.mys_api import mys_api
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH

gacha_type_meta_data = {
    '群星跃迁': ['1'],
    '始发跃迁': ['2'],
    '角色跃迁': ['11'],
    '光锥跃迁': ['12'],
}


async def get_new_gachalog_by_link(
    uid: str, gacha_url: str, full_data: Dict, is_force: bool
):
    temp = []
    for gacha_name in gacha_type_meta_data:
        for gacha_type in gacha_type_meta_data[gacha_name]:
            end_id = '0'
            for page in range(1, 999):
                url = parse.urlparse(gacha_url)
                url_parse = parse.parse_qs(url.query)
                if 'authkey' not in url_parse:
                    return {}
                authkey = url_parse['authkey'][0]
                data = await mys_api.get_gacha_log_by_link_in_authkey(
                    uid, authkey, gacha_type, page, end_id
                )
                await asyncio.sleep(0.45)
                if isinstance(data, int):
                    return {}
                data = data['list']
                if data == []:
                    break
                end_id = data[-1]['id']
                if data[-1] in full_data[gacha_name] and not is_force:
                    for item in data:
                        if item not in full_data[gacha_name]:
                            temp.append(item)
                    full_data[gacha_name][0:0] = temp
                    temp = []
                    break
                if len(full_data[gacha_name]) >= 1:
                    if int(data[-1]['id']) <= int(
                        full_data[gacha_name][0]['id']
                    ):
                        full_data[gacha_name].extend(data)
                    else:
                        full_data[gacha_name][0:0] = data
                else:
                    full_data[gacha_name].extend(data)
                await asyncio.sleep(0.25)
    return full_data


async def save_gachalogs(
    uid: str,
    gacha_url: str,
    raw_data: Optional[dict] = None,
    is_force: bool = False,
) -> str:
    path = PLAYER_PATH / str(uid)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # 获取当前时间
    now = datetime.now()
    current_time = now.strftime('%Y-%m-%d %H-%M-%S')

    # 初始化最后保存的数据
    result = {}

    # 抽卡记录json路径
    gachalogs_path = path / 'gacha_logs.json'

    # 如果有老的,准备合并, 先打开文件
    gachalogs_history = {}
    (
        old_normal_gacha_num,
        old_begin_gacha_num,
        old_char_gacha_num,
        old_weapon_gacha_num,
    ) = (0, 0, 0, 0)
    if gachalogs_path.exists():
        with open(gachalogs_path, "r", encoding='UTF-8') as f:
            gachalogs_history: Dict = json.load(f)
        gachalogs_history = gachalogs_history['data']
        old_normal_gacha_num = len(gachalogs_history['群星跃迁'])
        old_begin_gacha_num = len(gachalogs_history['始发跃迁'])
        old_char_gacha_num = len(gachalogs_history['角色跃迁'])
        old_weapon_gacha_num = len(gachalogs_history['光锥跃迁'])
    else:
        gachalogs_history = {
            '群星跃迁': [],
            '始发跃迁': [],
            '角色跃迁': [],
            '光锥跃迁': [],
        }

    # 获取新抽卡记录
    if raw_data is None:
        raw_data = await get_new_gachalog_by_link(
            uid, gacha_url, gachalogs_history, is_force
        )
    else:
        new_data = {'始发跃迁': [], '群星跃迁': [], '角色跃迁': [], '光锥跃迁': []}
        if gachalogs_history:
            for i in ['始发跃迁', '群星跃迁', '角色跃迁', '光锥跃迁']:
                for item in raw_data[i]:
                    if (
                        item not in gachalogs_history[i]
                        and item not in new_data[i]
                    ):
                        new_data[i].append(item)
            raw_data = new_data
            for i in ['始发跃迁', '群星跃迁', '角色跃迁', '光锥跃迁']:
                raw_data[i].extend(gachalogs_history[i])

    if raw_data == {} or not raw_data:
        return '请给出正确的抽卡记录链接或链接已失效'

    temp_data = {'始发跃迁': [], '群星跃迁': [], '角色跃迁': [], '光锥跃迁': []}
    for i in ['始发跃迁', '群星跃迁', '角色跃迁', '光锥跃迁']:
        for item in raw_data[i]:
            if item not in temp_data[i]:
                temp_data[i].append(item)
    raw_data = temp_data

    result['uid'] = uid
    result['data_time'] = current_time
    result['normal_gacha_num'] = len(raw_data['群星跃迁'])
    result['begin_gacha_num'] = len(raw_data['始发跃迁'])
    result['char_gacha_num'] = len(raw_data['角色跃迁'])
    result['weapon_gacha_num'] = len(raw_data['光锥跃迁'])
    for i in ['群星跃迁', '角色跃迁', '光锥跃迁']:
        if len(raw_data[i]) > 1:
            raw_data[i].sort(key=lambda x: (-int(x['id'])))
    result['data'] = raw_data

    # 计算数据
    normal_add = result['normal_gacha_num'] - old_normal_gacha_num
    begin_gacha_add = result['begin_gacha_num'] - old_begin_gacha_num
    char_add = result['char_gacha_num'] - old_char_gacha_num
    weapon_add = result['weapon_gacha_num'] - old_weapon_gacha_num
    all_add = normal_add + char_add + weapon_add + begin_gacha_add

    # 保存文件
    with open(gachalogs_path, 'w', encoding='UTF-8') as file:
        json.dump(result, file, ensure_ascii=False)

    # 回复文字
    if all_add == 0:
        im = f'UID{uid}没有新增祈愿数据!'
    else:
        im = (
            f'UID{uid}数据更新成功！'
            f'本次更新{all_add}个数据\n'
            f'群星跃迁{normal_add}个\n始发跃迁{begin_gacha_add}\n'
            f'角色跃迁{char_add}个\n光锥跃迁{weapon_add}个！'
        )
    return im
