import datetime
import json
import os
import re
from datetime import datetime

import redis
import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask import redirect
from requests import RequestException
import traceback
from util import aes_decrypt

app = Flask(__name__)
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


class Account:
    def __init__(self, username=None, password=None, key=None, cookies=None, previous=None):
        self._username = username
        self._password = password
        self._key = key
        self._cookies = cookies
        self._previous = previous

    def update_cookies(self, cookies: str):
        self._cookies = cookies

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def cookies(self):
        return self._cookies

    @property
    def key(self):
        return self._key

    @property
    def previous(self):
        return self._previous

    def to_str(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {
            'username': str(self._username),
            'password': str(self._password),
            'previous': self._previous,
            'key': self._key,
            'cookies': self._cookies

        }

    @staticmethod
    def from_json(data: dict):
        return Account(
            username=data.get('username', None),
            password=data.get('password', None),
            key=data.get('key', None),
            cookies=data.get('cookies', None),
            previous=data.get('previous', None)
        )

    def update_previous(self):
        self._previous = int(datetime.utcnow().timestamp())


class HttpUtil(object):
    def __init__(self, headers=None, code_type=None, cookies=None, *args, **kwargs):
        self._headers = headers
        self._request = requests.session()
        self._code_type = code_type
        self._timeout = (7, 12)
        self._response = None
        self._advanced = False
        self._proxies = None
        if kwargs.get('proxies'):
            self._proxies = {
                'http': kwargs.get('proxies'),
                'https': kwargs.get('proxies')
            }
        if self._headers:
            self._request.headers.update(self._headers)
        if cookies:
            self._request.cookies.update(cookies)

    def get(self, url, **kwargs):
        try:
            self._response = self._request.get(url, timeout=self._timeout, proxies=self._proxies, **kwargs)
            if self._code_type and self._response:
                self._response.encoding = self._code_type
            return self._response
        except RequestException as e:
            return None

    def post(self, url, data=None, json=None, **kwargs):
        try:
            self._response = self._request.post(url, data, json, timeout=self._timeout, proxies=self._proxies, **kwargs)
            if self._code_type and self._response:
                self._response.encoding = self._code_type
            return self._response
        except RequestException as e:
            return None

    @property
    def headers(self):
        return self._request.headers

    @property
    def cookies(self):
        return self._request.cookies


BASE_URL = 'codeforces.com'


class Codeforces:
    def __init__(self, account, *args, **kwargs):
        self._account = account
        self._req = HttpUtil(*args, **kwargs)
        # if r.get('account_cookies'):
        #     self._req.cookies.update(json.loads(r.get('account_cookies')))

    def get_cookies(self):
        return self._req.cookies.get_dict()

    def set_cookies(self, cookies):
        if isinstance(cookies, dict):
            self._req.cookies.update(cookies)

    # 登录页面
    def login_website(self):
        if self.is_login():
            return True
        try:
            res = self._req.get(f'https://{BASE_URL}/enter?back=%2F')
            if res.text.find('Redirecting... Please, wait.') != -1:
                pattern = re.compile(r'var a=toNumbers\("([\da-f]*)"\),b=toNumbers\("([\da-f]*)"\),c=toNumbers\("(['
                                     r'\da-f]*)"\);')
                grps = re.search(pattern, res.text)
                key = grps.group(1)
                iv = grps.group(2)
                cipherin = grps.group(3)
                cipherout = aes_decrypt(cipherin, key, iv)
                self._req.cookies.update({'RCPC': cipherout})
                res = self._req.get(f'https://{BASE_URL}/enter?back=%2F')
            soup = BeautifulSoup(res.text, 'lxml')
            csrf_token = soup.find(attrs={'name': 'X-Csrf-Token'}).get('content')
            post_data = {
                'csrf_token': csrf_token,
                'action': 'enter',
                'ftaa': '',
                'bfaa': '',
                'handleOrEmail': self._account.username,
                'password': self._account.password,
                'remember': []
            }
            self._req.post(url=f'https://{BASE_URL}/enter', data=post_data)
        except:
            traceback.print_exc()
        return self.is_login()

    # 检查登录状态
    def is_login(self):
        res = self._req.get(f'https://{BASE_URL}')
        if res and re.search(r'logout">Logout</a>', res.text):
            r.set('account_cookies', json.dumps(self._req.cookies.get_dict()))
            return True
        return False

    def find_languages(self):
        if self.login_website() is False:
            return {}
        res = self._req.get(f'https://{BASE_URL}/problemset/submit')
        website_data = res.text
        languages = {}
        if website_data:
            soup = BeautifulSoup(website_data, 'lxml')
            tags = soup.find('select', attrs={'name': 'programTypeId'})
            if tags:
                for child in tags.find_all('option'):
                    languages[child.get('value')] = child.string
        return languages

    # 检查源OJ是否运行正常
    def is_working(self):
        return self._req.get(f'https://{BASE_URL}').status_code == 200

    def parse_lang(self, lang: str) -> str:
        lang = lang.lower()
        lang_arr = [('gcc', 'c'), ('c++', 'cpp'), ('g++', 'cpp'), ('clang', 'cpp'), ('clang++', 'cpp'), ('c#', 'cs'),
                    ('python', 'python'), ('pypy', 'python'), ('java', 'java'), ('kotlin', 'kotlin'),
                    ('javascript', 'javascript'), ('go', 'go'), ('rust', 'rust'), ('scala', 'scala'),
                    ('node.js', 'javascript')]
        ret = 'plaintext'
        for item in lang_arr:
            if item[0] in lang:
                ret = item[1]
                break
        return ret

    def retrieve_submission(self, gym_id: int, submission_id: int):
        code = r.get(f'{gym_id}-{submission_id}')
        if code is not None:
            rl = r.get(f'{gym_id}-{submission_id}-lang')
            if rl is None:
                rl = 'plaintext'
            return code, rl
        self.login_website()
        try:
            url = f'https://{BASE_URL}/gym/{gym_id}/submission/{submission_id}'
            res = self._req.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            code = soup.find(id='program-source-text').text
            r.setex(f'{gym_id}-{submission_id}', 86400, code)
            try:
                lang = soup.find('div', attrs={'class': 'datatable'}).find('table').find_all('td')[3].text.strip()
            except:
                traceback.print_exc()
                lang = None
            rl = self.parse_lang(lang) if lang else 'plaintext'
            r.setex(f'{gym_id}-{submission_id}-lang', 86400, rl)
            return code, rl
        except:
            return None, None

    def add_contest(self, invitation_token: str):
        if re.fullmatch(r'[\da-f]{40}', invitation_token) is None:
            return None
        url = f'https://codeforces.com/contestInvitation/{invitation_token}'
        res = self._req.get(url)
        if res.status_code == 200:
            return 'Ok'
        return None


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/gym/<int:gym_id>/submission/<int:submission_id>')
def gym_submission(gym_id, submission_id):
    ac = Account(os.environ['USERNAME'], os.environ['PASSWORD'])
    cf = Codeforces(ac)
    res, lang = cf.retrieve_submission(gym_id, submission_id)
    if res is None:
        return "Error Retrieve Submission"
    data = {
        'content': res,
        'expiration_seconds': 86400,
        'lang': lang,
        'title': f'{gym_id}-{submission_id}'
    }
    try:
        pb_res = requests.post('https://paste.nugine.xyz/api/records', json=data)
        key = json.loads(pb_res.text)['key']
    except:
        traceback.print_exc()
        return 'Error'
    url = f'https://paste.nugine.xyz/{key}/'
    return redirect(url)


@app.route('/contestInvitation/<invitation_token>')
def contest_invitation(invitation_token):
    return f'/contestInvitation/{invitation_token}'


if __name__ == '__main__':
    app.run()
