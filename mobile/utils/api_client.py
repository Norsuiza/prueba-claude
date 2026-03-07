import requests
import json
import os
import threading

TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'auth_token.json')

_token = None
_user = None


def get_token():
    global _token
    if _token:
        return _token
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
                _token = data.get('token')
                return _token
        except Exception:
            pass
    return None


def get_user():
    global _user
    if _user:
        return _user
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
                _user = data.get('user')
                return _user
        except Exception:
            pass
    return None


def save_session(token, user):
    global _token, _user
    _token = token
    _user = user
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'token': token, 'user': user}, f)


def clear_session():
    global _token, _user
    _token = None
    _user = None
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def _headers():
    token = get_token()
    h = {'Content-Type': 'application/json'}
    if token:
        h['Authorization'] = f'Bearer {token}'
    return h


def _get_base_url():
    from mobile.config import get_server_url
    return get_server_url()


def login(username, password, on_success, on_error):
    def _run():
        try:
            url = f'{_get_base_url()}/api/login'
            resp = requests.post(url, json={'username': username, 'password': password}, timeout=10)
            data = resp.json()
            if resp.status_code == 200:
                save_session(data['token'], data['user'])
                on_success(data['user'])
            else:
                on_error(data.get('error', 'Error desconocido'))
        except requests.exceptions.ConnectionError:
            on_error('No se puede conectar al servidor.\nVerifica la URL en Configuración.')
        except Exception as e:
            on_error(f'Error: {str(e)}')
    threading.Thread(target=_run, daemon=True).start()


def register(user_data, on_success, on_error):
    def _run():
        try:
            url = f'{_get_base_url()}/api/register'
            resp = requests.post(url, json=user_data, headers=_headers(), timeout=10)
            data = resp.json()
            if resp.status_code == 201:
                save_session(data['token'], data['user'])
                on_success(data['user'])
            else:
                on_error(data.get('error', 'Error al registrar'))
        except requests.exceptions.ConnectionError:
            on_error('No se puede conectar al servidor.')
        except Exception as e:
            on_error(f'Error: {str(e)}')
    threading.Thread(target=_run, daemon=True).start()


def check_auth(on_success, on_error):
    def _run():
        try:
            url = f'{_get_base_url()}/api/me'
            resp = requests.get(url, headers=_headers(), timeout=10)
            if resp.status_code == 200:
                user = resp.json()
                save_session(get_token(), user)
                on_success(user)
            else:
                clear_session()
                on_error('Sesión expirada')
        except Exception:
            cached = get_user()
            if cached:
                on_success(cached)
            else:
                on_error('Sin conexión y sin sesión guardada')
    threading.Thread(target=_run, daemon=True).start()
