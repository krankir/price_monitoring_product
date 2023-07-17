import os
import requests

from dotenv import load_dotenv


load_dotenv()

PROXY_MANAGER_API_KEY = os.getenv('PROXY_MANAGER_API_KEY')


response = requests.get('http://10.1.0.48:8003/api/v1/get_proxies', params={
    'token': PROXY_MANAGER_API_KEY,
    'type': 'socks5',
    'count': 1,
    'country': 'ru',
})
response_data = response.json()

if response_data['error'] or not response_data['payload']:
    raise RuntimeError('Proxy loading failed: ' + response_data['message'])
else:
    response_data['payload'][0]


proxy = {
    response_data['payload'][0]['host']: response_data['payload'][0]['port'],
}
