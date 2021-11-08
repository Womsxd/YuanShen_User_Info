from pydantic import BaseModel
from typing import List


class GenshinUserCharacher(BaseModel):
    id: int
    image: str  # 角色头图url
    name: str  # 角色名
    element: str  # 属性
    fetter: int  # 好感等级
    level: int
    rarity: int  # 稀有度
    actived_constellation_num: int  # 命之座

class GenshinUserStats(BaseModel):
    active_day_number: int  # 活跃天数
    achievement_number: int  # 成就数
    win_rate: int
    anemoculus_number: int  # 风神瞳数量
    geoculus_number: int  # 岩神瞳数
    electroculus_number: int  # 雷神瞳数量
    avatar_number: int  # 角色数量
    way_point_number: int  # 传送点解锁数
    domain_number: int  # 秘境解锁数
    spiral_abyss: str  # 深渊进度
    common_chest_number: int  # 普通宝箱数量
    exquisite_chest_number: int  # 精致宝箱数量
    precious_chest_number: int  # 珍贵宝箱数量
    luxurious_chest_number: int  # 华丽宝箱数量
    magic_chest_number: int  # 奇馈宝箱数量

class GenshinWorldOfferings(BaseModel):
    name: str
    level: int

class GenshinWorldInfo(BaseModel):
    level: int  # 声望等级
    exploration_percentage: int  # 探索度
    icon: str  # 区域图标url
    name: str
    type: str
    id: int
    offerings: List[GenshinWorldOfferings]  # 供奉信息

class GenshinHomeInfo(BaseModel):
    level: int  # 信任等级
    visit_num: int  # 访客数
    comfort_num: int  # 洞天仙力
    item_num: int  # 摆件数量
    name: str
    icon: str  # 背景图
    comfort_level_name: str  # 洞天仙力对应名称
    comfort_level_icon: str  # 等级图标

class GenshinUserData(BaseModel):
    avatars: List[GenshinUserCharacher]  # 角色列表
    stats: GenshinUserStats
    city_explorations: List  # 不知道是啥玩意, 都是空的
    world_explorations: List[GenshinWorldInfo]  # 区域探索信息
    homes: List[GenshinHomeInfo]  # 家园信息

class GenshinSJLXRankInfo(BaseModel):
    avatar_id: int
    avatar_icon: str
    value: int
    rarity: int

class GenshinSJLXFloorInfoBattlesAvatars(BaseModel):
    id: int
    icon: str
    level: int
    rarity: int

class GenshinSJLXFloorInfoBattles(BaseModel):
    index: int  # 战斗场次
    timestamp: str
    avatars: List[GenshinSJLXFloorInfoBattlesAvatars]

class GenshinSJLXFloorInfo(BaseModel):
    index: int  # 间号
    star: int
    max_star: int
    battles: List[GenshinSJLXFloorInfoBattles]

class GenshinSJLXFloors(BaseModel):
    index: int  # 层数
    icon: str  # 空的
    is_unlock: bool
    settle_time: str
    star: int
    max_star: int
    levels: List[GenshinSJLXFloorInfo]

class GenshinShenJingLuoXuan(BaseModel):
    schedule_id: int
    start_time: int  # 10位
    end_time: int  # 10位
    total_battle_times: int
    total_win_times: int
    max_floor: str
    reveal_rank: List[GenshinSJLXRankInfo]  # 出战次数Rank
    defeat_rank: List[GenshinSJLXRankInfo]  # 击破数Rank
    damage_rank: List[GenshinSJLXRankInfo]  # 最强一击
    take_damage_rank: List[GenshinSJLXRankInfo]  # 承伤Rank
    normal_skill_rank: List[GenshinSJLXRankInfo]  # 元素战技释放数
    energy_skill_rank: List[GenshinSJLXRankInfo]  # 元素爆发次数
    floors: List[GenshinSJLXFloors]
    total_star: int
    is_unlock: bool

