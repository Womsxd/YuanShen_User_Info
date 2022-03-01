import json
import time
import random
import hashlib
import requests
from .structs import GenshinUserData, GenshinAbyss
from .cookie_set import MiHoYoCookie
from .settings import *
from typing import Tuple


class UserDataMaxRetryError(BaseException):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


def md5(text):
    _md5 = hashlib.md5()
    _md5.update(text.encode())
    return _md5.hexdigest()


def DSGet(query: str):
    n = salt
    i = str(int(time.time()))
    r = str(random.randint(100001, 200000))
    b = ""
    q = query
    c = md5(f"salt={n}&t={i}&r={r}&b={b}&q={q}")
    return f"{i},{r},{c}"

def OSDSGet():
    n = os_salt
    i = str(int(time.time()))
    r = str(random.randint(100001, 200000))
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return i + "," + r + "," + c

def uid2server(uid: str) -> Tuple[str, bool]:
    ordict = {"1": "cn_gf01", "2": "cn_gf01",  # 国服
              "5": "cn_qd01",  # B服
              "6": "os_usa", "7": "os_euro", "8": "os_asia", "9": "os_cht"}  # 海外服
    overseas = ["6", "7", "8", "9"]
    _u = uid[0]
    if _u in ordict:
        user_server = ordict[_u]
    else:
        raise ValueError("不正确的uid")
    is_oversea = True if _u in overseas else False
    return (user_server, is_oversea)


def GetInfo(Uid, ServerID, cookie: str, overseas=False):
    if overseas:
        req = requests.get(
            url=f"https://api-os-takumi.mihoyo.com/game_record/genshin/api/index?server={ServerID}&role_id={Uid}",
            headers={
                'Accept': 'application/json, text/plain, */*',
                'DS': OSDSGet(),
                'Origin': 'https://webstatic.mihoyo.com',
                'x-rpc-app_version': os_mhyVersion,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
                'x-rpc-client_type': os_client_type,
                'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
                'X-Requested-With': 'com.mihoyo.hyperion',
                "Cookie": cookie
            }
        )
    else:
        req = requests.get(
            url=f"https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index?server={ServerID}&role_id={Uid}",
            headers={
                'Accept': 'application/json, text/plain, */*',
                'DS': DSGet(f"role_id={Uid}&server={ServerID}"),
                'Origin': 'https://webstatic.mihoyo.com',
                'x-rpc-app_version': mhyVersion,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
                'x-rpc-client_type': client_type,
                'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
                'X-Requested-With': 'com.mihoyo.hyperion',
                "Cookie": cookie
            }
        )
    return req.text

def userAbyss(uid, ServerID: str, cookie: str, overseas=False, Schedule_type="1"):
    ck = cookie
    if not overseas:
        url = f"https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/spiralAbyss?" \
              f"schedule_type={Schedule_type}&server={ServerID}&role_id={uid}"
        _ver = mhyVersion
        _ctype = client_type
    else:
        url = f"https://api-os-takumi.mihoyo.com/game_record/app/genshin/api/spiralAbyss?" \
              f"schedule_type={Schedule_type}&server={ServerID}&role_id={uid}"
        _ver = os_mhyVersion
        _ctype = os_client_type

    headers = {
        'DS': DSGet(f"role_id={uid}&schedule_type={Schedule_type}&server={ServerID}"),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': ck,
        'x-rpc-app_version': _ver,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                      '(KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': _ctype,
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    req = requests.get(url, headers=headers)
    return req.text


class GetUserInfo(MiHoYoCookie):
    def __init__(self):
        super().__init__()
        self.scount = 0

    def check_code(self, code, cookie: str):
        retcode = str(code)
        if retcode == "10001":  # cookie过期, 删除此项
            self.check_limit(cookie=cookie, remove=True)
            return False

        elif retcode == "10102":  # 隐私设置
            raise RuntimeError("用户设置了隐私")

        elif retcode == "10101":  # 触发30次上限, 标记此cookie, 今天将不再使用
            self.check_limit(cookie=cookie, to_limit=True)
            return False

        elif retcode != "0":
            raise RuntimeError(f"请求失败: {retcode}")

        else:
            return True

    def get_cookie(self):
        cookies = self.get_cookie_list()
        if not cookies:
            raise LookupError("cookie列表为空, 请添加cookie")

        randint = random.randint(0, len(cookies) - 1)
        return cookies[randint][1]

    def _get_user_info(self, uid: str, func_call, func_ret):
        _sever = uid2server(uid)
        _cookie = self.get_cookie()
        getdata = json.loads(func_call(uid, _sever[0], _cookie, overseas=_sever[1]))

        stat = self.check_code(getdata["retcode"], cookie=_cookie)
        if not stat:
            if self.scount >= 2:
                raise UserDataMaxRetryError("已达到最大出错次数, 请检查您的cookie")
            self.scount += 1
            return self._get_user_info(uid, func_call, func_ret)  # 出错(cookie过期或失效)重试

        self.scount = 0  # 重置计数

        return func_ret(**getdata["data"])

    def get_user_info(self, uid: str) -> GenshinUserData:  # 用户基础信息
        """
        用户基本信息
        :param uid: 原神uid
        :return: GenshinUserData
        """
        return self._get_user_info(uid, GetInfo, GenshinUserData)

    def get_user_abyss(self, uid: str) -> GenshinAbyss:  # 深境螺旋
        """
        深境螺旋信息
        :param uid: 原神uid
        :return: GenshinAbyss
        """
        return self._get_user_info(uid, userAbyss, GenshinAbyss)
