from HearthStoneSpider.tools.ifan import iFanr
import random, string
import requests
import datetime
import time
import json

ifanr = iFanr()
tableID = ifanr.tablesID['activation_code']

# 定义激活码生成函数，并将激活码的长度length作为参数
def generatecode(length):
    result = ''  # 用于存放激活码
    s = string.ascii_letters + string.digits  # 获取字母和数字，作为生成激活码的字符集
    # string.ascii_letters  字符串常量，包含所有的大小写字母的字符串:'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # string.digits 字符串常量，包含数字0-9的字符串 '0123456789'
    for i in range(length):
        str = s[random.randint(0, len(s) - 1)]
        # n = random.randint(a, b)  #生成的随机整数n: a<= n <= b
        # 生成随机整数作为s的索引，随机整数的范围要同s的索引一致
        # 从字符集s中随机取一个字符
        result += str  # 收集随机生成的字符，形成激活码
    return result  # 返回激活码


# 定义打印激活码函数：
def printcode(length=20, count=100):  # 设置length和count默认值
    for i in range(count):
        code = generatecode((length))
        query = {
            'where': json.dumps({
                'code': {'$eq': code}
            }),
        }
        res = ifanr.get_table_data(tableID=tableID, query=query)
        if res:
            if res.get('meta').get('total_count'):
                print('该激活码已存在！')
            else:
                data = {
                    'code': code,
                    'hours': 8760,
                    'days': 365,
                    'description': '1年',
                    'state': 0
                }
                res = ifanr.add_table_data(tableID=tableID, data=data)
                print(code+'已创建',res)
        else:
            print('错误：res is none')
        print(code)

if __name__ == '__main__':
    # 调用函数，传入参数length和count，自定义激活码长度和数量
    printcode(25, 5)
