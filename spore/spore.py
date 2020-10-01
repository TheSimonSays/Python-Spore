from spore_exception import SporeException
from spore_response import Response
from add_header import AddHeader
from spore_middleware_weborama_authentication import SporeMiddlewareWeboramaAuthentication
from http_client import RESTHttpClient
from os import path
import json
import yaml
import sys


class Spore:
    """
    The Spore object
    Parameters
    ---------
    spec_file : str
        abs or relative path to spec file
    """
    _specs = None
    _client = None
    _methods = None
    _method_spec = None
    _format = None
    _host = None
    _base_url = None
    _request_path = None
    _request_url_path = None
    _request_params = None
    _request_cookies = None
    _request_raw_params = None
    _request_method = None
    _middlewares = None
    _httpClient = null = None
    _response = None

    def __init__(self, spec_file=None):
        self._init(spec_file)
        self._response = Response()
        self._request_params = list()
        self._request_cookies = list()
        self._middlewares = list()

    def _init(self, spec_file=None):
        """
        Custom init method for checking and loading spec file
        Parameters
        ---------
        spec_file : str
            abs or relative path to spec file
        Raises
        ------
        Spore Exception instance
            definition of spec file
        Returns
        -------
        void
        """
        if spec_file is None:
            raise SporeException('Initialization failed: spec file is not defined.')
        self._load_spec(spec_file)
        self._init_client()

    def set_base_url(self, base_url):
        self._base_url = base_url

    def enable(self, middleware, args):
        m = eval('{name}({args})'.format(name=middleware, args=args))
        self._middlewares.append(m)

    def _load_spec(self, spec_file):
        """
        Allow to know spec file extension and check it for true
        """
        _, file_extension = path.splitext(spec_file)
        if file_extension in ['.json', '.yaml']:
            spec_array = self._parse_spec_file(spec_file, file_extension)
            if 'methods' not in spec_array:
                raise SporeException('No method has been defined in the spec file: {}'.format(spec_file))
            self._specs = spec_array
        else:
            raise SporeException('Unsupported spec file: {}'.format(spec_file))

    def _parse_spec_file(self, spec_file, file_extension):
        if path.isfile(spec_file):
            if file_extension == '.json':
                with open(spec_file, 'rb') as jf:
                    spec_array = json.load(jf)
                    return spec_array
            elif file_extension == '.yaml':
                with open(spec_file, 'rb') as yf:
                    spec_array = yaml.safe_load(yf)
                    return spec_array
            else:
                raise SporeException('Unsupported spec file: {}'.format(file_extension))
        else:
            raise SporeException('File not found: {}'.format(spec_file))

    def _init_client(self):
        base_url = self._specs['base_url']
        self._base_url = base_url
        client = RESTHttpClient.connect(base_url)
        client.add_header('Accept-Charset', 'ISO-8859-1,utf-8')
        self._client = client
    
    def exec_method(self, method, params):
        if method not in self._specs['methods']:
            raise SporeException('Invalid method "{}"'.format(method))
        # print(self._specs['methods'][method])
        # print(self._specs['methods'][method]['method'])
        self._exec_method(method, params)
        return self._response

    def _exec_method(self, method, params):
        self._set_method_spec(self._specs['methods'][method])
        self._set_request_method(self._specs['methods'][method]['method'])
        self._prepare_params(method, params)
        self._prepare_cookies()

        for middleware in self._middlewares:
            middleware.execute(self)

        rest_response = None
        request_method = self._request_method.upper()

        if request_method == 'POST':
            rest_response = self._perform_post('POST', self._request_path, self._request_raw_params)
        elif request_method == 'PUT':
            rest_response = self._perform_put('PUT', self._request_path, self._request_raw_params)
        elif request_method == 'DELETE':
            rest_response = self._perform_delete('DELETE', self._request_path, self._request_raw_params)
        elif request_method == 'GET':
            rest_response = self._perform_get('GET', self._request_path, self._request_raw_params)

        self.set_response(rest_response)
        self._request_params = list()

    def _set_method_spec(self, spec):
        self._method_spec = spec
        
    def _set_request_method(self, request_method):
        self._request_method = request_method

    def _prepare_params(self, method, params):
        request_url_path = self._specs['methods'][method]['path']
        self._request_path = '{base_url}{path}'.format(
            base_url=self._base_url, 
            path=request_url_path
            )

        self._request_url_path = request_url_path
        required_params = list()
        if 'required_params' in self._specs['methods'][method]:
            for param in self._specs['methods'][method]['required_params']:
                if param not in params:
                    raise SporeException('Expected parameter {} is not found.'.format(param))

                self._insert_param(param, params[param])
                required_params.append(param)

        if params:
            for param in params:
                if param not in required_params:
                    self._insert_param(param, params[param])

        self._format = params['format'] if 'format' in params else 'json'
        self._set_raw_params(self._request_params)

    def _insert_param(self, param, value):
        if not value:
            return
        
        if self._request_path.find(':{}'.format(param)):
            self._request_path = self._request_path.replace(':{}'.format(param), value)
            self._request_url_path = self._request_url_path.replace(':{}'.format(param), value)
        else:
            self._request_params[param] = value

    def _set_raw_params(self, params=list()):
        raw_params = ''

        for param in params:
            raw_params += '' if not raw_params else '&'
            raw_params += '{param}={value}'.format(param=param, value=params[param])
        
        self._request_raw_params = raw_params

    def _prepare_cookies(self):
        cookies = self._request_cookies
        client = RESTHttpClient.get_http_client()
        cookie = ''
        for cookie_name in cookies:
            if 'name' not in cookie_name:
                raise SporeException('Expected cookie is not found.')
            else:
                cookie = '{{{name}}}={{{value}}};path={{{path}}};'.format(
                    name=cookie_name['name'],
                    value=cookie_name['value'],
                    path=cookie_name['path']
                )
                if cookie_name['domain'] is not None or cookie_name['domain'] != '':
                    cookie += 'domain={{{domain}}};'.format(domain=cookie_name['domain'])
                if cookie_name['secure'] is not None or cookie_name['secure'] != '':
                    cookie += 'secure;'

        client.add_cookie(cookie)

    def _perform_post(self, method, path, data=None):
        content_type = 'application/x-www-form-urlencoded; charset=utf-8'
        self._set_content_type(content_type)
        client = RESTHttpClient.get_http_client()
        return client.do_post(path, data)

    def _perform_put(self, method, path, data=None):
        content_type = 'application/x-www-form-urlencoded; charset=utf-8'
        self._set_content_type(content_type)
        client = RESTHttpClient.get_http_client()
        return client.do_put(path, data)

    def _perform_delete(self, method, path, data=None):
        content_type = 'application/x-www-form-urlencoded; charset=utf-8'
        self._set_content_type(content_type)
        client = RESTHttpClient.get_http_client()
        return client.do_delete(path, data)

    def _perform_get(self, method, path, data=None):
        content_type = 'application/x-www-form-urlencoded; charset=utf-8'
        self._set_content_type(content_type)
        client = RESTHttpClient.get_http_client()
        return client.do_get(path, data)

    def set_response(self, rest_response):
        client = RESTHttpClient.get_http_client()
        self._response['status'] = client.get_status()
        self._response['headers'] = client.get_header()
        self._response['body'] = self._parse_body()

    def _parse_body(self, body):
        tp = self._format.lower()
        if tp == 'xml':
            return 'xml'
        elif tp == 'json':
            return json.loads(body)
        elif tp == 'yml':
            return body

    def _set_content_type(self, content_type):
        client = RESTHttpClient.get_http_client()
        client.create_or_update_header('Content-Type', content_type)

    def get_spec(self):
        return self._specs

    def get_methods(self):
        if self._methods is not None:
            return self._methods

        methods = list()

        for method in self._specs['methods']:
            methods.append(method)

        self._methods = methods
        return methods

    def get_format(self):
        return self._format

    def get_method_spec(self):
        return self._method_spec

    def get_request_url_path(self):
        return self._request_url_path

    def get_request_params(self):
        return self._request_params

    def request_method(self):
        return self._request_method

    def get_middlewares(self):
        return self._middlewares

    def set_cookie(self, name, value, path='/', domain='', secure=False):
        cookie_array = {
            'name': name,
            'value': value,
            'path': path,
            'domain': domain,
            'secure': secure
        }

        self._request_cookies[name] = cookie_array






















