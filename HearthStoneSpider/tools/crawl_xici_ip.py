import requests
import time
from datetime import datetime
from scrapy.selector import Selector
from HearthStoneSpider.tools.dbtools import DBManager
from HearthStoneSpider.settings import SQL_FULL_DATETIME

db = DBManager()

def crawl_ips():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
    for i in range(10):
        if i<4:
            continue
        time.sleep(10)
        re = requests.get("https://www.xicidaili.com/wn/{0}".format(i), headers=headers )

        selector = Selector(text=re.text)
        all_trs = selector.css('#ip_list tr')

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split('秒')[0])
            # all_text = tr.css("td::text").extract()
            # ip = all_text[0]
            # port = all_text[1]
            # proxy_type = all_text[5]
            anonymous = tr.css("td:nth-of-type(5)::text").extract()[0]
            if anonymous == '高匿':
                ip = tr.css("td:nth-of-type(2)::text").extract()[0]
                port = tr.css("td:nth-of-type(3)::text").extract()[0]
                proxy_type = tr.css("td:nth-of-type(6)::text").extract()[0]

                ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            now = time.strftime("%Y/%m/%d")
            print('insert {0}://{1}:{2} {3} {4}'.format(ip_info[2], ip_info[0], ip_info[1], ip_info[3], now))
            db.insert('proxy_ip', {'ip': ip_info[0], 'port': ip_info[1], 'proxy_type':ip_info[2],
                                   'speed': ip_info[3], 'create_time': now})

class GetIP(object):
    def delete_ip(self, ip, port):
        delete_sql = "delete from proxy_ip where ip='{0}' and port='{1}'".format(ip, port)
        db.execute(delete_sql)
        db.conn.commit()
        return True

    def judge_ip(self, ip, port, proxy_type):
        http_url = "http://www.baidu.com"
        proxy_url = "{0}://{1}:{2}".format(proxy_type, ip, port)
        try:
            if (proxy_type == 'HTTP'):
                proxy_dict = {
                    "http":proxy_url
                }
            elif (proxy_type == 'HTTPS'):
                proxy_dict = {
                    "https": proxy_url
                }
            # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
            # response = requests.get(http_url, headers=headers, proxies=proxy_dict)
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print('invalid ip and port', e, ip, port)
            self.delete_ip(ip, port)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print('effective ip', ip, port)
                return True
            else:
                print('invalid ip and port code:', code, ip, port)
                self.delete_ip(ip, port)


    def get_random_ip(self):
        random_sql = "SELECT ip, port, proxy_type FROM proxy_ip ORDER BY RAND() LIMIT 1"
        result = db.execute(random_sql)
        for ip_info in db.cursor.fetchall():
            ip = ip_info['ip']
            port = ip_info['port']
            proxy_type = ip_info['proxy_type']
            res = self.judge_ip(ip, port, proxy_type)
            if res:
                now = datetime.now().strftime(SQL_FULL_DATETIME)
                print('{0}:代理IP：{1}://{2}:{3}'.format(now, proxy_type, ip, port))
                return "{0}://{1}:{2}".format(proxy_type, ip, port)
            else:
                return self.get_random_ip()

if __name__ == '__main__':
    crawl_ips()
    # get_ip = GetIP()
    # get_ip.get_random_ip()