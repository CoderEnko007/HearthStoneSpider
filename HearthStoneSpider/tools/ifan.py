import json
import requests
import urllib

api_key = {
    'client_id':'ec59002ba0fc4c74bf50',
    'client_secret':'bd7264a9542173aa188b650c1b76580e7d612355'
}

tablesID = {
    'decks_trending': 55498,
    'decks_decks': 53174,
    'standard_decks': 53174,
    'wild_decks': 55625,
    'arena_cards': 57106,
    'trending': 53120
}

class iFanr(object):

    def __init__(self):
        self.client_id = api_key.get('client_id')
        self.client_secret = api_key.get('client_secret')
        self.code_url = "https://cloud.minapp.com/api/oauth2/hydrogen/openapi/authorize/"
        self.token_url = "https://cloud.minapp.com/api/oauth2/access_token/"
        self.tablesID = tablesID
        self.get_token()

    def get_code(self):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(self.code_url, data=json.dumps(params))
        re_dict = json.loads(response.text)
        return re_dict.get('code')

    def get_token(self):
        code = self.get_code()
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code
        }
        response = requests.post(self.token_url, data=params)
        re_dict = json.loads(response.text)
        self.token = re_dict.get('access_token')

    def get_table_data(self, tableID, query):
        BASE_API = r'https://cloud.minapp.com/oserve/v1/table/%s/record/' % tableID
        HEADERS = {
            'Authorization': 'Bearer %s' % self.token
        }
        if query:
            query_ = urllib.parse.urlencode(query)
            API = '?'.join((BASE_API, query_))
        else:
            API = BASE_API
        response = requests.get(API, headers=HEADERS)
        try:
            re_dict = json.loads(response.text)
        except Exception as e:
            re_dict = ''
            print(e)
            print('API:', API)
            print('response:', response)
        return re_dict

    def add_table_data(self, tableID, data):
        print('add_table_data', tableID)
        url = r'https://cloud.minapp.com/oserve/v1/table/%s/record/' % tableID
        headers = {
            'Authorization': 'Bearer %s' % self.token,
            'Content-Type': 'application/json'
        }
        data = json.dumps(data)
        response = requests.post(url, headers=headers, data=data)
        re_dict = json.loads(response.text)
        print('add', re_dict)
        return re_dict

    def put_table_data(self, tableID, id, data):
        print('put_table_data', tableID, id)
        if id is None:
            print('ifanr id is None')
            return
        url = r'https://cloud.minapp.com/oserve/v1/table/%s/record/%s/' % (tableID, id)
        headers = {
            'Authorization': 'Bearer %s' % self.token,
            'Content-Type': 'application/json'
        }
        data = json.dumps(data)
        response = requests.put(url, headers=headers, data=data)
        re_dict = json.loads(response.text)
        print('update', re_dict)

if __name__ == "__main__":
    ifanr = iFanr()
    deck_id = 'ifIc6Kd0qhWqF7CaoU3oih'
    query = {
        'where': json.dumps({
            'deck_id': {'$eq': deck_id}
        }),
    }
    res = ifanr.get_table_data(tableID=54281, query=query)
    print(res.get('meta').get('total_count'))
    data = {
        'deck_id': 'ifIc6Kd0qhWqF7CaoU3oih',
        'faction': 'Shaman',
        'deck_name': 'Even Shaman',
        'dust_cost': 7760,
        'win_rate': 55.8,
        'game_count': 940,
        'duration': 7.3,
        'turns': 9
    }
    if (res.get('meta').get('total_count')):
        deck = res.get('objects')[0] if res.get('objects') else 'not found deck_id:%s' % deck_id
        print(deck)
        ifanr.put_table_data(tableID=54281, id=deck['id'], data=data)
    else:
        ifanr.add_table_data(tableID=54281, data=data)
