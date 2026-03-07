from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mobile.utils import api_client
from mobile.config import get_server_url, save_server_url

C_DARK = (0.102, 0.102, 0.180, 1)
C_CARD = (0.086, 0.129, 0.243, 1)
C_GOLD = (0.910, 0.725, 0.137, 1)
C_WHITE = (0.918, 0.918, 0.918, 1)
C_RED = (0.85, 0.2, 0.2, 1)


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        with self.canvas.before:
            Color(*C_DARK)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        root = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(16))

        # Logo/title
        root.add_widget(Label(size_hint_y=None, height=dp(20)))
        root.add_widget(Label(
            text='SISTEMA IPH',
            font_size=dp(28), bold=True,
            color=C_GOLD, size_hint_y=None, height=dp(40),
        ))
        root.add_widget(Label(
            text='Culiacán, Sinaloa',
            font_size=dp(14), color=C_WHITE,
            size_hint_y=None, height=dp(24),
        ))
        root.add_widget(Label(size_hint_y=None, height=dp(20)))

        # Card
        card = BoxLayout(
            orientation='vertical', padding=dp(20), spacing=dp(12),
            size_hint=(1, None), height=dp(320),
        )
        with card.canvas.before:
            Color(*C_CARD)
            card._bg = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                  size=lambda w, v: setattr(w._bg, 'size', v))

        card.add_widget(Label(
            text='Iniciar Sesión', font_size=dp(18), bold=True,
            color=C_WHITE, size_hint_y=None, height=dp(30),
        ))

        self.input_user = TextInput(
            hint_text='Usuario', multiline=False,
            size_hint_y=None, height=dp(44),
            background_color=C_DARK, foreground_color=C_WHITE,
            hint_text_color=(0.5, 0.5, 0.5, 1), padding=[dp(10), dp(10)],
            font_size=dp(16),
        )
        self.input_pass = TextInput(
            hint_text='Contraseña', multiline=False, password=True,
            size_hint_y=None, height=dp(44),
            background_color=C_DARK, foreground_color=C_WHITE,
            hint_text_color=(0.5, 0.5, 0.5, 1), padding=[dp(10), dp(10)],
            font_size=dp(16),
        )

        self.lbl_error = Label(
            text='', color=C_RED, size_hint_y=None, height=dp(30),
            font_size=dp(13),
        )

        btn_login = Button(
            text='ENTRAR', size_hint_y=None, height=dp(48),
            background_color=C_GOLD, color=(0.1, 0.1, 0.1, 1),
            font_size=dp(16), bold=True,
        )
        btn_login.bind(on_press=self.do_login)

        btn_register = Button(
            text='Crear cuenta nueva', size_hint_y=None, height=dp(36),
            background_color=(0, 0, 0, 0), color=C_GOLD,
            font_size=dp(14),
        )
        btn_register.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))

        card.add_widget(self.input_user)
        card.add_widget(self.input_pass)
        card.add_widget(self.lbl_error)
        card.add_widget(btn_login)
        card.add_widget(btn_register)

        root.add_widget(card)

        # Config button (server URL)
        btn_config = Button(
            text='Configurar servidor', size_hint_y=None, height=dp(32),
            background_color=(0, 0, 0, 0), color=(0.5, 0.5, 0.5, 1),
            font_size=dp(12),
        )
        btn_config.bind(on_press=self.show_config)
        root.add_widget(btn_config)
        root.add_widget(Label())

        self.add_widget(root)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def do_login(self, *args):
        username = self.input_user.text.strip()
        password = self.input_pass.text.strip()
        if not username or not password:
            self.lbl_error.text = 'Ingresa usuario y contraseña'
            return
        self.lbl_error.text = 'Conectando...'
        api_client.login(
            username, password,
            on_success=self._on_login_success,
            on_error=self._on_login_error,
        )

    def _on_login_success(self, user):
        Clock.schedule_once(lambda dt: self._go_home(), 0)

    def _on_login_error(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.lbl_error, 'text', msg), 0)

    def _go_home(self):
        home = self.manager.get_screen('home')
        home.refresh_user()
        self.manager.current = 'home'

    def show_config(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        content.add_widget(Label(
            text='URL del servidor\n(ej: https://abc.ngrok.io)',
            color=C_WHITE, size_hint_y=None, height=dp(50),
            halign='center', font_size=dp(13),
        ))
        url_input = TextInput(
            text=get_server_url(), multiline=False,
            size_hint_y=None, height=dp(44),
            background_color=C_DARK, foreground_color=C_WHITE,
            font_size=dp(14),
        )
        content.add_widget(url_input)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        btn_cancel = Button(text='Cancelar', background_color=(0.3, 0.3, 0.3, 1))
        btn_save = Button(text='Guardar', background_color=C_GOLD, color=(0.1, 0.1, 0.1, 1))
        btn_row.add_widget(btn_cancel)
        btn_row.add_widget(btn_save)
        content.add_widget(btn_row)

        popup = Popup(
            title='Configuración del Servidor',
            content=content,
            size_hint=(0.9, None), height=dp(260),
            background_color=C_CARD,
            title_color=C_GOLD,
        )
        btn_cancel.bind(on_press=popup.dismiss)
        btn_save.bind(on_press=lambda x: (save_server_url(url_input.text), popup.dismiss()))
        popup.open()

    def on_enter(self):
        self.lbl_error.text = ''
        self.input_pass.text = ''
