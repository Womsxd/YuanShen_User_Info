import sqlite3
import time
import os


def timestamp_to_text(timestamp: int, _format="%Y-%m-%d %H:%M:%S"):
    """

    :param timestamp: 时间戳,若输入13位时间戳则自动转为10位
    :param _format: 格式,默认"%Y-%m-%d %H:%M:%S"
    :return: %Y-%m-%d %H:%M:%S -> str
    """
    if(timestamp > 9999999999):  # 13位时间戳转10位
        timestamp = timestamp / 1000
    ret = time.strftime(_format, time.localtime(timestamp))
    return(ret)

class MiHoYoCookie:
    def __init__(self):
        self.spath = os.path.split(__file__)[0]
        self.conn = sqlite3.connect(f"{self.spath}/mys_cookies.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.day = timestamp_to_text(int(time.time()), "%Y%m%d")
        self.closed = False

    def check_limit(self, cid=-1, cookie=None, to_limit=False, remove=False):
        ret = False
        day = self.day
        # ts = int(time.time() * 1000)
        # conn = self.conn
        cursor = self.cursor

        if to_limit:
            if cookie is not None:
                cursor.execute("UPDATE cookies SET lastlimittime = ? WHERE cookie = ?", [day, cookie])
            else:
                cursor.execute("UPDATE cookies SET lastlimittime = ? WHERE id = ?", [day, cid])
            ret = True

        if remove:
            if cookie is not None:
                cursor.execute("DELETE FROM cookies WHERE cookie = ?", [cookie])
            else:
                cursor.execute("DELETE FROM cookies WHERE id = ?", [cid])
            ret = True

        if cookie is not None:
            check = cursor.execute("SELECT id, cookie, lastlimittime FROM cookies WHERE cookie = ?", [cookie]).fetchone()
        else:
            check = cursor.execute("SELECT id, cookie, lastlimittime FROM cookies WHERE id = ?", [cid]).fetchone()

        if check is None:
            ret = True
        else:
            lastlimittime = check[2]
            if lastlimittime == day:
                ret = True

        self.conn.commit()
        return ret

    def insert_cookie(self, cookie: str):
        check = self.cursor.execute("INSERT INTO cookies (cookie) VALUES (?)", [cookie])
        self.conn.commit()

    def get_cookie_list(self):
        cks = self.cursor.execute("SELECT id, cookie, lastlimittime FROM cookies WHERE lastlimittime != ?", [self.day])
        return cks.fetchall()

    def close_connect(self):
        self.cursor.close()
        self.conn.close()
        self.closed = True

    def __del__(self):
        if not self.closed:
            self.close_connect()
