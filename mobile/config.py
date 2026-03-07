import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'server_config.json')

DEFAULT_SERVER_URL = 'http://localhost:5001'  # PC local; en Android usa la IP de tu PC o ngrok


def get_server_url():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get('server_url', DEFAULT_SERVER_URL)
        except Exception:
            pass
    return DEFAULT_SERVER_URL


def save_server_url(url):
    url = url.strip().rstrip('/')
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'server_url': url}, f)
