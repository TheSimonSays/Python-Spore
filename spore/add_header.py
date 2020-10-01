from http_client import RESTHttpClient


class AddHeader:
    _header_name = None
    _header_value = None

    def __init__(self, args):
        if 'header_name' in args:
            self.set_header_name(args['header_name'])
        else:
            self.set_header_name('')

        if 'header_value' in args:
            self.set_header_value(args['header_value'])

    def set_header_name(self, header_name):
        self._header_name = header_name

    def set_header_value(self, header_value):
        self._header_value = header_value

    def execute(self, spore):
        client = RESTHttpClient.get_http_client()
        client.create_or_update_header(self._header_name, self._header_value)
