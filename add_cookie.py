from ys_api import cookie_set

if __name__ == "__main__":
    ck = cookie_set.MiHoYoCookie()

    while True:
        cookie = input("请输入cookie(退出请输入q):")
        if cookie in ["Q", "q"]:
            ck.close_connect()
            exit()
        else:
            ck.insert_cookie(cookie)
            print("添加成功, 若要添加多个, 请继续输入, 否则输入q退出")
