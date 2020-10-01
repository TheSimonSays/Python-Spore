from http_client import RESTHttpClient
import hashlib


class SporeMiddlewareWeboramaAuthentication:
    _application_key = None
    _private_key = None
    _signature_string = None
    _signature_sha1 = None
    _user_email = None

    def __init__(self, args):
        if 'application_key' in args:
            self.set_application_key(args['application_key'])
        else:
            self.set_application_key('')

        if 'private_key' in args:
            self.set_private_key(args['private_key'])
        else:
            self.set_private_key('')

        if 'user_email' in args:
            self.set_user_email(args['user_email'])
        else:
            self.set_user_email('')

    def set_application_key(self, application_key):
        self._application_key = application_key

    def set_private_key(self, private_key):
        self._private_key = private_key

    def set_user_email(self, user_email):
        self._user_email = user_email

    def set_signature_string(self, spore):
        self._signature_string = '{method}{path}'.format(
            method=spore.request_method().lower(),
            path=spore.get_request_url_path()
        )
        string_params = ''
        params = spore.get_request_params()
        # params = [(k, params[k]) for k in sorted(params.keys())]

        for param in params:
            string_params += '{key}={val}'.format(key=params, val=params[param])

        self._signature_string += string_params
        self._signature_string += self._private_key

    def get_signature_string(self):
        return self._signature_string

    def get_http_client(self):
        return self._http_client

    def execute(self, spore):
        self.set_signature_string(spore)
        self._signature_sha1 = hashlib.sha1(self._signature_string.encode('utf-8'))

        client = RESTHttpClient.get_http_client()
        client.create_or_update_header('X-Weborama-AppKey', self._application_key)
        client.create_or_update_header('X-Weborama-Signature', self._signature_sha1)
        client.create_or_update_header('X-Weborama-User-Email', self._user_email)

