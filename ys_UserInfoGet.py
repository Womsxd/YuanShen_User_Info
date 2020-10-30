#https://github.com/Womsxd/YuanShen_User_Info
import json
import time
import string
import random
import hashlib
import requests

def md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


def DSGet():
    mhyVersion = "2.1.0"
    n = md5(mhyVersion)
    i = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5("salt=" + n + "&t="+ i + "&r=" + r)
    return i + "," + r + "," + c
  

def GetInfo(Uid):
    req = requests.get(
        url = "https://api-takumi.mihoyo.com/game_record/genshin/api/index?server=cn_gf01&role_id=" + Uid ,
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'DS': DSGet(),
            'Origin': 'https://webstatic.mihoyo.com',
            'x-rpc-app_version': '2.1.0',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
            'x-rpc-client_type': '4',
            'Rferer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.mihoyo.hyperion'
        }
    )
    return req.text

def JsonAnalysis(JsonText):
    data = json.loads(JsonText)
    if ( data["retcode"] != 0):
        return (
            "Api报错，返回内容为：\r\n" 
            + JsonText + "\r\n出现这种情况可能的UID输入错误 or 不存在"
        )
    else:
        pass
    Character_Info = "人物："
    Character_List = []
    Character_List = data["data"]["avatars"]
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
                    i["name"]+ "[萤——妹妹]" + 
                    "（" + str(i["level"]) + "级，" 
                    + Character_Type + "）"
                )
            elif (i["image"].find("UI_AvatarIcon_PlayerBoy") != -1):
                TempText = (
                    i["name"]+ "[空——哥哥]" + 
                    "（" + str(i["level"]) + "级，" 
                    + Character_Type + "）"
                )
            else:
                TempText = (
                    i["name"]+ "[性别判断失败]" + 
                    "（" + str(i["level"]) + "级，" 
                    + Character_Type + "）"
                )
        else:
            TempText = (
                i["name"] + 
                "（" + str(i["level"]) + "级，" 
                + "好感度为" + str(i["fetter"]) + "级，" 
                + str(i["rarity"]) + "★角色，"
                + Character_Type + "）"
            )
        Character_Info = Character_Info + TempText
    Account_Info = (
        "活跃天数：" + str(data["data"]["stats"]["active_day_number"]) +
        "，一共达成了" + str(data["data"]["stats"]["achievement_number"]) +
        "个成就，风神瞳收集了" + str(data["data"]["stats"]["anemoculus_number"]) +
        "个，岩神瞳收集了" + str(data["data"]["stats"]["geoculus_number"]) +
        "个，目前获得了" + str(data["data"]["stats"]["avatar_number"]) +
        "个角色，解锁了" + str(data["data"]["stats"]["way_point_number"]) +
        "个传送点和" + str(data["data"]["stats"]["domain_number"]) +
        "个秘境，深境螺旋当期目前"
    )
    if (data["data"]["stats"]["spiral_abyss"] == "-"):
        Account_Info = Account_Info + "没打"
    else:
        Account_Info = Account_Info + "打到了" + data["data"]["stats"]["spiral_abyss"]
    Account_Info = Account_Info + (
        "，一共开启了" + str(data["data"]["stats"]["common_chest_number"]) +
        "个普通宝箱，" + str(data["data"]["stats"]["exquisite_chest_number"]) +
        "个精致宝箱，" + str(data["data"]["stats"]["luxurious_chest_number"]) +
        "个珍贵宝箱，" + str(data["data"]["stats"]["precious_chest_number"]) +
        "个华丽宝箱"
    )
    return Character_Info + "\r\n" + Account_Info

if __name__ == "__main__":
    while True:
        uid = input("请输入要查询的UID(目前仅支持国内官服，退出请输入exit)：")
        if (uid == "exit"):
            exit()
        else:
            pass
        uid = str(int(uid))
        if (len(uid) == 9):
            print("正在查询UID" + uid + "的原神信息")
            UidInfo = JsonAnalysis(GetInfo(uid))
            print("uid " + uid + "的信息为：\r\n" + UidInfo)
        else:
            print("UID长度有误！")
    pass
pass
