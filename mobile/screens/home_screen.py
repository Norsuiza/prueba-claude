from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.metrics import dp

import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from mobile.utils import api_client

C_WHITE  = (1, 1, 1, 1)
C_BG     = (0.94, 0.94, 0.94, 1)
C_GREEN  = (0.0, 0.408, 0.278, 1)
C_RED    = (0.808, 0.067, 0.149, 1)
C_TEXT   = (0.1, 0.1, 0.1, 1)
C_GRAY   = (0.5, 0.5, 0.5, 1)
C_LIGHT  = (0.97, 0.97, 0.97, 1)

MODULES = [
    {'title': 'IPH · Delitos',       'sub': 'Informe Policial\nHomologado', 'screen': 'iph',  'active': True},
    {'title': 'IPH · Accidentes',    'sub': 'En desarrollo',                'screen': None,   'active': False},
    {'title': 'Actas Admin.',         'sub': 'En desarrollo',                'screen': None,   'active': False},
    {'title': 'Partes Diarios',       'sub': 'En desarrollo',                'screen': None,   'active': False},
    {'title': 'Estadísticas',         'sub': 'En desarrollo',                'screen': None,   'active': False},
    {'title': 'Directorio',           'sub': 'En desarrollo',                'screen': None,   'active': False},
]


class ModuleCard(Button):
    def __init__(self, title, sub, active, target, mgr_getter, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self._target = target
        self._mgr_getter = mgr_getter

        with self.canvas.before:
            Color(*C_WHITE if active else C_LIGHT)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
            if active:
                Color(*C_GREEN)
                self._border = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._upd, size=self._upd)

        inner = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(4))

        t = Label(
            text=title, font_size=dp(13), bold=True,
            color=C_GREEN if active else C_GRAY,
            size_hint_y=None, height=dp(38),
            halign='center', valign='middle',
        )
        t.bind(size=t.setter('text_size'))

        s = Label(
            text=sub, font_size=dp(10),
            color=C_TEXT if active else C_GRAY,
            halign='center', valign='top',
        )
        s.bind(size=s.setter('text_size'))

        inner.add_widget(t)
        inner.add_widget(s)
        self.add_widget(inner)

        if active and target:
            self.bind(on_press=self._go)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        if hasattr(self, '_border'):
            # thin green border
            pass

    def _go(self, *a):
        mgr = self._mgr_getter()
        if mgr:
            mgr.current = self._target


class HomeScreen(Screen):
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
            orientation='horizontal', size_hint_y=None, height=dp(72),
            padding=[dp(16), dp(10)], spacing=dp(10),
        )
        with hdr.canvas.before:
            Color(*C_GREEN)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                 size=lambda w, v: setattr(w._bg, 'size', v))

        info = BoxLayout(orientation='vertical')
        self.lbl_name = Label(
            text='Bienvenido', font_size=dp(15), bold=True,
            color=C_WHITE, halign='left',
        )
        self.lbl_name.bind(size=self.lbl_name.setter('text_size'))
        self.lbl_role = Label(
            text='', font_size=dp(11), color=(0.85, 1, 0.85, 1), halign='left',
        )
        self.lbl_role.bind(size=self.lbl_role.setter('text_size'))
        info.add_widget(self.lbl_name)
        info.add_widget(self.lbl_role)

        btn_out = Button(
            text='Salir', size_hint_x=None, width=dp(56),
            background_color=C_RED, color=C_WHITE,
            font_size=dp(13), bold=True,
        )
        btn_out.bind(on_press=self._logout)

        hdr.add_widget(info)
        hdr.add_widget(btn_out)
        outer.add_widget(hdr)

        # Divider label
        outer.add_widget(Label(
            text='MÓDULOS', font_size=dp(11), bold=True,
            color=C_GRAY, size_hint_y=None, height=dp(32),
        ))

        # Grid de módulos
        scroll = ScrollView()
        grid = GridLayout(
            cols=2, padding=[dp(12), dp(4)], spacing=dp(10),
            size_hint_y=None,
        )
        grid.bind(minimum_height=grid.setter('height'))

        for m in MODULES:
            card = ModuleCard(
                title=m['title'], sub=m['sub'],
                active=m['active'], target=m['screen'],
                mgr_getter=lambda: self.manager,
                size_hint_y=None, height=dp(100),
            )
            grid.add_widget(card)

        scroll.add_widget(grid)
        outer.add_widget(scroll)
        self.add_widget(outer)

    def refresh_user(self):
        user = api_client.get_user()
        if user:
            nombre = f"{user.get('nombre', '')} {user.get('primer_apellido', '')}".strip()
            self.lbl_name.text = f"Bienvenido, {nombre}"
            cargo = user.get('cargo_grado', '')
            inst = user.get('institucion', '')
            self.lbl_role.text = f"{cargo} · {inst}".strip(' · ')

    def on_enter(self):
        self.refresh_user()
        # Actualizar manager ref en cards
        for card in self.walk():
            if isinstance(card, ModuleCard):
                card._mgr_getter = lambda: self.manager

    def _logout(self, *a):
        api_client.clear_session()
        self.manager.current = 'login'
