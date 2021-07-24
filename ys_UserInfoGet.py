#https://github.com/Womsxd/YuanShen_User_Info
import os
import re
import sys
import json
import time
import string
import random
import hashlib
import requests

from settings import *

def md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return (md5.hexdigest())


def DSGet():
    n = salt
    i = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5("salt=" + n + "&t="+ i + "&r=" + r)
    return (i + "," + r + "," + c)

def Cookie_get():
    global cache_Cookie
    if (cache_Cookie == ""):
        r = open("cookie.txt",mode='r+')
        tmp_Cookie = r.read()
        if (tmp_Cookie == ""):
            tmp_Cookie = input("请输入Cookie:")
            r.write(tmp_Cookie)
            r.flush()
            r.close()
        cache_Cookie = tmp_Cookie
    return (cache_Cookie)

def GetInfo(Uid, ServerID):
    # 原本的try……except没有意义并且会掩盖错误信息，删除
    req = requests.get(
        url = "https://api-takumi.mihoyo.com/game_record/genshin/api/index?server="+ ServerID +"&role_id=" + Uid ,
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'DS': DSGet(),
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': mhyVersion,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
            'x-rpc-client_type': client_type,
            'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion',
            "Cookie": Cookie_get()
        }
    )
    return (req.text)

def calcStringLength(text):
    # 令len(str(string).encode()) = m, len(str(string)) = n
    # 字符串所占位置长度 = (m + n) / 2
    # 但由于'·'属于一个符号而非中文字符所以需要把长度 - 1
    if re.search('·', text) is not None:
        stringlength = int(((str(text).encode()) + len(text) - 1) / 2)
    elif re.search(r'[“”]', text) is not None:
        stringlength = int((len(str(text).encode()) + len(str(text))) / 2) - 2
    else:
        stringlength = int((len(str(text).encode()) + len(text)) / 2)

    return stringlength

def spaceWrap(text, flex=10):
    stringlength = calcStringLength(text)

    return '%s' % (str(text)) + '%s' % (' ' * int((int(flex) - stringlength)))

def JsonAnalysis(JsonText):
    data = json.loads(JsonText)
    if ( data["retcode"] != 0):
        if (data["retcode"] == 10001):
            os.remove("cookie.txt")
            return("Cookie错误/过期，请重置Cookie")
        return (
            "Api报错，返回内容为：\r\n" 
            + JsonText + "\r\n出现这种情况可能是UID输入错误 or 不存在"
        )
    else:
        pass
    Character_Info = "人物：\n\t"
    Character_List = []
    name_length = []
    Character_List = data["data"]["avatars"]
    for i in Character_List:
        name_length.append(calcStringLength(i["name"]))
    namelength_max = int(max(name_length))
    for i in Character_List:
        if (i["element"] == "None"):
            Character_Type = "无属性"
        elif (i["element"] == "Anemo"):
            Character_Type = "风属性"
        elif (i["element"] == "Pyro"):
            Character_Type = "火属性"
        elif (i["element"] == "Geo"):
            Character_Type = "岩属性"
        elif (i["element"] == "Electro"):
            Character_Type = "雷属性"
        elif (i["element"] == "Cryo"):
            Character_Type = "冰属性"
        elif (i["element"] == "Hydro"):
            Character_Type = "水属性"
        else:
            Character_Type = "草属性"
        if (i["name"] == "旅行者"):
            if (i["image"].find("UI_AvatarIcon_PlayerGirl") != -1):
                TempText = (
                    spaceWrap(str("荧"), namelength_max) + 
                    "（" + spaceWrap(str(i["level"]), 2) + "级，" 
                    + Character_Type + "）\n\t"
                )
            elif (i["image"].find("UI_AvatarIcon_PlayerBoy") != -1):
                TempText = (
                    spaceWrap(str("空"), namelength_max) + 
                    "（" + spaceWrap(str(i["level"]), 2) + "级，" 
                    + Character_Type + "）\n\t"
                )
            else:
                TempText = (
                    i["name"]+ "[?]" + 
                    "（" + spaceWrap(str(i["level"]), 2) + "级，" 
                    + Character_Type + "）\n\t"
                )
        else:
            TempText = (
                spaceWrap(str(i["name"]), namelength_max) + 
                "（" + spaceWrap(str(i["level"]), 2) + "级，" 
                + str(i["actived_constellation_num"]) + "命，"
                + spaceWrap(str(i["fetter"]), 2) + "好感度，" 
                + str(i["rarity"]) + "★，"
                + Character_Type + "）\n\t"
            )
        Character_Info = Character_Info + TempText
    Account_Info = (
        "账号信息：\n\t活跃天数：" + str(data["data"]["stats"]["active_day_number"]) +
        "\n\t达成成就数量：" + str(data["data"]["stats"]["achievement_number"]) +
        "个\n\t风神瞳收集数量：" + str(data["data"]["stats"]["anemoculus_number"]) +
        "个\n\t岩神瞳收集数量：" + str(data["data"]["stats"]["geoculus_number"]) +
        "个\n\t获得角色数量：" + str(data["data"]["stats"]["avatar_number"]) +
        "个\n\t解锁传送点：" + str(data["data"]["stats"]["way_point_number"]) +
        "个；解锁秘境：" + str(data["data"]["stats"]["domain_number"]) +
        "\n\t深境螺旋当期进度："
    )
    if (data["data"]["stats"]["spiral_abyss"] == "-"):
        Account_Info = Account_Info + "没打\n"
    else:
        Account_Info = Account_Info + data["data"]["stats"]["spiral_abyss"] + "\n"
    Account_Info = Account_Info + (
        "\n开启宝箱计数：\n\t" + "普通宝箱：" + str(data["data"]["stats"]["common_chest_number"]) +
        "个\n\t精致宝箱：" + str(data["data"]["stats"]["exquisite_chest_number"]) +
        "个\n\t珍贵宝箱：" + str(data["data"]["stats"]["precious_chest_number"]) +
        "个\n\t华丽宝箱：" + str(data["data"]["stats"]["luxurious_chest_number"]) +
        "个\n"
    )
    Area_list = []
    Area_list = data["data"]["world_explorations"]
    Prestige_Info = "声望信息：\n"
    ExtraArea_Info = "特殊地区信息：\n"
    for i in Area_list:
        if (i["type"] == "Reputation"):
            Prestige_Info = (Prestige_Info + "\t" + i["name"] +
            "，探索进度：" + str(i["exploration_percentage"] / 10) +
            "%，声望等级：" + str(i["level"]) + "级\n")
        else:
            ExtraArea_Info = (ExtraArea_Info + "\t" + i["name"] +
            "，探索进度：" + str(i["exploration_percentage"] / 10) +
            "%，区域等级：" + str(i["level"]) + "级\n")
    Home_Info = "家园信息：\n已开启区域："
    Home_List = []
    Home_List = data["data"]["homes"]
    homeworld_list = []
    for i in Home_List:
        homeworld_list.append(i["name"])
    Home_Info += '、'.join(homeworld_list)
    Home_Info += "\n\t最高洞天仙力为" + str(Home_List[0]["comfort_num"]) + '（' + Home_List[0]["comfort_level_name"] + '）'
    Home_Info += "\n\t已获得摆件数量" + str(Home_List[0]["item_num"])
    Home_Info += "\n\t信任等级为" + str(Home_List[0]["level"]) + '级'
    Home_Info += "\n\t最高历史访客数" + str(Home_List[0]["visit_num"])

    return (Character_Info + "\r\n" + Account_Info + "\r\n" + Prestige_Info + "\r\n" + ExtraArea_Info + "\r\n" + Home_Info)

def infoQuery(uid):
    try:
        uid = str(int(uid))
    except:
        if (uid == "exit" or uid == "q"):
            sys.exit(0)
        else:
            print("输入有误！")
    if (len(uid) == 9):
        print("正在查询UID" + uid + "的原神信息")
        if (uid[0] == "1"):
            UidInfo = JsonAnalysis(GetInfo(uid ,"cn_gf01"))
            print("uid " + uid + "(官服)的信息为：\r\n" + UidInfo + "\n以上为UID：" + str(uid) + "的查询结果\n")
        elif (uid[0] == "5"):
            UidInfo = JsonAnalysis(GetInfo(uid ,"cn_qd01"))
            print("uid " + uid + "(B服)的信息为：\r\n" + UidInfo)
        else:
            print("UID输入有误！！\r\n请检查UID是否为国服UID！")
    else:
        print("UID长度有误！！\r\n请检查输入的UID是否为9位数！")

def sleep(maxSecond, queryOrder):
    sleepSec = random.randint(1,maxSecond)
    print("为避免查询过于频繁，开始第" + str(queryOrder) + "次查询之前等待" + str(sleepSec) + "秒……")
    time.sleep(sleepSec)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            infoQuery(sys.argv[i])
            if i + 1 < len(sys.argv):
                sleep(4, i + 1) # sleep(最长等待时间, 即将执行的是第几次查询)
        quit()
    else:
        while True:
            uid = input("请输入要查询的国服UID(多个UID请使用空格分隔，退出输入exit或q)：")
            uidList = uid.split(' ')
            i = 1
            for uid in uidList:
                infoQuery(uid)
                i += 1
                if i <= len(uidList):
                    sleep(4, i)