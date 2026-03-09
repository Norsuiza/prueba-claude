from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

from utils import api_client
from utils.widgets import rounded_btn, RoundedButton, footer_bar
from config import get_server_url, save_server_url

# Colores Gobierno de México
C_WHITE   = (1, 1, 1, 1)
C_BG      = (0.96, 0.96, 0.96, 1)   # fondo gris muy claro
C_GREEN   = (0.0, 0.408, 0.278, 1)  # #006847
C_RED     = (0.808, 0.067, 0.149, 1) # #CE1126
C_TEXT    = (0.1, 0.1, 0.1, 1)
C_GRAY    = (0.4, 0.4, 0.4, 1)
C_BORDER  = (0.85, 0.85, 0.85, 1)
C_INPUT   = (1, 1, 1, 1)


def _text_input(hint, password=False):
    return TextInput(
        hint_text=hint, multiline=False, password=password,
        size_hint_y=None, height=dp(46),
        background_color=C_INPUT,
        foreground_color=C_TEXT,
        hint_text_color=(0.6, 0.6, 0.6, 1),
        padding=[dp(12), dp(12)],
        font_size=dp(15),
        cursor_color=C_GREEN,
    )


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        with self.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        outer = BoxLayout(orientation='vertical')

        # Header verde
        header = BoxLayout(
            orientation='vertical', size_hint_y=None, height=dp(140),
            padding=[dp(20), dp(20)],
        )
        with header.canvas.before:
            Color(*C_GREEN)
            header._bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                    size=lambda w, v: setattr(w._bg, 'size', v))

        header.add_widget(Label(
            text='GOBIERNO DE CULIACÁN',
            font_size=dp(12), color=(0.8, 1, 0.8, 1),
            size_hint_y=None, height=dp(18), bold=True,
        ))
        header.add_widget(Label(
            text='ChatPoli',
            font_size=dp(28), color=C_WHITE,
            size_hint_y=None, height=dp(40), bold=True,
        ))
        header.add_widget(Label(
            text='Informe Policial Homologado',
            font_size=dp(13), color=(0.85, 1, 0.85, 1),
            size_hint_y=None, height=dp(20),
        ))
        outer.add_widget(header)

        # Formulario
        form = BoxLayout(
            orientation='vertical', padding=[dp(24), dp(24)],
            spacing=dp(12), size_hint_y=None, height=dp(320),
        )
        with form.canvas.before:
            Color(*C_WHITE)
            form._bg = Rectangle(pos=form.pos, size=form.size)
        form.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                  size=lambda w, v: setattr(w._bg, 'size', v))

        form.add_widget(Label(
            text='Iniciar sesión', font_size=dp(18), bold=True,
            color=C_TEXT, size_hint_y=None, height=dp(28), halign='left',
        ))

        self.input_user = _text_input('Número de placa o usuario')
        self.input_pass = _text_input('Contraseña', password=True)

        self.lbl_error = Label(
            text='', color=C_RED, size_hint_y=None, height=dp(24),
            font_size=dp(12),
        )

        btn_login = rounded_btn('ENTRAR', height=dp(48), on_press=self.do_login)

        btn_reg = rounded_btn(
            'Crear cuenta nueva', bg=(0, 0, 0, 0),
            color=C_GREEN, height=dp(36),
        )
        btn_reg.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))

        form.add_widget(self.input_user)
        form.add_widget(self.input_pass)
        form.add_widget(self.lbl_error)
        form.add_widget(btn_login)
        form.add_widget(btn_reg)
        outer.add_widget(form)

        # Config servidor
        btn_cfg = Button(
            text='[Config] Servidor',
            size_hint_y=None, height=dp(36),
            background_color=(0, 0, 0, 0), color=C_GRAY,
            font_size=dp(12),
        )
        btn_cfg.bind(on_press=self.show_config)
        outer.add_widget(btn_cfg)
        outer.add_widget(Label())  # spacer
        outer.add_widget(footer_bar())
        self.add_widget(outer)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def do_login(self, *a):
        u = self.input_user.text.strip()
        p = self.input_pass.text.strip()
        if not u or not p:
            self.lbl_error.text = 'Ingresa usuario y contraseña'
            return
        self.lbl_error.text = 'Conectando...'
        api_client.login(u, p, on_success=self._ok, on_error=self._err)

    def _ok(self, user):
        Clock.schedule_once(lambda dt: self._go_home(), 0)

    def _err(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.lbl_error, 'text', msg), 0)

    def _go_home(self):
        self.manager.get_screen('home').refresh_user()
        self.manager.current = 'home'

    def show_config(self, *a):
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        content.add_widget(Label(
            text='URL del servidor\nEj: https://abc.ngrok.io',
            color=C_TEXT, size_hint_y=None, height=dp(44),
            halign='center', font_size=dp(13),
        ))
        ti = TextInput(
            text=get_server_url(), multiline=False,
            size_hint_y=None, height=dp(42),
            background_color=C_INPUT, foreground_color=C_TEXT, font_size=dp(13),
        )
        content.add_widget(ti)
        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        b_cancel = Button(text='Cancelar', background_color=C_BORDER, color=C_TEXT)
        b_save = Button(text='Guardar', background_color=C_GREEN, color=C_WHITE)
        row.add_widget(b_cancel)
        row.add_widget(b_save)
        content.add_widget(row)
        pop = Popup(title='Servidor', content=content,
                    size_hint=(0.9, None), height=dp(240))
        b_cancel.bind(on_press=pop.dismiss)
        b_save.bind(on_press=lambda x: (save_server_url(ti.text), pop.dismiss()))
        pop.open()

    def on_enter(self):
        self.lbl_error.text = ''
        self.input_pass.text = ''
