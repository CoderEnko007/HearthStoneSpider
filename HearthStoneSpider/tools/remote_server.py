import json
import requests
from urllib.parse import urljoin

class HSServer(object):
    def __init__(self, path=None):
        # self.host = 'http://127.0.0.1:8001'
        self.host = 'http://47.98.187.217'
        self.url = urljoin(self.host, path)

    def set_url_path(self, path):
        self.url = urljoin(self.host, path)

    def list(self, params):
        response = requests.get(self.url, params=params)
        re_dict = json.loads(response.text)
        print(response.status_code, re_dict)
        if response.status_code == 200:
            res = dict(re_dict, **{
                'status_code': 200
            })
            return res
        else:
            return {
                'status_code': response.status_code
            }

    def get(self, id):
        url = "{0}{1}/".format(self.url, str(id))
        response = requests.get(url)
        re_dict = json.loads(response.text)
        print('get', re_dict)
        if response.status_code == 200:
            res = dict(re_dict, **{
                'status_code': 200
            })
            return res
        else:
            return {
                'status_code': response.status_code
            }

    def post(self, data):
        headers = {
            'Content-Type': 'application/json'
        }
        data = json.dumps(data)
        response = requests.post(self.url, headers=headers, data=data)
        re_dict = json.loads(response.text)
        print('post', re_dict)
        if response.status_code == 200:
            res = dict(re_dict, **{
                'status_code': 200
            })
            return res
        else:
            return {
                'status_code': response.status_code
            }

    def put(self, id, data):
        url = "{0}{1}/".format(self.url, str(id))
        response = requests.put(url, json=data)
        re_dict = json.loads(response.text)
        print('put', re_dict)
        if response.status_code == 200:
            res = dict(re_dict, **{
                'status_code': 200
            })
            return res
        else:
            return {
                'status_code': response.status_code
            }

    def delete(self, id):
        url = "{0}{1}/".format(self.url, id)
        response = requests.delete(url)
        status = response.status_code
        print(status)
        return 'success' if status == '204' else 'failed'


if __name__ == '__main__':
    url = 'http://127.0.0.1:8001/winrate/'
    server = HSServer(url)
    params = {
        'rank_range': 'TOP_1000_LEGEND',
        'faction': 'Hunter',
        'archetype': 'Highlander Hunter',
        'create_time': '2020-7-19'
    }
    server.list(params=params)
    data = {
        'rank_range': 'TOP_1000_LEGEND',
        'faction': 'Hunter',
        'archetype': 'test',
        'winrate': '99.99'
        # 'create_time': str(datetime.datetime.now())
    }
    # server.put(id=117265, data=data)
    # server.delete(id=117264)