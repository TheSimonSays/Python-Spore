from spore_exception import SporeException
import re
import urllib.parse
from requests import Session, Request


class RESTHttpClient:
    HTTP = 'http'
    HTTPS = 'https'
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'
    PUT = 'PUT'
    HTTP_OK = 200
    HTTP_CREATED = 201
    HTTP_ACEPTED = 202

    _host = None
    _port = None
    _user = None
    _baseurl = None
    _cookies = list()
    _pass = None
    _protocol = None
    _status = None
    _content = None
    _conn_multiple = False
    _httpClient = None
    _append = list()
    _silent_mode = False
    _requests = list()
    _headers = list()

    def __init__(self, base_url, conn_multiple):
        self._connMultiple = conn_multiple
        self._baseurl = base_url

    @classmethod
    def get_http_client(cls):
        if cls._httpClient is None:
            cls._httpClient = RESTHttpClient(None, False)
        return cls._httpClient

    def get_status(self):
        return self._status

    def get_content(self):
        return self._content

    def add_cookie(self, cookie):
        self._cookies.append(cookie)
        return self._cookies

    @classmethod
    def connect(cls, base_url):
        cls._httpClient = cls(base_url, False)
        return cls._httpClient

    @classmethod
    def multi_connect(cls):
        return cls(None, False)
    
    def add(self, http):
        self._append.append(http)
        return self

    def silent_mode(self, mode=True):
        self._silent_mode = mode
        return self
    
    def set_credentials(self, user, password):
        self._user = user
        self._pass = password

    def put(self, url, params=None):
        if params is None:
            params = list()
        self._requests.append([self.PUT, self._url(url), params])
        return self

    def post(self, url, params=None):
        self._requests.append([self.POST, self._url(url), params])
        return self

    def delete(self, url, params=None):
        self._requests.append([self.DELETE, self._url(url), params])
        return self

    def get(self, url, params=None):
        self._requests.append([self.GET, self._url(url), params])
        return self

    def _get_requests(self):
        return self._requests

    def set_headers(self, headers):
        self._headers = headers
        return self
    
    def ad_header(self, header, value):
        header_str = '{header}:{value}'.format(header=header, value=value)
        self._headers.append(header_str)
        return self._headers

    def create_or_update_header(self, header, value):
        old_header = self._headers
        headers = list()
        header_str = '{header}:{value}'.format(header=header, value=value)
        pattern = '/^{header}/'.format(header=header)
        is_defined_header = 0

        for old_header_value in old_header:
            if re.search(pattern, old_header_value):
                headers.append(header_str)
                is_defined_header = 1
            else:
                headers.append(old_header_value)
        
        if is_defined_header == 0:
            header.append(header_str)
        
        self._headers = header
        return self._headers
    
    def get_headers(self):
        return self._headers

    def _url(self, url=None):
        return url
    
    def _exec(self, _type, url, params=None):
        headers = self._headers
        cookies = ''.join(self._cookies)
        session = Session()

        if self._user is not None:
            payload = {self._user: self._pass}
        else:
            payload = {}

        if _type in [self.DELETE, self.GET]:
            url = urllib.parse.urlencode('{url}?{params}'.format(url=url, params=params))
            request = Request(_type, url, params=params, cookies=cookies, data=payload, headers=headers)
        elif _type in [self.PUT, self.POST, self.GET]:
            request = Request(_type, url, params=params, cookies=cookies, data=payload, headers=headers)
        else:
            raise SporeException('Undefined method: {method}.'.format(method=_type))

        prepped = session.prepare_request(request)
        response = session.send(prepped)
        status = response.status_code
        if status in [self.HTTP_OK, self.HTTP_CREATED, self.HTTP_ACEPTED]:
            response = response.text
        self._content = response
        return response

    def run(self):
        if self._conn_multiple:
            return self._run_multiple()
        else:
            return self._run()

    def _run_multiple(self):
        response = None
        if len(self._append) > 0:
            arr = list()
            for _append in self._append:
                arr = arr + _append

            self._requests = arr
            response = self._run()
        return response

    def _run(self):
        headers = self._headers
        curly = result = list()
        print(self._requests)

    def do_post(self, url, params=None):
        return self._exec(self.POST, self._url(url), params)