from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

from utils import api_client
from utils.widgets import RoundedButton, rounded_btn, HamburgerButton, footer_bar, popup_content

C_WHITE  = (1, 1, 1, 1)
C_BG     = (0.94, 0.94, 0.94, 1)
C_GREEN  = (0.0, 0.408, 0.278, 1)
C_RED    = (0.808, 0.067, 0.149, 1)
C_TEXT   = (0.1, 0.1, 0.1, 1)
C_GRAY   = (0.5, 0.5, 0.5, 1)
C_LGRAY  = (0.88, 0.88, 0.88, 1)
C_DRAWER = (0.98, 0.98, 0.98, 1)

INSTITUTIONS = [
    'Policía Municipal', 'Policía Estatal', 'Guardia Nacional',
    'Policía Ministerial', 'Policía Federal Ministerial',
    'Policía Mando Único', 'Otra autoridad',
]

MODULES = [
    {'title': 'IPH\nDelitos',      'sub': 'Informe Policial\nHomologado', 'screen': 'iph',  'active': True},
    {'title': 'IPH\nAccidentes',   'sub': 'En desarrollo',                'screen': None,   'active': False},
    {'title': 'Actas\nAdmin.',      'sub': 'En desarrollo',                'screen': None,   'active': False},
    {'title': 'Partes\nDiarios',    'sub': 'En desarrollo',                'screen': None,   'active': False},
    {'title': 'Estadísticas',       'sub': 'En desarrollo',                'screen': None,   'active': False},
    {'title': 'Directorio',         'sub': 'En desarrollo',                'screen': None,   'active': False},
]


# ── Tarjeta de módulo ─────────────────────────────────────────────────────────

class ModuleCard(BoxLayout):
    def __init__(self, title, sub, active, target, mgr_getter, **kwargs):
        super().__init__(orientation='vertical', padding=dp(12), spacing=dp(4), **kwargs)
        self._target = target
        self._mgr = mgr_getter
        self._active = active

        radius = dp(12)
        with self.canvas.before:
            Color(*(C_WHITE if active else (0.95, 0.95, 0.95, 1)))
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
            if active:
                Color(*C_GREEN)
                self._border = RoundedRectangle(
                    pos=(self.x + 0, self.y + 0),
                    size=(dp(4), self.height),
                    radius=[radius, 0, 0, radius],
                )
        self.bind(pos=self._upd, size=self._upd)

        t = Label(
            text=title, font_size=dp(14), bold=active,
            color=C_GREEN if active else C_GRAY,
            halign='center', valign='middle',
            size_hint_y=0.5,
        )
        t.bind(size=t.setter('text_size'))

        s = Label(
            text=sub, font_size=dp(11),
            color=C_TEXT if active else C_GRAY,
            halign='center', valign='top',
            size_hint_y=0.5,
        )
        s.bind(size=s.setter('text_size'))

        self.add_widget(t)
        self.add_widget(s)

    def on_touch_down(self, touch):
        if self._active and self._target and self.collide_point(*touch.pos):
            self._go()
            return True
        return super().on_touch_down(touch)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        if hasattr(self, '_border'):
            self._border.pos = (self.x, self.y)
            self._border.size = (dp(4), self.height)

    def _go(self):
        mgr = self._mgr()
        if mgr:
            mgr.current = self._target


# ── Drawer (menú hamburguesa) ─────────────────────────────────────────────────

class DrawerMenu(BoxLayout):
    def __init__(self, close_cb, logout_cb, profile_cb, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.size_hint = (None, 1)
        self.width = dp(260)
        self._close_cb = close_cb

        with self.canvas.before:
            Color(*C_DRAWER)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v: setattr(self._bg, 'pos', v),
                  size=lambda w, v: setattr(self._bg, 'size', v))

        # Header del drawer
        hdr = BoxLayout(size_hint_y=None, height=dp(130), padding=dp(16), spacing=dp(6),
                        orientation='vertical')
        with hdr.canvas.before:
            Color(*C_GREEN)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                 size=lambda w, v: setattr(w._bg, 'size', v))

        self.lbl_nombre = Label(text='', font_size=dp(16), bold=True, color=C_WHITE,
                                 halign='left', size_hint_y=None, height=dp(26))
        self.lbl_nombre.bind(size=self.lbl_nombre.setter('text_size'))
        self.lbl_cargo = Label(text='', font_size=dp(11), color=(0.85, 1, 0.85, 1),
                                halign='left', size_hint_y=None, height=dp(20))
        self.lbl_cargo.bind(size=self.lbl_cargo.setter('text_size'))
        self.lbl_inst = Label(text='', font_size=dp(11), color=(0.8, 1, 0.8, 1),
                               halign='left', size_hint_y=None, height=dp(20))
        self.lbl_inst.bind(size=self.lbl_inst.setter('text_size'))

        hdr.add_widget(Label(size_hint_y=None, height=dp(8)))
        hdr.add_widget(self.lbl_nombre)
        hdr.add_widget(self.lbl_cargo)
        hdr.add_widget(self.lbl_inst)
        self.add_widget(hdr)

        # Items del menú
        items = [
            ('  Mi Perfil',      profile_cb, C_TEXT),
            ('  Cerrar sesion',  logout_cb,  C_RED),
        ]
        for text, cb, color in items:
            sep = BoxLayout(size_hint_y=None, height=dp(1))
            with sep.canvas.before:
                Color(*C_LGRAY)
                sep._bg = Rectangle(pos=sep.pos, size=sep.size)
            sep.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                     size=lambda w, v: setattr(w._bg, 'size', v))
            self.add_widget(sep)

            btn = Button(
                text=text, size_hint_y=None, height=dp(56),
                background_color=(0, 0, 0, 0),
                background_normal='', background_down='',
                color=color, font_size=dp(15), halign='left',
            )
            btn.bind(size=btn.setter('text_size'))
            btn.bind(on_press=lambda x, f=cb: (close_cb(), f()))
            self.add_widget(btn)

        self.add_widget(Label())  # spacer

    def refresh_user(self):
        user = api_client.get_user()
        if user:
            nombre = f"{user.get('nombre', '')} {user.get('primer_apellido', '')}".strip()
            self.lbl_nombre.text = nombre
            self.lbl_cargo.text = user.get('cargo_grado', '')
            self.lbl_inst.text = user.get('institucion', '')

    def open(self):
        self.refresh_user()
        Animation(x=0, duration=0.22, t='out_cubic').start(self)

    def close(self):
        Animation(x=-self.width, duration=0.18, t='in_cubic').start(self)


# ── Pantalla principal ────────────────────────────────────────────────────────

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._drawer_open = False
        self._build_ui()

    def _build_ui(self):
        root = FloatLayout()

        # Fondo
        with root.canvas.before:
            Color(*C_BG)
            root._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                  size=lambda w, v: setattr(w._bg, 'size', v))

        # ── Contenido principal ──
        main = BoxLayout(orientation='vertical', size_hint=(1, 1))

        # Header
        hdr = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60),
                        padding=[dp(8), dp(8)], spacing=dp(8))
        with hdr.canvas.before:
            Color(*C_GREEN)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                 size=lambda w, v: setattr(w._bg, 'size', v))

        # Botón hamburguesa
        btn_ham = HamburgerButton(
            line_color=C_WHITE, size_hint_x=None, width=dp(48),
        )
        btn_ham.bind(on_press=lambda x: self._toggle_drawer())

        title_box = BoxLayout(orientation='vertical')
        self.lbl_name = Label(text='ChatPoli', font_size=dp(16), bold=True,
                               color=C_WHITE, halign='left')
        self.lbl_name.bind(size=self.lbl_name.setter('text_size'))
        self.lbl_sub = Label(text='Culiacán, Sinaloa', font_size=dp(11),
                              color=(0.85, 1, 0.85, 1), halign='left')
        self.lbl_sub.bind(size=self.lbl_sub.setter('text_size'))
        title_box.add_widget(self.lbl_name)
        title_box.add_widget(self.lbl_sub)

        hdr.add_widget(btn_ham)
        hdr.add_widget(title_box)
        main.add_widget(hdr)

        # Subtítulo módulos
        main.add_widget(Label(
            text='MÓDULOS DISPONIBLES', font_size=dp(10), bold=True,
            color=C_GRAY, size_hint_y=None, height=dp(28),
        ))

        # Grid de módulos
        scroll = ScrollView()
        grid = GridLayout(
            cols=2, padding=[dp(14), dp(6)], spacing=dp(12),
            size_hint_y=None,
        )
        grid.bind(minimum_height=grid.setter('height'))

        for m in MODULES:
            card = ModuleCard(
                title=m['title'], sub=m['sub'],
                active=m['active'], target=m['screen'],
                mgr_getter=lambda: self.manager,
                size_hint_y=None, height=dp(110),
            )
            grid.add_widget(card)

        scroll.add_widget(grid)
        main.add_widget(scroll)
        main.add_widget(footer_bar())
        root.add_widget(main)

        # ── Overlay oscuro (cierra el drawer al tocar) ──
        # size (0,0) cuando cerrado para no bloquear toques
        self._overlay = Button(
            size_hint=(None, None), size=(0, 0),
            background_color=(0, 0, 0, 0.45),
            background_normal='', background_down='',
            opacity=0,
        )
        self._overlay.bind(on_press=lambda x: self._close_drawer())
        root.add_widget(self._overlay)

        # ── Drawer ──
        self._drawer = DrawerMenu(
            close_cb=self._close_drawer,
            logout_cb=self._do_logout,
            profile_cb=self._show_profile,
            pos=(-dp(260), 0),
        )
        root.add_widget(self._drawer)

        self.add_widget(root)

    # ── Drawer ──────────────────────────────────────────────────────────────

    def _toggle_drawer(self):
        if self._drawer_open:
            self._close_drawer()
        else:
            self._open_drawer()

    def _open_drawer(self):
        self._drawer_open = True
        self._overlay.size_hint = (1, 1)
        self._overlay.opacity = 1
        self._drawer.open()

    def _close_drawer(self):
        self._drawer_open = False
        self._overlay.size_hint = (None, None)
        self._overlay.size = (0, 0)
        self._overlay.opacity = 0
        self._drawer.close()

    # ── Perfil ───────────────────────────────────────────────────────────────

    def _show_profile(self):
        user = api_client.get_user() or {}

        content = popup_content(padding=14, spacing=6)
        scroll = ScrollView()  # size_hint_y=1: ocupa espacio disponible entre btns
        form = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        def _lbl(t):
            l = Label(text=t, color=C_GRAY, font_size=dp(11),
                      size_hint_y=None, height=dp(18), halign='left')
            l.bind(size=l.setter('text_size'))
            return l

        def _inp(hint, val=''):
            return TextInput(
                hint_text=hint, text=val, multiline=False,
                size_hint_y=None, height=dp(42),
                background_color=C_WHITE, foreground_color=C_TEXT,
                padding=[dp(10), dp(10)], font_size=dp(13),
            )

        fields = [
            ('Primer apellido', 'primer_apellido'), ('Segundo apellido', 'segundo_apellido'),
            ('Nombre(s)', 'nombre'), ('Adscripción', 'adscripcion'),
            ('Cargo / Grado', 'cargo_grado'), ('No. Placa/Empleado', 'no_placa'),
        ]
        inputs = {}
        for label, key in fields:
            form.add_widget(_lbl(label))
            inp = _inp(label, user.get(key, ''))
            inputs[key] = inp
            form.add_widget(inp)

        form.add_widget(_lbl('Institución'))
        spinner = Spinner(
            text=user.get('institucion', 'Policía Municipal'),
            values=INSTITUTIONS,
            size_hint_y=None, height=dp(42),
            background_color=(0.95, 0.95, 0.95, 1), color=C_TEXT, font_size=dp(13),
        )
        form.add_widget(spinner)
        scroll.add_widget(form)
        content.add_widget(scroll)

        lbl_err = Label(text='', color=C_RED, font_size=dp(12),
                        size_hint_y=None, height=dp(24))
        content.add_widget(lbl_err)

        btn_save = rounded_btn('GUARDAR', height=dp(46))
        btn_cancel = rounded_btn('Cancelar', bg=(0.7, 0.7, 0.7, 1), height=dp(40))
        content.add_widget(btn_save)
        content.add_widget(btn_cancel)

        pop = Popup(title='Mi Perfil', content=content,
                    size_hint=(0.92, 0.88))

        def save(*a):
            data = {k: v.text.strip() for k, v in inputs.items()}
            data['institucion'] = spinner.text
            lbl_err.text = 'Guardando...'
            api_client.update_profile(data,
                on_success=lambda u: Clock.schedule_once(lambda dt: (
                    setattr(lbl_err, 'text', 'Guardado correctamente'),
                    self.refresh_user(),
                    pop.dismiss(),
                ), 0),
                on_error=lambda e: Clock.schedule_once(
                    lambda dt: setattr(lbl_err, 'text', e), 0),
            )

        btn_save.bind(on_press=save)
        btn_cancel.bind(on_press=pop.dismiss)
        pop.open()

    # ── Misc ─────────────────────────────────────────────────────────────────

    def refresh_user(self):
        user = api_client.get_user()
        if user:
            nombre = f"{user.get('nombre', '')} {user.get('primer_apellido', '')}".strip()
            self.lbl_name.text = nombre or 'ChatPoli'
            cargo = user.get('cargo_grado', '')
            inst = user.get('institucion', '')
            self.lbl_sub.text = f"{cargo} · {inst}".strip(' · ') or 'Culiacán, Sinaloa'

    def on_enter(self):
        self.refresh_user()
        self._close_drawer()

    def _do_logout(self):
        api_client.clear_session()
        self.manager.current = 'login'
