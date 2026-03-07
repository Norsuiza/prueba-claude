from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp

import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from mobile.utils import api_client

C_WHITE  = (1, 1, 1, 1)
C_BG     = (0.96, 0.96, 0.96, 1)
C_GREEN  = (0.0, 0.408, 0.278, 1)
C_RED    = (0.808, 0.067, 0.149, 1)
C_TEXT   = (0.1, 0.1, 0.1, 1)
C_GRAY   = (0.45, 0.45, 0.45, 1)
C_BORDER = (0.82, 0.82, 0.82, 1)

INSTITUTIONS = [
    'Policía Municipal',
    'Policía Estatal',
    'Guardia Nacional',
    'Policía Ministerial',
    'Policía Federal Ministerial',
    'Policía Mando Único',
    'Otra autoridad',
]


def _inp(hint, password=False):
    return TextInput(
        hint_text=hint, multiline=False, password=password,
        size_hint_y=None, height=dp(44),
        background_color=C_WHITE, foreground_color=C_TEXT,
        hint_text_color=(0.6, 0.6, 0.6, 1),
        padding=[dp(10), dp(10)], font_size=dp(14),
        cursor_color=C_GREEN,
    )


def _lbl(text):
    return Label(
        text=text, color=C_GRAY,
        size_hint_y=None, height=dp(20), font_size=dp(11),
        halign='left', text_size=(None, None),
    )


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        with self.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v: setattr(self._bg, 'pos', v),
                  size=lambda w, v: setattr(self._bg, 'size', v))

        outer = BoxLayout(orientation='vertical')

        # Header
        hdr = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(56),
            padding=[dp(8), dp(8)], spacing=dp(8),
        )
        with hdr.canvas.before:
            Color(*C_GREEN)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                 size=lambda w, v: setattr(w._bg, 'size', v))

        btn_back = Button(
            text='← Volver', size_hint_x=None, width=dp(80),
            background_color=(0, 0, 0, 0), color=C_WHITE, font_size=dp(13),
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        hdr.add_widget(btn_back)
        hdr.add_widget(Label(text='Crear Cuenta', font_size=dp(17), bold=True, color=C_WHITE))
        outer.add_widget(hdr)

        scroll = ScrollView()
        form = BoxLayout(
            orientation='vertical', padding=[dp(20), dp(16)],
            spacing=dp(4), size_hint_y=None,
        )
        form.bind(minimum_height=form.setter('height'))

        fields = [
            ('Nombre de usuario *', 'f_username', False),
            ('Contraseña *', 'f_password', True),
            ('Primer apellido *', 'f_ap1', False),
            ('Segundo apellido', 'f_ap2', False),
            ('Nombre(s) *', 'f_nombre', False),
            ('Adscripción', 'f_adsc', False),
            ('Cargo / Grado', 'f_cargo', False),
            ('No. de Placa / Empleado', 'f_placa', False),
        ]
        for label, attr, pw in fields:
            form.add_widget(_lbl(label))
            inp = _inp(label.replace(' *', ''), password=pw)
            setattr(self, attr, inp)
            form.add_widget(inp)

        form.add_widget(_lbl('Institución'))
        self.f_inst = Spinner(
            text='Policía Municipal', values=INSTITUTIONS,
            size_hint_y=None, height=dp(44),
            background_color=C_WHITE, color=C_TEXT, font_size=dp(14),
        )
        form.add_widget(self.f_inst)

        self.lbl_error = Label(
            text='', color=C_RED, size_hint_y=None, height=dp(30), font_size=dp(12),
        )
        form.add_widget(self.lbl_error)

        btn = Button(
            text='CREAR CUENTA', size_hint_y=None, height=dp(50),
            background_color=C_GREEN, color=C_WHITE, font_size=dp(15), bold=True,
        )
        btn.bind(on_press=self.do_register)
        form.add_widget(btn)
        form.add_widget(Label(size_hint_y=None, height=dp(20)))

        scroll.add_widget(form)
        outer.add_widget(scroll)
        self.add_widget(outer)

    def do_register(self, *a):
        u = self.f_username.text.strip()
        p = self.f_password.text.strip()
        n = self.f_nombre.text.strip()
        a1 = self.f_ap1.text.strip()
        if not u or not p or not n or not a1:
            self.lbl_error.text = 'Usuario, contraseña, nombre y primer apellido son obligatorios'
            return
        self.lbl_error.text = 'Registrando...'
        api_client.register({
            'username': u, 'password': p,
            'primer_apellido': a1,
            'segundo_apellido': self.f_ap2.text.strip(),
            'nombre': n,
            'institucion': self.f_inst.text,
            'adscripcion': self.f_adsc.text.strip(),
            'cargo_grado': self.f_cargo.text.strip(),
            'no_placa': self.f_placa.text.strip(),
        }, on_success=self._ok, on_error=self._err)

    def _ok(self, user):
        Clock.schedule_once(lambda dt: self._go_home(), 0)

    def _err(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.lbl_error, 'text', msg), 0)

    def _go_home(self):
        self.manager.get_screen('home').refresh_user()
        self.manager.current = 'home'
