from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from mobile.utils import api_client

C_DARK = (0.102, 0.102, 0.180, 1)
C_CARD = (0.086, 0.129, 0.243, 1)
C_GOLD = (0.910, 0.725, 0.137, 1)
C_WHITE = (0.918, 0.918, 0.918, 1)
C_GRAY = (0.4, 0.4, 0.4, 1)
C_GREEN = (0.2, 0.7, 0.3, 1)


MODULES = [
    {
        'title': 'IPH\nDelitos',
        'icon': '📋',
        'desc': 'Informe Policial\nHomologado',
        'screen': 'iph',
        'active': True,
    },
    {
        'title': 'IPH\nAccidentes',
        'icon': '🚗',
        'desc': 'En desarrollo',
        'screen': None,
        'active': False,
    },
    {
        'title': 'Actas\nAdmin.',
        'icon': '📝',
        'desc': 'En desarrollo',
        'screen': None,
        'active': False,
    },
    {
        'title': 'Partes\nDiarios',
        'icon': '📊',
        'desc': 'En desarrollo',
        'screen': None,
        'active': False,
    },
    {
        'title': 'Estadísticas',
        'icon': '📈',
        'desc': 'En desarrollo',
        'screen': None,
        'active': False,
    },
    {
        'title': 'Directorio',
        'icon': '📞',
        'desc': 'En desarrollo',
        'screen': None,
        'active': False,
    },
]


class ModuleCard(Button):
    def __init__(self, title, icon, desc, active, target_screen, manager_ref, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.target_screen = target_screen
        self.manager_ref = manager_ref

        with self.canvas.before:
            if active:
                Color(*C_CARD)
            else:
                Color(0.12, 0.12, 0.20, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                  size=lambda w, v: setattr(w._bg, 'size', v))

        inner = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))

        icon_lbl = Label(
            text=icon, font_size=dp(30),
            size_hint_y=None, height=dp(40),
        )
        title_lbl = Label(
            text=title, font_size=dp(13), bold=True,
            color=C_GOLD if active else C_GRAY,
            size_hint_y=None, height=dp(36),
            halign='center', valign='middle',
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))

        desc_lbl = Label(
            text=desc if active else 'En desarrollo',
            font_size=dp(10),
            color=C_WHITE if active else C_GRAY,
            size_hint_y=None, height=dp(30),
            halign='center', valign='middle',
        )
        desc_lbl.bind(size=desc_lbl.setter('text_size'))

        inner.add_widget(icon_lbl)
        inner.add_widget(title_lbl)
        inner.add_widget(desc_lbl)
        self.add_widget(inner)

        if active and target_screen:
            self.bind(on_press=self._go_to_screen)

    def _go_to_screen(self, *args):
        if self.manager_ref and self.target_screen:
            self.manager_ref.current = self.target_screen


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user = None
        self._build_ui()

    def _build_ui(self):
        with self.canvas.before:
            Color(*C_DARK)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        outer = BoxLayout(orientation='vertical')

        # Header bar
        self.header = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(70),
            padding=[dp(16), dp(8)], spacing=dp(8),
        )
        with self.header.canvas.before:
            Color(*C_CARD)
            self.header._bg = Rectangle(pos=self.header.pos, size=self.header.size)
        self.header.bind(
            pos=lambda w, v: setattr(w._bg, 'pos', v),
            size=lambda w, v: setattr(w._bg, 'size', v),
        )

        header_text = BoxLayout(orientation='vertical')
        self.lbl_welcome = Label(
            text='Bienvenido', font_size=dp(14), color=C_GOLD,
            halign='left', bold=True,
        )
        self.lbl_welcome.bind(size=self.lbl_welcome.setter('text_size'))
        self.lbl_cargo = Label(
            text='Oficial de Tránsito', font_size=dp(11), color=C_WHITE,
            halign='left',
        )
        self.lbl_cargo.bind(size=self.lbl_cargo.setter('text_size'))
        header_text.add_widget(self.lbl_welcome)
        header_text.add_widget(self.lbl_cargo)

        btn_logout = Button(
            text='Salir', size_hint_x=None, width=dp(60),
            background_color=(0.5, 0.1, 0.1, 1), color=C_WHITE,
            font_size=dp(13),
        )
        btn_logout.bind(on_press=self.do_logout)

        self.header.add_widget(header_text)
        self.header.add_widget(btn_logout)
        outer.add_widget(self.header)

        # Subtitle
        sub = Label(
            text='MÓDULOS DEL SISTEMA',
            font_size=dp(12), color=C_GRAY,
            size_hint_y=None, height=dp(36),
            bold=True,
        )
        outer.add_widget(sub)

        # Module grid
        scroll = ScrollView()
        grid = GridLayout(
            cols=2, padding=dp(16), spacing=dp(12),
            size_hint_y=None,
        )
        grid.bind(minimum_height=grid.setter('height'))

        for mod in MODULES:
            card = ModuleCard(
                title=mod['title'],
                icon=mod['icon'],
                desc=mod['desc'],
                active=mod['active'],
                target_screen=mod['screen'],
                manager_ref=self.manager,
                size_hint_y=None,
                height=dp(120),
            )
            grid.add_widget(card)

        scroll.add_widget(grid)
        outer.add_widget(scroll)
        self.add_widget(outer)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def refresh_user(self):
        user = api_client.get_user()
        if user:
            nombre = f"{user.get('nombre', '')} {user.get('primer_apellido', '')}".strip()
            cargo = f"{user.get('cargo_grado', '')} · {user.get('institucion', '')}".strip(' · ')
            self.lbl_welcome.text = f"Bienvenido, {nombre}"
            self.lbl_cargo.text = cargo
            # Rebuild cards with correct manager reference
            self._rebuild_grid()

    def _rebuild_grid(self):
        pass  # Grid already built; manager reference is set at on_enter

    def on_enter(self):
        self.refresh_user()
        # Fix manager references in cards after screen is added to manager
        for child in self.walk():
            if isinstance(child, ModuleCard):
                child.manager_ref = self.manager

    def do_logout(self, *args):
        api_client.clear_session()
        self.manager.current = 'login'
