import requests
import json
import os
import threading
import base64
import hashlib

TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'auth_token.json')

# ── Cifrado simple XOR con clave derivada del path de instalación ─────────────
def _get_key():
    seed = (os.path.dirname(os.path.abspath(__file__)) + 'chatpoli-iph').encode()
    return hashlib.sha256(seed).digest()

def _xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def _encrypt(text: str) -> str:
    return base64.b64encode(_xor(text.encode(), _get_key())).decode()

def _decrypt(text: str) -> str:
    try:
        return _xor(base64.b64decode(text), _get_key()).decode()
    except Exception:
        return text  # fallback si viene sin cifrar

_token = None
_user = None


def get_token():
    global _token
    if _token:
        return _token
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                data = json.loads(_decrypt(f.read()))
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
                data = json.loads(_decrypt(f.read()))
                _user = data.get('user')
                return _user
        except Exception:
            pass
    return None


def save_session(token, user):
    global _token, _user
    _token = token
    _user = user
    payload = json.dumps({'token': token, 'user': user})
    with open(TOKEN_FILE, 'w') as f:
        f.write(_encrypt(payload))


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
    from config import get_server_url
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


def update_profile(data, on_success, on_error):
    def _run():
        try:
            url = f'{_get_base_url()}/api/me'
            resp = requests.put(url, json=data, headers=_headers(), timeout=10)
            result = resp.json()
            if resp.status_code == 200:
                save_session(get_token(), result)
                on_success(result)
            else:
                on_error(result.get('error', 'Error al guardar'))
        except requests.exceptions.ConnectionError:
            on_error('Sin conexión al servidor')
        except Exception as e:
            on_error(str(e))
    threading.Thread(target=_run, daemon=True).start()


def generate_pdf(form_data, user_data, output_path, on_success, on_error):
    def _run():
        try:
            url = f'{_get_base_url()}/api/generate_pdf'
            resp = requests.post(
                url,
                json={'form_data': form_data, 'user_data': user_data},
                headers=_headers(),
                timeout=30,
            )
            if resp.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                on_success(output_path)
            else:
                try:
                    error = resp.json().get('error', 'Error del servidor')
                except Exception:
                    error = f'Error HTTP {resp.status_code}'
                on_error(error)
        except requests.exceptions.ConnectionError:
            on_error('Sin conexión al servidor')
        except Exception as e:
            on_error(str(e))
    threading.Thread(target=_run, daemon=True).start()


def save_report(form_data, on_success, on_error):
    def _run():
        try:
            url = f'{_get_base_url()}/api/reports'
            resp = requests.post(url, json={'form_data': form_data},
                                 headers=_headers(), timeout=15)
            if resp.status_code == 201:
                on_success(resp.json())
            else:
                on_error(resp.json().get('error', 'Error al guardar'))
        except Exception as e:
            on_error(str(e))
    threading.Thread(target=_run, daemon=True).start()


def get_reports(on_success, on_error):
    def _run():
        try:
            url = f'{_get_base_url()}/api/reports'
            resp = requests.get(url, headers=_headers(), timeout=10)
            if resp.status_code == 200:
                on_success(resp.json())
            else:
                on_error('Error al obtener historial')
        except Exception as e:
            on_error(str(e))
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
