import json
from pathlib import Path

MARKET = 'market'
KRX = 'KRX'
NXT = 'NXT'
SOR = 'SOR'

USER_NAME = 'name'
USER_ACCOUNT = 'account'
USER_APPKEY = 'appkey'
USER_APPSECRET = 'appsecret'
USER_CURRENT = 'current'

CONFIG_FILE = 'users.json'


USER_INFOS = []
SETTINGS = dict()
SETTINGS[MARKET] = KRX

class Model:
    @staticmethod
    def load():
        Path(CONFIG_FILE).touch()
        f = open(CONFIG_FILE, 'r', encoding="utf-8")
        text = f.read()

        if text:
            config = json.loads(text)
            USER_INFOS.extend(config.get('USER_INFOS', []))
            SETTINGS.update(config.get('SETTINGS', {}))

    @staticmethod
    def save():
        f = open(CONFIG_FILE, 'w',  encoding="utf-8")
        f.write(json.dumps({
            'USER_INFOS': USER_INFOS,
            'SETTINGS': SETTINGS
        }, ensure_ascii=False, indent=4))
        f.close()


    @staticmethod
    def update_market(market):
        SETTINGS[MARKET] = market
        Model.save()

    
    @staticmethod
    def market():
        return SETTINGS[MARKET]
    

    @staticmethod
    def find_by_user(account):
        return Model._find_by_user(USER_INFOS, account)


    @staticmethod
    def set_current_account(account):
        Model._set_current_account(USER_INFOS, account)
        Model.save()


    @staticmethod
    def add_user(name, account, appKey, appSecret, set_as_current=False):
        user = Model.find_by_user(account)

        if user != None:
            print ('user is alread exist!')
            return

        user = {
            USER_NAME: name, 
            USER_ACCOUNT: account, 
            USER_APPKEY: appKey,
            USER_APPSECRET: appSecret,
            USER_CURRENT: False}
        
        USER_INFOS.append(user)
        if set_as_current:
            Model.set_current_account(account)

        Model.save()

    @staticmethod
    def current_user():
        current = next((user for user in USER_INFOS if user.get(USER_CURRENT) is True), None)
        return current


    @staticmethod
    def account_list():
        return [user[USER_ACCOUNT] + ' ' + user[USER_NAME]  for user in USER_INFOS]
    

    @staticmethod
    def _find_by_user(data, account):
        return next((item for item in data if item[USER_ACCOUNT] == account), None)


    @staticmethod
    def _set_current_account(data, account):
        user = Model.find_by_user(account)
        if user == None:
            return
        for user in USER_INFOS:
            user[USER_CURRENT] = (user[USER_ACCOUNT] == account)            
        return USER_INFOS