# https://github.com/Womsxd/YuanShen_User_Info
import re
import sys
import time
import random
import ys_api
from ys_api import structs as ysstructs
from ys_api import UserDataMaxRetryError
from ys_api.cookie_set import timestamp_to_text

# Github-@lulu666lulu https://github.com/Azure99/GenshinPlayerQuery/issues/20
'''
{body:"",query:{"action_ticket": undefined, "game_biz": "hk4e_cn”}}
对应 https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn //查询米哈游账号下绑定的游戏(game_biz可留空)
{body:"",query:{"uid": 12345(被查询账号米哈游uid)}}
对应 https://api-takumi.mihoyo.com/game_record/app/card/wapi/getGameRecordCard?uid=
{body:"",query:{'role_id': '查询账号的uid(游戏里的)' ,'server': '游戏服务器'}}
对应 https://api-takumi.mihoyo.com/game_record/app/genshin/api/index?server= server信息 &role_id= 游戏uid
{body:"",query:{'role_id': '查询账号的uid(游戏里的)' , 'schedule_type': 1(我这边只看到出现过1和2), 'server': 'cn_gf01'}}
对应 https://api-takumi.mihoyo.com/game_record/app/genshin/api/spiralAbyss?schedule_type=1&server= server信息 &role_id= 游戏uid
{body:"",query:{game_id: 2(目前我知道有崩坏3是1原神是2)}}
对应 https://api-takumi.mihoyo.com/game_record/app/card/wapi/getAnnouncement?game_id=    这个是公告api
b=body q=query
其中b只在post的时候有内容，q只在get的时候有内容
'''


def calcStringLength(text):
    # 令len(str(string).encode()) = m, len(str(string)) = n
    # 字符串所占位置长度 = (m + n) / 2
    # 但由于'·'属于一个符号而非中文字符所以需要把长度 - 1
    if re.search('·', text) is not None:
        stringlength = int(((str(text).encode()) + len(str(text)) - 1) / 2)
    elif re.search(r'[“”]', text) is not None:
        stringlength = int((len(str(text).encode()) + len(str(text))) / 2) - 2
    else:
        stringlength = int((len(str(text).encode()) + len(text)) / 2)

    return stringlength


def spaceWrap(text, flex=10):
    stringlength = calcStringLength(text)

    return '%s' % (str(text)) + '%s' % (' ' * int((int(flex) - stringlength)))


def elementDict(text, isOculus=False):
    elementProperty = str(re.sub(r'culus_number$', '', text)).lower()
    elementMastery = {
        "anemo": "风",
        "pyro": "火",
        "geo": "岩",
        "electro": "雷",
        "cryo": "冰",
        "hydro": "水",
        "dendro": "草",  # https://genshin-impact.fandom.com/wiki/Dendro
        "none": "无",
    }
    try:
        elementProperty = str(elementMastery[elementProperty])
    except KeyError:
        elementProperty = "草"
    if isOculus:
        return elementProperty + "神瞳"
    elif not isOculus:
        return elementProperty + "属性"

def char_id_to_name(udata: ysstructs.GenshinUserData, charid: int):  # id2name.json数据不全, 我也懒得去搜集了, 故采用此邪道方法(
    chars = udata.avatars
    for char in chars:
        if charid == char.id:
            return char.name
    return f"{charid}"

def abyssAnalysis(aby: ysstructs.GenshinShenJingLuoXuan, udata: ysstructs.GenshinUserData):
    if not aby.floors:  # 没打
        return ""
    rettext = f"深境螺旋信息:\n\t开始时间: {timestamp_to_text(aby.start_time)}\n\t结束时间: {timestamp_to_text(aby.end_time)}" \
              f"\n\t最深抵达:{aby.max_floor}\n\t胜利场次/总场次: {aby.total_win_times}/{aby.total_battle_times}\n\t" \
              f"出战最多: {char_id_to_name(udata, aby.reveal_rank[0].avatar_id)} - {aby.reveal_rank[0].value}\n\t" \
              f"击破最多: {char_id_to_name(udata, aby.defeat_rank[0].avatar_id)} - {aby.defeat_rank[0].value}\n\t" \
              f"最强一击: {char_id_to_name(udata, aby.damage_rank[0].avatar_id)} - {aby.damage_rank[0].value}\n\t" \
              f"最高承伤: {char_id_to_name(udata, aby.take_damage_rank[0].avatar_id)} - {aby.take_damage_rank[0].value}\n\t" \
              f"元素战技: {char_id_to_name(udata, aby.normal_skill_rank[0].avatar_id)} - {aby.normal_skill_rank[0].value}\n\t" \
              f"元素爆发: {char_id_to_name(udata, aby.energy_skill_rank[0].avatar_id)} - {aby.energy_skill_rank[0].value}\n\t" \
              f"总星数: ★ {aby.total_star}\n\t"


    ftext = ""  # 层
    for floor in aby.floors:  # 层
        rtext = ""  # 间
        for room in floor.levels:  # 间
            btext = ""  # 场
            for battle in room.battles:  # 场次
                ctext = ""  # 角色
                for char in battle.avatars:  # 角色列表
                    ctext += f"/{char_id_to_name(udata, char.id)}"
                btext += f"\n\t\t\t\t第 {battle.index} 场: {ctext[1:]}"

            rtext += f"\n\t\t\t第 {room.index} 间 (★ {room.star}/{room.max_star}):{btext}"

        ftext += f"\n\n\t\t第 {floor.index} 层:\t{rtext}"

    rettext = f"{rettext}楼层信息:{ftext}"
    return rettext

def dataAnalysis(userid: str):
    req = ys_api.GetUserInfo()
    data = req.get_user_info(userid)
    data_abyss = req.get_user_abyss(userid)
    abyss_info = abyssAnalysis(data_abyss, data)

    Character_Info = "人物：\n\t"
    name_length = []
    Character_List = data.avatars
    for i in Character_List:
        name_length.append(calcStringLength(i.name))
    namelength_max = int(max(name_length))
    for i in Character_List:
        Character_Type = elementDict(i.element, isOculus=False)
        if i.name == "旅行者":
            if i.image.find("UI_AvatarIcon_PlayerGirl") != -1:
                TempText = (
                        spaceWrap(str("荧"), namelength_max) +
                        "（" + spaceWrap(str(i.level), 2) + "级，"
                        + Character_Type + "）\n\t"
                )
            elif i.image.find("UI_AvatarIcon_PlayerBoy") != -1:
                TempText = (
                        spaceWrap(str("空"), namelength_max) +
                        "（" + spaceWrap(str(i.level), 2) + "级，"
                        + Character_Type + "）\n\t"
                )
            else:
                TempText = (
                        i.name + "[?]" +
                        "（" + spaceWrap(str(i.level), 2) + "级，"
                        + Character_Type + "）\n\t"
                )
        else:
            TempText = (
                    spaceWrap(str(i.name), namelength_max) +
                    "（" + spaceWrap(str(i.level), 2) + "级，"
                    + str(i.actived_constellation_num) + "命，"
                    + spaceWrap(str(i.fetter), 2) + "好感度，"
                    + re.sub('^105$', '5', str(i.rarity)) + "★，"
                    + Character_Type + "）\n\t"
            )
        Character_Info = Character_Info + TempText
    Account_Info = "账号信息：\n\t"
    Account_Info += "活跃天数：　　" + str(data.stats.active_day_number) + "\n\t"
    Account_Info += "达成成就数量：" + str(data.stats.achievement_number) + "个\n\t"
    for key in data.stats:
        if re.search(r'culus_number$', key[0]) is not None:
            Account_Info = "{}{}已收集：{}个\n\t".format(
                Account_Info,
                elementDict(str(key[0]), isOculus=True),  # 判断神瞳属性
                str(key[1])
            )
        else:
            pass
    Account_Info += "获得角色数量：" + str(data.stats.avatar_number) + "个\n\t"
    Account_Info += "传送点已解锁：" + str(data.stats.way_point_number) + "个\n\t"
    Account_Info += "秘境解锁数量：" + str(data.stats.domain_number) + "个\n\t"
    Account_Info += "深渊当期进度："
    if data.stats.spiral_abyss != "-":
        Account_Info += data.stats.spiral_abyss + "\n"
    else:
        Account_Info += "没打\n"
    Account_Info = Account_Info + (
            "\n开启宝箱计数：\n\t" +
            "普通宝箱：" + str(data.stats.common_chest_number) + "个\n\t" +
            "精致宝箱：" + str(data.stats.exquisite_chest_number) + "个\n\t" +
            "珍贵宝箱：" + str(data.stats.precious_chest_number) + "个\n\t" +
            "华丽宝箱：" + str(data.stats.luxurious_chest_number) + "个\n\t" +
            "奇馈宝箱：" + str(data.stats.magic_chest_number) + "个\n"
    )
    Area_list = data.world_explorations
    Prestige_Info = "区域信息：\n"
    ExtraArea_Info = "供奉信息：\n"

    # 排版开始
    prestige_info_length = []
    extra_area_info_length = []
    for i in Area_list:
        prestige_info_length.append(calcStringLength(i.name + " "))
        if len(i.offerings) != 0:
            extra_area_info_length.append(calcStringLength(str(i.offerings[0].name) + " "))

    prestige_info_length_max = max(prestige_info_length)
    extra_area_info_length_max = max(extra_area_info_length)
    # 排版结束

    for i in Area_list:
        if (i.type == "Reputation"):
            Prestige_Info = "{}\t{}探索进度：{}%，声望等级：{}级\n".format(
                Prestige_Info,
                spaceWrap(i.name + " ", prestige_info_length_max),  # 以最长的地名为准，自动补足空格
                spaceWrap(str(i.exploration_percentage / 10).replace("100.0", "100"), 4),  # 以xx.x%长度为准，自动补足空格
                spaceWrap(str(i.level), 2)
            )
        else:
            Prestige_Info = "{}\t{}探索进度：{}%\n".format(
                Prestige_Info,
                spaceWrap(i.name + " ", prestige_info_length_max),  # 以最长的地名为准，自动补足空格
                spaceWrap(str(i.exploration_percentage / 10).replace("100.0", "100"), 4)  # 以xx.x%长度为准，自动补足空格
            )
        if len(i.offerings) != 0:
            ExtraArea_Info = "{}\t{}供奉等级：{}级，位置：{}\n".format(
                ExtraArea_Info,
                spaceWrap(str(i.offerings[0].name + " "), extra_area_info_length_max),
                spaceWrap(str(i.offerings[0].level), 2),
                str(i.name)
            )
    if len(data.homes) > 0:
        Home_Info = "家园信息：\n\t" + spaceWrap("已开启区域：", 16)
        Home_List = data.homes
        homeworld_list = []
        for i in Home_List:
            homeworld_list.append(i.name)
        Home_Info += '、'.join(homeworld_list) + "\n\t"
        Home_Info += "最高洞天仙力：  " + str(Home_List[0].comfort_num) + '（' + Home_List[0].comfort_level_name + '）\n\t'
        Home_Info += "已获得摆件数量：" + str(Home_List[0].item_num) + "\n\t"
        Home_Info += "最大信任等级：  " + str(Home_List[0].level) + '级' + "\n\t"
        Home_Info += "最高历史访客数：" + str(Home_List[0].visit_num)
    else:
        Home_Info = "家园信息：\n\t" + "家园暂未开启！"

    return (f"{Character_Info}\r\n{Account_Info}\r\n{Prestige_Info}\r\n{ExtraArea_Info}\r\n{Home_Info}\r\n\n{abyss_info}")


def infoQuery(uid):
    try:
        uid = str(int(uid))
    except:
        if uid == "exit" or uid == "q":
            sys.exit(0)
        else:
            print("输入有误！")
    if len(uid) == 9:
        print("正在查询UID" + uid + "的原神信息")
        if uid[0] in ["1", "2"]:
            _server = "官服"
        elif uid[0] == "5":
            _server = "B服"
        elif uid[0] in "6789":
            _server = {
                "6": "os_usa",
                "7": "os_euro",
                "8": "os_asia",
                "9": "os_cht",
            }[uid[0]]

        else:
            print("UID输入有误！！\r\n请检查UID是否为国服UID！")
            return

        UidInfo = dataAnalysis(uid)
        print(f"uid {uid}({_server})的信息为:\r\n" + UidInfo)

    else:
        print("UID长度有误！！\r\n请检查输入的UID是否为9位数！")


def sleep(maxSecond, queryOrder):
    sleepSec = random.randint(1, maxSecond)
    print("为避免查询过于频繁，开始第" + str(queryOrder) + "次查询之前等待" + str(sleepSec) + "秒……")
    time.sleep(sleepSec)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            infoQuery(sys.argv[i])
            if i + 1 < len(sys.argv):
                sleep(4, i + 1)  # sleep(最长等待时间, 即将执行的是第几次查询)
        quit()
    else:
        while True:
            try:
                uid = input("请输入要查询的国服UID(多个UID请使用空格分隔，退出输入exit或q)：")
                uidList = uid.split(' ')
                i = 1
                for uid in uidList:
                    infoQuery(uid)
                    i += 1
                    if i <= len(uidList):
                        sleep(4, i)

            except UserDataMaxRetryError:
                print("已达到最大出错次数, 请检查您的cookie")
                break

            except Exception as sb:
                print(sb)
