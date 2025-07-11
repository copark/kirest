import requests
import json
import time
from config import *
from util import *
from model import *

# https://openapi.kiwoom.com/guide/apiguide

HOST = 'https://api.kiwoom.com'
MOCK_HOST = 'https://mockapi.kiwoom.com'

TOKEN_PATH = '/oauth2/token'
ACCOUNT_PATH = '/api/dostk/acnt'
ORDER_PATH = '/api/dostk/ordr'
INFO_PATH = '/api/dostk/stkinfo'

CONTENT_TYPE = 'application/json;charset=UTF-8'

class Kiwoon:
    def __init__(self, appKey, appSecret):
        self.appKey = appKey
        self.appSecret = appSecret
        self.token = ''
        self.expires_dt = ''
        

    def get_header(self,token=None, cont=None, next=None, api=None):
        headers = {
            'Contrent-Type': CONTENT_TYPE,
        }

        if token != None:
            headers['authorization'] = f'Bearer {token}'
        
        if cont != None:
            headers['cont-yn'] = cont
        
        if next != None:
            headers['next-key'] = next

        if api != None:
            headers['api-id'] = api
                    
        return headers

    def token_body(self):
        body = {
            'grant_type': 'client_credentials',
            'appkey': self.appKey,
            'secretkey': self.appSecret
        }
        return body

    def url_request(self, url, headers, data):
        start_time = time.time()

        if DEBUG:
            print('--------------------------------------------------')
            print(f'url = {url}')
            print(f'header = {headers}')
            print(f'body = {data}')

        response = requests.post(url, headers=headers, json=data)
        end_time = time.time()
        elapsed_time = end_time - start_time

        if DEBUG:
            print('--------------------------------------------------')
            print (f'{response.status_code} {response.text}')

        return response


    def is_ok(self, response):
        if response.status_code == 200 and response.json()['return_code'] == 0:
            return True
        
        return False
    
    def is_valid_token(self):
        if self.token == '' or self.expires_dt == '':
            return False
        
        if self.expires_dt < Util.today():
            return False
        
        return True


    def request_api(self, path, api, params):
        url = HOST + path
        responses = []
        req_headers = self.get_header(token=self.token, api=api)        
        while True:
            response = self.url_request(url, req_headers, params)
            responses.append(response.json())

            res_headers = response.headers
            if not self.has_next(res_headers):
                break
            
            req_headers = self.get_header(self.token, res_headers['cont-yn'], res_headers['next-key'], api)
        
        return responses


    def has_next(self, header):
        if 'cont-yn' in header:
            return header['cont-yn'] == 'Y'
        
        return False

    
    def request_token(self):
        url = HOST + TOKEN_PATH
        response = self.url_request(url, self.get_header(), self.token_body())       
        if not self.is_ok(response):
            Util.show_warning('token error')
            return
        r = response.json()
        self.token = r['token']
        self.expires_dt = r['expires_dt']


    # kt00003 추정자산조회요청
    # kt00004 계좌평가현황요청
    # ka10075 미체결요청
    def request_account(self, command, params):
        self.request_token()

        return self.request_api(ACCOUNT_PATH, command, params)    


    # kt10000 주식 매수주문
    # kt10001 주식 매도주문
    # kt10002 주식 정정주문 
    # kt10003 주식 취소주문
    def request_order(self, command, params):
        return self.request_api(ORDER_PATH, command, params)
    
    # ka10099 종목정보 리스트 , 0. 10
    def request_stocklist(self, market):
        params = {'mrkt_tp': market }
        return self.request_api(INFO_PATH, 'ka10099', params)
    

    def is_valid_order(self, code, qty, uv):
        if code == '' or qty == '' or uv == '':
            return False    
        return True
