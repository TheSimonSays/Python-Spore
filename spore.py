from spore_exception import SporeException
from spore_response import Response
import http.client
from http_client import RESTHttpClient
from os import path
import json
import yaml


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
        client = http.client.HTTPSConnection(base_url)
        self._client = client
    
    def __call__(self, method, params):
        if method not in self._specs['methods']:
            raise SporeException('Invalid method {}'.format(method))
        self._exec_method(method, params)
        return self._response

    def _exec_method(self, method, params):
        pass

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
                if param not in params[0]:
                    raise SporeException('Expected parameter {} is not found.'.format(param))
                self._insert_param(param, params[0][param])
                required_params.append(param)

        if params:
            for param in params[0]:
                if param not in required_params:
                    self._insert_param(param, params[0][param])

        self._format = params[0]['format'] if 'format' in params[0] else 'json'
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
        cookies = list()
        client = RESTHttpClient.get_http_client()