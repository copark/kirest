import json
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class AES256Cipher:
    def __init__(self, key_file='key.bin'):
        self.key_file = key_file
        self.key = self._load_or_create_key()

    def _load_or_create_key(self):
        if not Path(self.key_file).exists():
            key = os.urandom(32)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            print(f"새 AES 키 생성 및 {self.key_file}에 저장되었습니다.")
        else:
            with open(self.key_file, 'rb') as f:
                key = f.read()
                if len(key) != 32:
                    raise ValueError("키 파일이 손상되었습니다. 32바이트 키가 필요합니다.")
        return key

    def encrypt(self, data: bytes) -> bytes:
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded = padder.update(data) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()
        return iv + encrypted

    def decrypt(self, data: bytes) -> bytes:
        iv = data[:16]
        encrypted = data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(encrypted) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded) + unpadder.finalize()


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

cipher = AES256Cipher()


class Model:
    @staticmethod
    def load():
        Path(CONFIG_FILE).touch()
        with open(CONFIG_FILE, 'rb') as f:
            encrypted = f.read()

        if not encrypted:
            return

        try:
            decrypted = cipher.decrypt(encrypted)
            config = json.loads(decrypted.decode('utf-8'))
            USER_INFOS.extend(config.get('USER_INFOS', []))
            SETTINGS.update(config.get('SETTINGS', {}))
        except Exception as e:
            print(f"복호화 오류: {e}")

    @staticmethod
    def save():
        data = json.dumps({
            'USER_INFOS': USER_INFOS,
            'SETTINGS': SETTINGS
        }, ensure_ascii=False, indent=4).encode('utf-8')

        encrypted = cipher.encrypt(data)
        with open(CONFIG_FILE, 'wb') as f:
            f.write(encrypted)

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
        if user is not None:
            print('user already exists!')
            return

        user = {
            USER_NAME: name,
            USER_ACCOUNT: account,
            USER_APPKEY: appKey,
            USER_APPSECRET: appSecret,
            USER_CURRENT: False
        }

        USER_INFOS.append(user)

        if set_as_current:
            Model.set_current_account(account)

        Model.save()

    @staticmethod
    def current_user():
        return next((user for user in USER_INFOS if user.get(USER_CURRENT) is True), None)

    @staticmethod
    def account_list():
        return [user[USER_ACCOUNT] + ' ' + user[USER_NAME] for user in USER_INFOS]

    @staticmethod
    def _find_by_user(data, account):
        return next((item for item in data if item[USER_ACCOUNT] == account), None)

    @staticmethod
    def _set_current_account(data, account):
        user = Model.find_by_user(account)
        if user is None:
            return
        for user in USER_INFOS:
            user[USER_CURRENT] = (user[USER_ACCOUNT] == account)

