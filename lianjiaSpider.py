#!C:/SoftWare/Virtualenv/python3
# @FileName: 03-链家网信息
# @Author: 李易阳
# @Time: 2019/2/27
# @Soft: PyCharm

# 导包
import urllib.request
from bs4 import BeautifulSoup
import pymysql
import time
import json
import csv

# 创建发起请求
def get_page(url, page):

    url = url.format(page)
    print("第{}页".format(page), url)

    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    # 创建请求
    req = urllib.request.Request(url, headers=headers)

    # 发起请求返回响应
    res = urllib.request.urlopen(req)

    # 网页文本
    return res.read().decode()


# 解析界面
def parge_page(html_text):
    # soup对象
    soup = BeautifulSoup(html_text, "lxml")

    # 选择所有房屋的信息
    house_list = soup.select("li.clear")
    # print(house_list)

    # 循环
    for house in house_list:
        # 定义一个字典，用于保存房屋信息
        item = {}
        # title
        item["title"] = house.select(".title a")[0].get_text()
        # 房屋信息
        item["house"] = house.select(".houseInfo")[0].get_text()
        # 位置信息
        item["position"] = house.select(".positionInfo")[0].get_text()
        # 总价
        item["totalPrice"] = house.select(".totalPrice")[0].get_text()
        # 单价
        item["unitPrice"] = house.select(".unitPrice")[0].get_text()
        # 图片
        item["img"] = house.select(".lj-lazy")[0].get("data-original")

        # print(item)
        yield item
        

# 存入数据库
def write_to_sql(house_list):
    # 创建数据库的连接
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="lwd", password="123456", db="study", charset="utf8")

    # 游标
    cursor = conn.cursor()

    # 创建sql语句
    for houes in house_list:
        for house in houes:
            sql = 'insert into ershoufang values(NULL,"{}","{}","{}","{}","{}","{}")'.format(house["title"], house["house"], house["position"], house["totalPrice"], house["unitPrice"], house["img"])
            # 开始
            conn.begin()
            # 写入数据库
            cursor.execute(sql)
            # 提交
            conn.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    conn.close()


# 存入文件txt
def write_to_txt(house_list):
    for houses in house_list:
        for house in houses:
            with open("./链家网二手房信息.txt", 'a+', encoding="utf-8") as fp:
                fp.write(json.dumps(house, ensure_ascii=False) + "\n\n")


# 存入json文件
def write_to_json(house_list):

    # 修改格式
    json_list = []
    for houses in house_list:
        for house in houses:
            json_list.append(house)

    with open("./链家网二手房信息.json", "a+", encoding="utf-8") as fp:
        fp.write(json.dumps(json_list, ensure_ascii=False))




# 存入csv文件
def write_to_csv(house_list):
    csv_item = []
    for houses in house_list:
        for house in houses:
            item = []
            for k, v in house.items():
                item.append(v)
            csv_item.append(item)
    with open("./链家网二手房信息.csv", "a+", encoding="utf-8") as fp:
        # csv对象
        w = csv.writer(fp)

        # 写入表头
        w.writerow(["title", "houseInfo", "position", "totalPrice", "unitPrice", "img_url"])

        # 写入数据
        w.writerows(csv_item)


# 主函数
def main():
    # 开始页面
    start_page = input("开始页面：")
    # 结束页面
    end_page = input("结束页面：")

    # 请求url
    url = "https://sz.lianjia.com/ershoufang/pg{}/"

    house_list = []
    for page in range(int(start_page), int(end_page)+1):

        # 创建发起请求
        html_text = get_page(url, page)

        # 解析界面
        item = parge_page(html_text)

        house_list.append(item)

    # 写入数据库
    # write_to_sql(house_list)
    # time.sleep(1)

    # 写入txt文件
    # write_to_txt(house_list)

    # 写入json文件
    write_to_json(house_list)

    # 写入csv文件
    write_to_csv(house_list)


if __name__ == '__main__':
    main()

