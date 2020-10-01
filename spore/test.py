from spore import Spore

settings = {
    'application_key': '***',
    'private_key': '***',
    'email': '***',
    'password': '***',
}

client = Spore('/home/mgruzdev/projects/Python-Spore/config/route_config.desktop.yaml')

acc = 534

client.enable('AddHeader', {
    'header_name': 'X-Weborama-Account_Id',
    'header_value': acc
})

client.enable('SporeMiddlewareWeboramaAuthentication', {
    'application_key': settings['application_key'],
    'private_key': settings['private_key'],
    'user_email': settings['email']
})

# get_authentication_token
auth = client.exec_method('get_authentication_token', {
    'format': 'json',
    'email': '***',
    'password': '***',
})

# auth = client.get_authentication_token()
