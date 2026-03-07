import os
import threading
from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

import sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from mobile.utils import api_client
from mobile.utils.pdf_generator import generate_iph_pdf
from mobile.data.iph_questions import get_question_list

C_WHITE  = (1, 1, 1, 1)
C_BG     = (0.96, 0.96, 0.96, 1)
C_GREEN  = (0.0, 0.408, 0.278, 1)
C_GREEN2 = (0.0, 0.52, 0.35, 1)   # verde más claro para hover
C_RED    = (0.808, 0.067, 0.149, 1)
C_TEXT   = (0.1, 0.1, 0.1, 1)
C_GRAY   = (0.5, 0.5, 0.5, 1)
C_BOT    = (0.92, 0.97, 0.93, 1)  # burbuja bot: verde muy claro
C_USER   = (0.0, 0.408, 0.278, 1) # burbuja usuario: verde gobierno
C_INPUT  = (1, 1, 1, 1)
C_BORDER = (0.82, 0.82, 0.82, 1)


class ChatBubble(BoxLayout):
    def __init__(self, text, is_bot=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = [dp(8), dp(4)]

        bg = C_BOT if is_bot else C_USER
        txt_color = C_TEXT if is_bot else C_WHITE
        align = 'left' if is_bot else 'right'

        lbl = Label(
            text=text, font_size=dp(14),
            color=txt_color,
            halign=align, valign='top',
            markup=True,
            size_hint_x=0.82,
        )
        lbl.bind(width=lambda w, v: setattr(lbl, 'text_size', (v, None)))
        lbl.bind(texture_size=lambda w, v: setattr(lbl, 'height', v[1] + dp(8)))

        bubble = BoxLayout(size_hint_x=0.82, size_hint_y=None, padding=dp(12))
        with bubble.canvas.before:
            Color(*bg)
            bubble._bg = RoundedRectangle(pos=bubble.pos, size=bubble.size, radius=[dp(10)])
        bubble.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                    size=lambda w, v: setattr(w._bg, 'size', v))
        bubble.add_widget(lbl)
        bubble.bind(minimum_height=bubble.setter('height'))

        spacer = Label(size_hint_x=0.18)
        if is_bot:
            self.add_widget(bubble)
            self.add_widget(spacer)
        else:
            self.add_widget(spacer)
            self.add_widget(bubble)

        self.bind(minimum_height=self.setter('height'))


class IPHScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form_data = {}
        self.questions = []
        self.current_index = 0
        self.multiselect_selected = []
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
            orientation='horizontal', size_hint_y=None, height=dp(52),
            padding=[dp(8), dp(6)], spacing=dp(8),
        )
        with hdr.canvas.before:
            Color(*C_GREEN)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                 size=lambda w, v: setattr(w._bg, 'size', v))

        btn_back = Button(
            text='← Inicio', size_hint_x=None, width=dp(80),
            background_color=(0, 0, 0, 0), color=C_WHITE, font_size=dp(13),
        )
        btn_back.bind(on_press=self._confirm_exit)

        self.lbl_section = Label(
            text='IPH · Delitos', font_size=dp(14), bold=True, color=C_WHITE,
        )
        hdr.add_widget(btn_back)
        hdr.add_widget(self.lbl_section)
        outer.add_widget(hdr)

        # Barra de progreso verde
        self.progress_bar = ProgressBar(
            max=100, value=0, size_hint_y=None, height=dp(5),
        )
        outer.add_widget(self.progress_bar)

        self.lbl_progress = Label(
            text='', font_size=dp(10), color=C_GRAY,
            size_hint_y=None, height=dp(18),
        )
        outer.add_widget(self.lbl_progress)

        # Chat
        self.scroll = ScrollView()
        self.chat = GridLayout(
            cols=1, padding=[dp(8), dp(8)], spacing=dp(6),
            size_hint_y=None,
        )
        self.chat.bind(minimum_height=self.chat.setter('height'))
        self.scroll.add_widget(self.chat)
        outer.add_widget(self.scroll)

        # Área de input
        self.input_area = BoxLayout(
            orientation='vertical', size_hint_y=None,
            padding=[dp(10), dp(8)], spacing=dp(6),
        )
        with self.input_area.canvas.before:
            Color(*C_WHITE)
            self.input_area._bg = Rectangle(
                pos=self.input_area.pos, size=self.input_area.size)
        self.input_area.bind(
            pos=lambda w, v: setattr(w._bg, 'pos', v),
            size=lambda w, v: setattr(w._bg, 'size', v),
            minimum_height=self.input_area.setter('height'),
        )
        outer.add_widget(self.input_area)
        self.add_widget(outer)

    # ── Flujo del chatbot ──────────────────────────────────────────────────

    def on_enter(self):
        self.form_data = {}
        self.current_index = 0
        self.chat.clear_widgets()
        self.questions = get_question_list(self.form_data)
        self._bot('¡Hola! Soy el asistente [b]IPH[/b].\nResponde cada pregunta para llenar el informe.\nAl final se generará el PDF oficial.')
        Clock.schedule_once(lambda dt: self._ask(), 0.4)

    def _ask(self):
        self.questions = get_question_list(self.form_data)
        if self.current_index >= len(self.questions):
            self._show_finish()
            return
        q = self.questions[self.current_index]
        total = len(self.questions)
        self.progress_bar.value = int(self.current_index / total * 100)
        self.lbl_progress.text = f'Pregunta {self.current_index + 1} de {total}'
        self.lbl_section.text = q.get('seccion', 'IPH · Delitos')
        self._bot(q['texto'])
        self._render_input(q)

    def _bot(self, text):
        self.chat.add_widget(ChatBubble(text, is_bot=True))
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def _user(self, text):
        self.chat.add_widget(ChatBubble(text, is_bot=False))
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    # ── Renderizado de inputs ──────────────────────────────────────────────

    def _render_input(self, q):
        self.input_area.clear_widgets()
        t = q.get('tipo', 'text')
        if t in ('text', 'date', 'time'):
            self._ui_text(q)
        elif t == 'long_text':
            self._ui_longtext(q)
        elif t == 'yes_no':
            self._ui_yesno(q)
        elif t == 'choice':
            self._ui_choice(q)
        elif t == 'multiselect':
            self._ui_multiselect(q)

    def _ui_text(self, q):
        hint = {'date': 'DD/MM/AAAA', 'time': 'HH:MM'}.get(q['tipo'], '')
        prefill = ''
        if q.get('prefill'):
            u = api_client.get_user()
            if u:
                prefill = u.get(q['prefill'], '')
        ti = TextInput(
            hint_text=hint, text=prefill, multiline=False,
            size_hint_y=None, height=dp(44),
            background_color=C_INPUT, foreground_color=C_TEXT,
            hint_text_color=(0.6, 0.6, 0.6, 1),
            padding=[dp(10), dp(10)], font_size=dp(15),
            cursor_color=C_GREEN,
        )
        btn = self._green_btn('Siguiente →', lambda x: self._submit_text(q, ti.text.strip()))
        self.input_area.add_widget(ti)
        self.input_area.add_widget(btn)
        ti.focus = True

    def _ui_longtext(self, q):
        ti = TextInput(
            hint_text='Escribe aquí...', multiline=True,
            size_hint_y=None, height=dp(100),
            background_color=C_INPUT, foreground_color=C_TEXT,
            hint_text_color=(0.6, 0.6, 0.6, 1),
            padding=[dp(10), dp(10)], font_size=dp(14),
            cursor_color=C_GREEN,
        )
        btn = self._green_btn('Siguiente →', lambda x: self._submit_text(q, ti.text.strip()))
        self.input_area.add_widget(ti)
        self.input_area.add_widget(btn)

    def _ui_yesno(self, q):
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        b_si = Button(text='Sí', background_color=C_GREEN, color=C_WHITE, font_size=dp(16), bold=True)
        b_no = Button(text='No', background_color=C_RED,   color=C_WHITE, font_size=dp(16), bold=True)
        b_si.bind(on_press=lambda x: self._submit_choice(q, 'Sí'))
        b_no.bind(on_press=lambda x: self._submit_choice(q, 'No'))
        row.add_widget(b_si)
        row.add_widget(b_no)
        self.input_area.add_widget(row)

    def _ui_choice(self, q):
        sc = ScrollView(size_hint_y=None, height=min(dp(200), dp(46) * len(q['opciones'])))
        inner = GridLayout(cols=1, spacing=dp(4), size_hint_y=None, padding=[0, dp(2)])
        inner.bind(minimum_height=inner.setter('height'))
        for opt in q['opciones']:
            b = Button(
                text=opt, size_hint_y=None, height=dp(44),
                background_color=C_WHITE, color=C_TEXT,
                font_size=dp(13),
            )
            b.bind(on_press=lambda x, o=opt: self._submit_choice(q, o))
            inner.add_widget(b)
        sc.add_widget(inner)
        self.input_area.add_widget(sc)

    def _ui_multiselect(self, q):
        self.multiselect_selected = []
        self._ms_btns = {}
        sc = ScrollView(size_hint_y=None, height=min(dp(180), dp(44) * len(q['opciones'])))
        inner = GridLayout(cols=1, spacing=dp(4), size_hint_y=None, padding=[0, dp(2)])
        inner.bind(minimum_height=inner.setter('height'))
        for opt in q['opciones']:
            b = Button(
                text=opt, size_hint_y=None, height=dp(42),
                background_color=C_WHITE, color=C_TEXT, font_size=dp(12),
            )
            b.bind(on_press=lambda x, o=opt: self._toggle(o, x))
            inner.add_widget(b)
            self._ms_btns[opt] = b
        sc.add_widget(inner)
        self.input_area.add_widget(sc)
        self.input_area.add_widget(
            self._green_btn('Confirmar selección →', lambda x: self._submit_multi(q))
        )

    def _toggle(self, opt, btn):
        if opt in self.multiselect_selected:
            self.multiselect_selected.remove(opt)
            btn.background_color = C_WHITE
            btn.color = C_TEXT
        else:
            self.multiselect_selected.append(opt)
            btn.background_color = C_GREEN
            btn.color = C_WHITE

    def _green_btn(self, text, callback):
        b = Button(
            text=text, size_hint_y=None, height=dp(46),
            background_color=C_GREEN, color=C_WHITE,
            font_size=dp(15), bold=True,
        )
        b.bind(on_press=callback)
        return b

    # ── Submit ─────────────────────────────────────────────────────────────

    def _submit_text(self, q, val):
        self.form_data[q['campo']] = val or 'N/A'
        self._user(val or 'N/A')
        self.current_index += 1
        Clock.schedule_once(lambda dt: self._ask(), 0.3)

    def _submit_choice(self, q, val):
        self.form_data[q['campo']] = val
        self._user(val)
        self.current_index += 1
        Clock.schedule_once(lambda dt: self._ask(), 0.3)

    def _submit_multi(self, q):
        sel = list(self.multiselect_selected) or ['Ninguno']
        self.form_data[q['campo']] = sel
        self._user(', '.join(sel))
        self.current_index += 1
        Clock.schedule_once(lambda dt: self._ask(), 0.3)

    # ── Finalizar ──────────────────────────────────────────────────────────

    def _show_finish(self):
        self.progress_bar.value = 100
        self.lbl_progress.text = 'Formulario completo'
        self.input_area.clear_widgets()
        self._bot('[b]¡Formulario completado![/b]\nPresiona el botón para generar el PDF oficial.')

        btn_pdf = self._green_btn('Generar PDF oficial', self._generate_pdf)
        btn_new = Button(
            text='Nuevo informe', size_hint_y=None, height=dp(42),
            background_color=(0, 0, 0, 0), color=C_GREEN, font_size=dp(14),
        )
        btn_new.bind(on_press=lambda x: self.on_enter())
        self.input_area.add_widget(btn_pdf)
        self.input_area.add_widget(btn_new)

    def _generate_pdf(self, *a):
        self._bot('Generando PDF, un momento...')
        user = api_client.get_user() or {}

        def _run():
            try:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                out_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'IPH_Reportes')
                os.makedirs(out_dir, exist_ok=True)
                path = os.path.join(out_dir, f'IPH_{ts}.pdf')
                generate_iph_pdf(self.form_data, user, path)
                Clock.schedule_once(lambda dt: self._pdf_ok(path), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._bot(f'Error: {e}'), 0)

        threading.Thread(target=_run, daemon=True).start()

    def _pdf_ok(self, path):
        self._bot(f'[b]PDF generado correctamente.[/b]\nGuardado en:\n{path}')
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        content.add_widget(Label(
            text=f'Archivo guardado:\n{os.path.basename(path)}\n\nCarpeta: Documents/IPH_Reportes',
            color=C_TEXT, font_size=dp(13), halign='center',
            size_hint_y=None, height=dp(70),
        ))
        btn = Button(
            text='Aceptar', size_hint_y=None, height=dp(44),
            background_color=C_GREEN, color=C_WHITE, font_size=dp(14),
        )
        pop = Popup(title='PDF Generado', content=content,
                    size_hint=(0.85, None), height=dp(210))
        btn.bind(on_press=pop.dismiss)
        content.add_widget(btn)
        pop.open()

    def _confirm_exit(self, *a):
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        content.add_widget(Label(
            text='¿Salir del IPH?\nSe perderá el progreso.',
            color=C_TEXT, font_size=dp(14), halign='center',
            size_hint_y=None, height=dp(50),
        ))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        b1 = Button(text='Continuar', background_color=(0.85, 0.85, 0.85, 1), color=C_TEXT)
        b2 = Button(text='Salir', background_color=C_RED, color=C_WHITE)
        row.add_widget(b1)
        row.add_widget(b2)
        content.add_widget(row)
        pop = Popup(title='Salir', content=content,
                    size_hint=(0.8, None), height=dp(190))
        b1.bind(on_press=pop.dismiss)
        b2.bind(on_press=lambda x: (pop.dismiss(), setattr(self.manager, 'current', 'home')))
        pop.open()
