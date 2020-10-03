import json
import requests

def GetInfo(Uid):
    req = requests.get(
        url = "https://api-takumi.mihoyo.com/game_record/genshin/api/index?server=cn_gf01&role_id=" + Uid ,
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,zh-HK;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
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
        print("正在查询UID" + uid + "的原神信息")
        UidInfo = JsonAnalysis(GetInfo(uid))
        print("uid " + uid + "的信息为：\r\n" + UidInfo)
    pass
pass
