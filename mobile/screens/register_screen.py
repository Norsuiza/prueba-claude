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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mobile.utils import api_client

C_DARK = (0.102, 0.102, 0.180, 1)
C_CARD = (0.086, 0.129, 0.243, 1)
C_GOLD = (0.910, 0.725, 0.137, 1)
C_WHITE = (0.918, 0.918, 0.918, 1)
C_RED = (0.85, 0.2, 0.2, 1)

INSTITUTIONS = [
    'Policía Municipal',
    'Policía Estatal',
    'Guardia Nacional',
    'Policía Ministerial',
    'Policía Federal Ministerial',
    'Policía Mando Único',
    'Otra autoridad',
]


def _input(hint, password=False):
    return TextInput(
        hint_text=hint, multiline=False, password=password,
        size_hint_y=None, height=dp(44),
        background_color=C_DARK, foreground_color=C_WHITE,
        hint_text_color=(0.5, 0.5, 0.5, 1), padding=[dp(10), dp(10)],
        font_size=dp(15),
    )


def _label(text):
    return Label(
        text=text, color=(0.7, 0.7, 0.7, 1),
        size_hint_y=None, height=dp(22), font_size=dp(12),
        halign='left', text_size=(None, None),
    )


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        with self.canvas.before:
            Color(*C_DARK)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        outer = BoxLayout(orientation='vertical')

        # Header
        header = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(56),
            padding=[dp(10), dp(8)], spacing=dp(8),
        )
        with header.canvas.before:
            Color(*C_CARD)
            header._bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                    size=lambda w, v: setattr(w._bg, 'size', v))

        btn_back = Button(
            text='← Volver', size_hint_x=None, width=dp(90),
            background_color=(0, 0, 0, 0), color=C_GOLD, font_size=dp(14),
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        header.add_widget(btn_back)
        header.add_widget(Label(
            text='Crear Cuenta', font_size=dp(18), bold=True, color=C_WHITE,
        ))
        outer.add_widget(header)

        # Scrollable form
        scroll = ScrollView()
        form = BoxLayout(
            orientation='vertical', padding=dp(20), spacing=dp(6),
            size_hint_y=None,
        )
        form.bind(minimum_height=form.setter('height'))

        form.add_widget(_label('Nombre de usuario *'))
        self.f_username = _input('usuario123')
        form.add_widget(self.f_username)

        form.add_widget(_label('Contraseña *'))
        self.f_password = _input('Contraseña', password=True)
        form.add_widget(self.f_password)

        form.add_widget(_label('Primer apellido *'))
        self.f_ap1 = _input('Primer apellido')
        form.add_widget(self.f_ap1)

        form.add_widget(_label('Segundo apellido'))
        self.f_ap2 = _input('Segundo apellido')
        form.add_widget(self.f_ap2)

        form.add_widget(_label('Nombre(s) *'))
        self.f_nombre = _input('Nombre(s)')
        form.add_widget(self.f_nombre)

        form.add_widget(_label('Institución'))
        self.f_inst = Spinner(
            text='Policía Municipal',
            values=INSTITUTIONS,
            size_hint_y=None, height=dp(44),
            background_color=C_DARK, color=C_WHITE,
            font_size=dp(15),
        )
        form.add_widget(self.f_inst)

        form.add_widget(_label('Adscripción'))
        self.f_adsc = _input('Ej: Dirección de Seguridad Pública')
        form.add_widget(self.f_adsc)

        form.add_widget(_label('Cargo / Grado'))
        self.f_cargo = _input('Ej: Oficial de Tránsito')
        form.add_widget(self.f_cargo)

        form.add_widget(_label('No. de Placa / Empleado'))
        self.f_placa = _input('Ej: 0042')
        form.add_widget(self.f_placa)

        self.lbl_error = Label(
            text='', color=C_RED, size_hint_y=None, height=dp(36),
            font_size=dp(13),
        )
        form.add_widget(self.lbl_error)

        btn_reg = Button(
            text='CREAR CUENTA', size_hint_y=None, height=dp(50),
            background_color=C_GOLD, color=(0.1, 0.1, 0.1, 1),
            font_size=dp(16), bold=True,
        )
        btn_reg.bind(on_press=self.do_register)
        form.add_widget(btn_reg)
        form.add_widget(Label(size_hint_y=None, height=dp(20)))

        scroll.add_widget(form)
        outer.add_widget(scroll)
        self.add_widget(outer)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def do_register(self, *args):
        username = self.f_username.text.strip()
        password = self.f_password.text.strip()
        nombre = self.f_nombre.text.strip()
        ap1 = self.f_ap1.text.strip()

        if not username or not password or not nombre or not ap1:
            self.lbl_error.text = 'Usuario, contraseña, nombre y primer apellido son obligatorios'
            return

        self.lbl_error.text = 'Registrando...'
        data = {
            'username': username,
            'password': password,
            'primer_apellido': ap1,
            'segundo_apellido': self.f_ap2.text.strip(),
            'nombre': nombre,
            'institucion': self.f_inst.text,
            'adscripcion': self.f_adsc.text.strip(),
            'cargo_grado': self.f_cargo.text.strip(),
            'no_placa': self.f_placa.text.strip(),
        }
        api_client.register(data, on_success=self._on_success, on_error=self._on_error)

    def _on_success(self, user):
        Clock.schedule_once(lambda dt: self._go_home(), 0)

    def _on_error(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.lbl_error, 'text', msg), 0)

    def _go_home(self):
        home = self.manager.get_screen('home')
        home.refresh_user()
        self.manager.current = 'home'
