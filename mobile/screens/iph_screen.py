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

C_DARK = (0.102, 0.102, 0.180, 1)
C_CARD = (0.086, 0.129, 0.243, 1)
C_GOLD = (0.910, 0.725, 0.137, 1)
C_WHITE = (0.918, 0.918, 0.918, 1)
C_BOT_BG = (0.15, 0.20, 0.35, 1)
C_USER_BG = (0.55, 0.42, 0.08, 1)
C_GREEN = (0.2, 0.72, 0.3, 1)


class ChatBubble(BoxLayout):
    def __init__(self, text, is_bot=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = [dp(8), dp(4)]
        self.spacing = dp(4)

        bg_color = C_BOT_BG if is_bot else C_USER_BG
        align = 'left' if is_bot else 'right'

        lbl = Label(
            text=text,
            font_size=dp(14),
            color=C_WHITE,
            halign=align,
            valign='top',
            size_hint_x=0.85,
            markup=True,
        )
        lbl.bind(texture_size=lambda w, v: setattr(lbl, 'height', v[1] + dp(16)))
        lbl.bind(width=lambda w, v: setattr(lbl, 'text_size', (v, None)))

        bubble = BoxLayout(size_hint_x=0.85, size_hint_y=None, padding=dp(10))
        with bubble.canvas.before:
            Color(*bg_color)
            bubble._bg = RoundedRectangle(pos=bubble.pos, size=bubble.size, radius=[dp(8)])
        bubble.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                    size=lambda w, v: setattr(w._bg, 'size', v))
        bubble.add_widget(lbl)
        bubble.bind(minimum_height=bubble.setter('height'))

        if is_bot:
            self.add_widget(bubble)
            self.add_widget(Label(size_hint_x=0.15))
        else:
            self.add_widget(Label(size_hint_x=0.15))
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
            text='← Inicio', size_hint_x=None, width=dp(80),
            background_color=(0, 0, 0, 0), color=C_GOLD, font_size=dp(14),
        )
        btn_back.bind(on_press=self._confirm_exit)

        self.lbl_section = Label(
            text='IPH · Delitos', font_size=dp(15), bold=True, color=C_WHITE,
        )
        header.add_widget(btn_back)
        header.add_widget(self.lbl_section)
        outer.add_widget(header)

        # Progress bar
        self.progress_bar = ProgressBar(
            max=100, value=0,
            size_hint_y=None, height=dp(6),
        )
        outer.add_widget(self.progress_bar)

        # Progress label
        self.lbl_progress = Label(
            text='', font_size=dp(11), color=C_GOLD,
            size_hint_y=None, height=dp(20),
        )
        outer.add_widget(self.lbl_progress)

        # Chat area
        self.scroll = ScrollView(size_hint_y=1)
        self.chat_layout = GridLayout(
            cols=1, padding=[dp(8), dp(8)], spacing=dp(8),
            size_hint_y=None,
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.scroll.add_widget(self.chat_layout)
        outer.add_widget(self.scroll)

        # Input area (dynamic)
        self.input_area = BoxLayout(
            orientation='vertical', size_hint_y=None,
            padding=[dp(8), dp(8)], spacing=dp(6),
        )
        with self.input_area.canvas.before:
            Color(*C_CARD)
            self.input_area._bg = Rectangle(pos=self.input_area.pos, size=self.input_area.size)
        self.input_area.bind(
            pos=lambda w, v: setattr(w._bg, 'pos', v),
            size=lambda w, v: setattr(w._bg, 'size', v),
            minimum_height=self.input_area.setter('height'),
        )
        outer.add_widget(self.input_area)
        self.add_widget(outer)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_enter(self):
        self.form_data = {}
        self.current_index = 0
        self.chat_layout.clear_widgets()
        self.questions = get_question_list(self.form_data)
        self._add_bot_message(
            '[b]Hola, soy el asistente IPH.[/b]\n'
            'Te haré preguntas para llenar el Informe Policial Homologado.\n'
            'Responde cada pregunta y al final se generará el PDF.'
        )
        Clock.schedule_once(lambda dt: self._ask_current(), 0.5)

    def _ask_current(self):
        self.questions = get_question_list(self.form_data)

        if self.current_index >= len(self.questions):
            self._show_finish()
            return

        q = self.questions[self.current_index]
        total = len(self.questions)
        progress = int((self.current_index / total) * 100)
        self.progress_bar.value = progress
        self.lbl_progress.text = f'Pregunta {self.current_index + 1} de {total}'
        self.lbl_section.text = q.get('seccion', 'IPH')

        self._add_bot_message(q['texto'])
        self._render_input(q)

    def _add_bot_message(self, text):
        bubble = ChatBubble(text, is_bot=True)
        self.chat_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: self._scroll_bottom(), 0.1)

    def _add_user_message(self, text):
        bubble = ChatBubble(text, is_bot=False)
        self.chat_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: self._scroll_bottom(), 0.1)

    def _scroll_bottom(self):
        self.scroll.scroll_y = 0

    def _render_input(self, q):
        self.input_area.clear_widgets()
        tipo = q.get('tipo', 'text')

        if tipo in ('text', 'date', 'time'):
            self._render_text_input(q)
        elif tipo == 'long_text':
            self._render_long_text(q)
        elif tipo == 'yes_no':
            self._render_yes_no(q)
        elif tipo == 'choice':
            self._render_choice(q)
        elif tipo == 'multiselect':
            self._render_multiselect(q)

    def _render_text_input(self, q):
        hint = {'date': 'DD/MM/AAAA', 'time': 'HH:MM'}.get(q['tipo'], '')
        prefill = ''
        if q.get('prefill'):
            user = api_client.get_user()
            if user:
                prefill = user.get(q['prefill'], '')

        ti = TextInput(
            hint_text=hint, text=prefill, multiline=False,
            size_hint_y=None, height=dp(44),
            background_color=C_DARK, foreground_color=C_WHITE,
            hint_text_color=(0.5, 0.5, 0.5, 1), padding=[dp(10), dp(10)],
            font_size=dp(16),
        )
        btn = Button(
            text='Siguiente →', size_hint_y=None, height=dp(44),
            background_color=C_GOLD, color=(0.1, 0.1, 0.1, 1),
            font_size=dp(16), bold=True,
        )
        btn.bind(on_press=lambda x: self._submit_text(q, ti.text.strip()))
        self.input_area.add_widget(ti)
        self.input_area.add_widget(btn)
        ti.focus = True

    def _render_long_text(self, q):
        ti = TextInput(
            hint_text='Escribe aquí...', multiline=True,
            size_hint_y=None, height=dp(100),
            background_color=C_DARK, foreground_color=C_WHITE,
            hint_text_color=(0.5, 0.5, 0.5, 1), padding=[dp(10), dp(10)],
            font_size=dp(14),
        )
        btn = Button(
            text='Siguiente →', size_hint_y=None, height=dp(44),
            background_color=C_GOLD, color=(0.1, 0.1, 0.1, 1),
            font_size=dp(16), bold=True,
        )
        btn.bind(on_press=lambda x: self._submit_text(q, ti.text.strip()))
        self.input_area.add_widget(ti)
        self.input_area.add_widget(btn)

    def _render_yes_no(self, q):
        row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_si = Button(
            text='Sí', background_color=C_GREEN, color=C_WHITE,
            font_size=dp(16), bold=True,
        )
        btn_no = Button(
            text='No', background_color=(0.6, 0.1, 0.1, 1), color=C_WHITE,
            font_size=dp(16), bold=True,
        )
        btn_si.bind(on_press=lambda x: self._submit_choice(q, 'Sí'))
        btn_no.bind(on_press=lambda x: self._submit_choice(q, 'No'))
        row.add_widget(btn_si)
        row.add_widget(btn_no)
        self.input_area.add_widget(row)

    def _render_choice(self, q):
        scroll = ScrollView(size_hint_y=None, height=min(dp(200), dp(50) * len(q['opciones'])))
        inner = GridLayout(cols=1, spacing=dp(6), size_hint_y=None, padding=[0, dp(4)])
        inner.bind(minimum_height=inner.setter('height'))
        for opt in q['opciones']:
            btn = Button(
                text=opt, size_hint_y=None, height=dp(44),
                background_color=C_CARD, color=C_WHITE, font_size=dp(14),
            )
            btn.bind(on_press=lambda x, o=opt: self._submit_choice(q, o))
            inner.add_widget(btn)
        scroll.add_widget(inner)
        self.input_area.add_widget(scroll)

    def _render_multiselect(self, q):
        self.multiselect_selected = []
        self._ms_buttons = {}

        scroll = ScrollView(size_hint_y=None, height=min(dp(180), dp(46) * len(q['opciones'])))
        inner = GridLayout(cols=1, spacing=dp(4), size_hint_y=None, padding=[0, dp(2)])
        inner.bind(minimum_height=inner.setter('height'))

        for opt in q['opciones']:
            btn = Button(
                text=opt, size_hint_y=None, height=dp(42),
                background_color=C_CARD, color=C_WHITE, font_size=dp(13),
            )
            btn.bind(on_press=lambda x, o=opt: self._toggle_multiselect(o, x))
            inner.add_widget(btn)
            self._ms_buttons[opt] = btn

        scroll.add_widget(inner)
        self.input_area.add_widget(scroll)

        btn_confirm = Button(
            text='Confirmar selección →', size_hint_y=None, height=dp(44),
            background_color=C_GOLD, color=(0.1, 0.1, 0.1, 1),
            font_size=dp(15), bold=True,
        )
        btn_confirm.bind(on_press=lambda x: self._submit_multiselect(q))
        self.input_area.add_widget(btn_confirm)

    def _toggle_multiselect(self, opt, btn):
        if opt in self.multiselect_selected:
            self.multiselect_selected.remove(opt)
            btn.background_color = C_CARD
        else:
            self.multiselect_selected.append(opt)
            btn.background_color = (0.3, 0.55, 0.15, 1)

    def _submit_text(self, q, value):
        if not value:
            value = 'N/A'
        self.form_data[q['campo']] = value
        self._add_user_message(value)
        self.current_index += 1
        Clock.schedule_once(lambda dt: self._ask_current(), 0.3)

    def _submit_choice(self, q, value):
        self.form_data[q['campo']] = value
        self._add_user_message(value)
        self.current_index += 1
        Clock.schedule_once(lambda dt: self._ask_current(), 0.3)

    def _submit_multiselect(self, q):
        selected = list(self.multiselect_selected)
        if not selected:
            selected = ['Ninguno']
        self.form_data[q['campo']] = selected
        self._add_user_message(', '.join(selected))
        self.current_index += 1
        Clock.schedule_once(lambda dt: self._ask_current(), 0.3)

    def _show_finish(self):
        self.progress_bar.value = 100
        self.lbl_progress.text = 'Formulario completo'
        self.input_area.clear_widgets()

        self._add_bot_message(
            '[b]¡Formulario completado![/b]\n'
            'Presiona el botón para generar el PDF del IPH.'
        )

        btn_pdf = Button(
            text='Generar PDF', size_hint_y=None, height=dp(54),
            background_color=C_GOLD, color=(0.1, 0.1, 0.1, 1),
            font_size=dp(18), bold=True,
        )
        btn_pdf.bind(on_press=self._generate_pdf)

        btn_new = Button(
            text='Nuevo informe', size_hint_y=None, height=dp(44),
            background_color=C_CARD, color=C_WHITE, font_size=dp(15),
        )
        btn_new.bind(on_press=lambda x: self.on_enter())

        self.input_area.add_widget(btn_pdf)
        self.input_area.add_widget(btn_new)

    def _generate_pdf(self, *args):
        self._add_bot_message('Generando PDF, espera un momento...')
        user = api_client.get_user() or {}

        def _run():
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'IPH_{timestamp}.pdf'
                # Guardar en carpeta Documentos/IPH (o Escritorio en Android)
                home = os.path.expanduser('~')
                out_dir = os.path.join(home, 'Documents', 'IPH_Reportes')
                os.makedirs(out_dir, exist_ok=True)
                output_path = os.path.join(out_dir, filename)
                generate_iph_pdf(self.form_data, user, output_path)
                Clock.schedule_once(lambda dt: self._on_pdf_done(output_path), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._on_pdf_error(str(e)), 0)

        threading.Thread(target=_run, daemon=True).start()

    def _on_pdf_done(self, path):
        self._add_bot_message(f'[b]PDF generado correctamente.[/b]\nGuardado en:\n{path}')
        self._show_pdf_popup(path)

    def _on_pdf_error(self, msg):
        self._add_bot_message(f'Error al generar PDF: {msg}')

    def _show_pdf_popup(self, path):
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        content.add_widget(Label(
            text=f'PDF guardado en:\n{path}',
            color=C_WHITE, font_size=dp(12),
            halign='center', size_hint_y=None, height=dp(60),
        ))
        btn_ok = Button(
            text='Aceptar', size_hint_y=None, height=dp(44),
            background_color=C_GOLD, color=(0.1, 0.1, 0.1, 1),
        )
        content.add_widget(btn_ok)
        popup = Popup(
            title='IPH Generado',
            content=content,
            size_hint=(0.85, None), height=dp(200),
            background_color=C_CARD,
            title_color=C_GOLD,
        )
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def _confirm_exit(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        content.add_widget(Label(
            text='¿Salir del IPH?\nSe perderá el progreso actual.',
            color=C_WHITE, font_size=dp(14),
            halign='center', size_hint_y=None, height=dp(60),
        ))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        btn_cancel = Button(text='Continuar', background_color=C_CARD, color=C_WHITE)
        btn_exit = Button(text='Salir', background_color=(0.7, 0.1, 0.1, 1), color=C_WHITE)
        row.add_widget(btn_cancel)
        row.add_widget(btn_exit)
        content.add_widget(row)
        popup = Popup(
            title='Salir del IPH',
            content=content,
            size_hint=(0.8, None), height=dp(200),
            background_color=C_CARD, title_color=C_GOLD,
        )
        btn_cancel.bind(on_press=popup.dismiss)
        btn_exit.bind(on_press=lambda x: (popup.dismiss(), setattr(self.manager, 'current', 'home')))
        popup.open()
