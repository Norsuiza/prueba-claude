"""Widgets reutilizables con estilo Gobierno de México."""
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp

C_WHITE  = (1, 1, 1, 1)

C_WHITE  = (1, 1, 1, 1)
C_GREEN  = (0.0, 0.408, 0.278, 1)
C_RED    = (0.808, 0.067, 0.149, 1)
C_GRAY   = (0.85, 0.85, 0.85, 1)
C_TEXT   = (0.1, 0.1, 0.1, 1)


class RoundedButton(Button):
    """Botón con bordes redondeados."""
    def __init__(self, bg_color=None, text_color=C_WHITE, radius=dp(10), **kwargs):
        super().__init__(**kwargs)
        bg_color = bg_color or C_GREEN
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.color = text_color
        self._bg_color = bg_color
        self._radius = radius
        with self.canvas.before:
            self._c = Color(*bg_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def set_color(self, color):
        self._c.rgba = color


class HamburgerButton(Button):
    """Botón hamburguesa: 3 líneas horizontales dibujadas en canvas (sin Unicode)."""
    def __init__(self, line_color=C_WHITE, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.text = ''
        with self.canvas.after:
            self._lc = Color(*line_color)
            self._l1 = Rectangle()
            self._l2 = Rectangle()
            self._l3 = Rectangle()
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        lw = self.width * 0.52
        lh = dp(2.5)
        gap = dp(5)
        x = self.center_x - lw / 2
        total = lh * 3 + gap * 2
        y = self.center_y + total / 2 - lh
        self._l1.pos = (x, y);      self._l1.size = (lw, lh)
        y -= lh + gap
        self._l2.pos = (x, y);      self._l2.size = (lw, lh)
        y -= lh + gap
        self._l3.pos = (x, y);      self._l3.size = (lw, lh)


def popup_content(padding=16, spacing=10):
    """BoxLayout con fondo blanco para usar como content en Popup."""
    box = BoxLayout(orientation='vertical', padding=dp(padding), spacing=dp(spacing))
    with box.canvas.before:
        Color(*C_WHITE)
        box._bg = Rectangle(pos=box.pos, size=box.size)
    box.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
             size=lambda w, v: setattr(w._bg, 'size', v))
    return box


def footer_bar():
    """Pie de página estándar para todas las pantallas excepto el chat."""
    lbl = Label(
        text='(c) Dev with love by @NorzCode 2026',
        font_size=dp(10), color=(0.55, 0.55, 0.55, 1),
        size_hint_y=None, height=dp(26), halign='center',
    )
    lbl.bind(size=lbl.setter('text_size'))
    return lbl


def rounded_btn(text, bg=None, color=C_WHITE, height=dp(46), radius=dp(10), **kwargs):
    return RoundedButton(
        text=text, bg_color=bg or C_GREEN, text_color=color,
        radius=radius, size_hint_y=None, height=height,
        font_size=dp(14), bold=True, **kwargs
    )
