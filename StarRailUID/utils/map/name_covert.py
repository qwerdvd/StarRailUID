from .SR_MAP_PATH import (
    EquipmentID2Name,
    EquipmentID2EnName,
    alias_data,
    avatarId2Name,
)


async def avatar_id_to_name(avatar_id: str) -> str:
    char_name = avatarId2Name[avatar_id]
    return char_name


async def name_to_avatar_id(name: str) -> str:
    avatar_id = ''
    for i in avatarId2Name:
        if avatarId2Name[i] == name:
            avatar_id = i
            break
    return avatar_id


async def alias_to_char_name(char_name: str) -> str:
    for i in alias_data['characters']:
        if char_name in alias_data['characters'][i]:
            return alias_data['characters'][i][0]
    return char_name


async def weapon_id_to_name(weapon_id: str) -> str:
    weapon_name = EquipmentID2Name[weapon_id]
    return weapon_name


async def name_to_weapon_id(name: str) -> str:
    weapon_id = ''
    for i in EquipmentID2Name:
        if EquipmentID2Name[i] == name:
            weapon_id = i
            break
    return weapon_id


async def weapon_id_to_en_name(weapon_id: str) -> str:
    weapon_en_name = EquipmentID2EnName[weapon_id]
    return weapon_en_name


async def en_name_to_weapon_id(name: str) -> str:
    weapon_id = ''
    for i in EquipmentID2EnName:
        if EquipmentID2EnName[i] == name:
            weapon_id = i
            break
    return weapon_id
