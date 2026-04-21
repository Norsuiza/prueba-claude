import os
import shutil
import calendar as _cal
from datetime import datetime

_MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

from utils import api_client
from utils.pdf_generator import generate_iph_pdf
from utils.widgets import RoundedButton, rounded_btn, popup_content
from data.iph_questions import get_question_list

C_WHITE  = (1, 1, 1, 1)
C_BG     = (0.96, 0.96, 0.96, 1)
C_GREEN  = (0.0, 0.408, 0.278, 1)
C_RED    = (0.808, 0.067, 0.149, 1)
C_TEXT   = (0.1, 0.1, 0.1, 1)
C_GRAY   = (0.5, 0.5, 0.5, 1)
C_BOT    = (0.90, 0.96, 0.91, 1)
C_INPUT  = (1, 1, 1, 1)
C_CHOICE = (0.96, 0.96, 0.96, 1)


class ChatBubble(BoxLayout):
    def __init__(self, text, is_bot=True, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None,
                         padding=[dp(8), dp(4)], **kwargs)
        bg = C_BOT if is_bot else C_GREEN
        tc = C_TEXT if is_bot else C_WHITE

        lbl = Label(
            text=text, font_size=dp(14), color=tc,
            halign='left' if is_bot else 'right',
            valign='top', markup=True, size_hint_x=1, size_hint_y=None,
        )
        lbl.bind(width=lambda w, v: setattr(lbl, 'text_size', (v, None)))
        lbl.bind(texture_size=lambda w, v: setattr(lbl, 'height', v[1] + dp(6)))

        bubble = BoxLayout(size_hint_x=0.82, size_hint_y=None,
                           padding=[dp(12), dp(8)], spacing=0)
        with bubble.canvas.before:
            Color(*bg)
            bubble._bg = RoundedRectangle(pos=bubble.pos, size=bubble.size,
                                           radius=[dp(12)])
        bubble.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                    size=lambda w, v: setattr(w._bg, 'size', v))
        bubble.add_widget(lbl)
        bubble.bind(minimum_height=bubble.setter('height'))

        sp = Label(size_hint_x=0.18)
        if is_bot:
            self.add_widget(bubble); self.add_widget(sp)
        else:
            self.add_widget(sp); self.add_widget(bubble)
        self.bind(minimum_height=self.setter('height'))


class IPHScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form_data = {}
        self.questions = []
        self.current_index = 0
        self.multiselect_selected = []
        self._chat_log = []  # [(widget, question_index)]
        self._build_ui()

    def _build_ui(self):
        with self.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v: setattr(self._bg, 'pos', v),
                  size=lambda w, v: setattr(self._bg, 'size', v))

        outer = BoxLayout(orientation='vertical')

        # ── Header ────────────────────────────────────────────────────────────
        hdr = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(52),
                        padding=[dp(8), dp(6)], spacing=dp(8))
        with hdr.canvas.before:
            Color(*C_GREEN)
            hdr._bg = Rectangle(pos=hdr.pos, size=hdr.size)
        hdr.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                 size=lambda w, v: setattr(w._bg, 'size', v))

        btn_back = Button(
            text='< Inicio', size_hint_x=None, width=dp(80),
            background_color=(0, 0, 0, 0), background_normal='', background_down='',
            color=C_WHITE, font_size=dp(13),
        )
        btn_back.bind(on_press=self._confirm_exit)

        self.lbl_section = Label(text='IPH - Delitos', font_size=dp(14),
                                  bold=True, color=C_WHITE)

        btn_reload = Button(
            text='[R]', size_hint_x=None, width=dp(44),
            background_color=(0, 0, 0, 0), background_normal='', background_down='',
            color=C_WHITE, font_size=dp(13),
        )
        btn_reload.bind(on_press=self._confirm_reset)

        hdr.add_widget(btn_back)
        hdr.add_widget(self.lbl_section)
        hdr.add_widget(btn_reload)
        outer.add_widget(hdr)

        # ── Barra de progreso ─────────────────────────────────────────────────
        prog_row = BoxLayout(size_hint_y=None, height=dp(28),
                             padding=[dp(10), dp(2)], spacing=dp(8))
        with prog_row.canvas.before:
            Color(*C_WHITE)
            prog_row._bg = Rectangle(pos=prog_row.pos, size=prog_row.size)
        prog_row.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                      size=lambda w, v: setattr(w._bg, 'size', v))

        self.lbl_progress = Label(
            text='Iniciando...', font_size=dp(10), color=C_GRAY,
            size_hint_x=None, width=dp(120), halign='left',
        )
        self.lbl_progress.bind(size=self.lbl_progress.setter('text_size'))

        bar_outer = BoxLayout(size_hint_y=None, height=dp(8))
        with bar_outer.canvas.before:
            Color(0.88, 0.88, 0.88, 1)
            bar_outer._bg = RoundedRectangle(pos=bar_outer.pos, size=bar_outer.size,
                                              radius=[dp(4)])
        bar_outer.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                       size=lambda w, v: setattr(w._bg, 'size', v))

        self._bar_outer = bar_outer
        self._bar_fill = BoxLayout(size_hint_x=None, size_hint_y=1, width=0)
        with self._bar_fill.canvas.before:
            Color(*C_GREEN)
            self._bar_fill._bg = RoundedRectangle(
                pos=self._bar_fill.pos, size=self._bar_fill.size, radius=[dp(4)])
        self._bar_fill.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                            size=lambda w, v: setattr(w._bg, 'size', v))

        bar_outer.add_widget(self._bar_fill)
        bar_outer.add_widget(Label())

        self.lbl_pct = Label(
            text='0%', font_size=dp(10), bold=True, color=C_GREEN,
            size_hint_x=None, width=dp(38), halign='right',
        )
        self.lbl_pct.bind(size=self.lbl_pct.setter('text_size'))

        prog_row.add_widget(self.lbl_progress)
        prog_row.add_widget(bar_outer)
        prog_row.add_widget(self.lbl_pct)
        outer.add_widget(prog_row)

        # ── Chat ──────────────────────────────────────────────────────────────
        self.scroll = ScrollView()
        self.chat = GridLayout(cols=1, padding=[dp(8), dp(8)], spacing=dp(6),
                                size_hint_y=None)
        self.chat.bind(minimum_height=self.chat.setter('height'))
        self.scroll.add_widget(self.chat)
        outer.add_widget(self.scroll)

        # ── Input area ────────────────────────────────────────────────────────
        self.input_area = BoxLayout(
            orientation='vertical', size_hint_y=None,
            padding=[dp(10), dp(8)], spacing=dp(6),
        )
        with self.input_area.canvas.before:
            Color(*C_WHITE)
            self.input_area._bg = Rectangle(pos=self.input_area.pos,
                                             size=self.input_area.size)
        self.input_area.bind(
            pos=lambda w, v: setattr(w._bg, 'pos', v),
            size=lambda w, v: setattr(w._bg, 'size', v),
            minimum_height=self.input_area.setter('height'),
        )
        outer.add_widget(self.input_area)
        self.add_widget(outer)

    # ── Progreso ──────────────────────────────────────────────────────────────

    def _update_progress(self):
        total = len(self.questions)
        if total == 0:
            return
        done = min(self.current_index, total)
        if done >= total:
            pct = 100
            self.lbl_progress.text = '¡Formulario completo!'
        else:
            pct = int(done / total * 100)
            self.lbl_progress.text = f'Pregunta {done + 1} de {total}'
        self._bar_fill.width = self._bar_outer.width * (pct / 100)
        self.lbl_pct.text = f'{pct}%'

    # ── Flujo chatbot ─────────────────────────────────────────────────────────

    def on_enter(self):
        self.form_data = {}
        self.current_index = 0
        self._chat_log = []
        self.chat.clear_widgets()
        self.questions = get_question_list(self.form_data)
        self._update_progress()
        self._bot('¡Hola! Soy el asistente [b]IPH[/b].\n'
                  'Responde cada pregunta para llenar el informe.\n'
                  'Al final se generara el PDF oficial.')
        Clock.schedule_once(lambda dt: self._ask(), 0.4)

    def _ask(self):
        self.questions = get_question_list(self.form_data)
        if self.current_index >= len(self.questions):
            self._show_finish()
            return
        q = self.questions[self.current_index]
        self._update_progress()
        self.lbl_section.text = q.get('seccion', 'IPH - Delitos')
        self._bot(q['texto'], qi=self.current_index)
        self._render_input(q)

    def _bot(self, text, qi=None):
        bubble = ChatBubble(text, is_bot=True)
        self.chat.add_widget(bubble)
        if qi is not None:
            self._chat_log.append((bubble, qi))
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def _user_msg(self, text, qi=None):
        if qi is not None:
            wrapper = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(1))
            wrapper.bind(minimum_height=wrapper.setter('height'))

            bubble = ChatBubble(text, is_bot=False)
            bubble.size_hint_x = 0.88

            pencil_col = BoxLayout(
                orientation='vertical', size_hint_x=0.12, size_hint_y=None,
                padding=[0, dp(4)],
            )
            pencil_col.bind(minimum_height=pencil_col.setter('height'))
            pencil_btn = Button(
                text='Ed', size_hint_y=None, height=dp(30),
                background_color=(0, 0, 0, 0), background_normal='',
                background_down='', color=C_GRAY, font_size=dp(11),
            )
            pencil_btn.bind(on_press=lambda x, q=qi: self._confirm_edit(q))
            pencil_col.add_widget(pencil_btn)

            wrapper.add_widget(pencil_col)
            wrapper.add_widget(bubble)
            self.chat.add_widget(wrapper)
            self._chat_log.append((wrapper, qi))
        else:
            self.chat.add_widget(ChatBubble(text, is_bot=False))
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    # ── Inputs ────────────────────────────────────────────────────────────────

    def _render_input(self, q):
        self.input_area.clear_widgets()
        t = q.get('tipo', 'text')
        if t == 'text':
            self._ui_text(q)
        elif t == 'date':
            self._ui_date(q)
        elif t == 'time':
            self._ui_time(q)
        elif t == 'long_text':
            self._ui_longtext(q)
        elif t == 'yes_no':
            self._ui_yesno(q)
        elif t == 'choice':
            self._ui_choice(q)
        elif t == 'multiselect':
            self._ui_multiselect(q)
        elif t == 'estado_mx':
            self._ui_estado_mx(q)
        elif t == 'municipio_mx':
            self._ui_municipio_mx(q)
        elif t == 'coordinates':
            self._ui_coordinates(q)

    def _ui_text(self, q):
        prefill = ''
        if q.get('prefill'):
            u = api_client.get_user()
            if u:
                prefill = u.get(q['prefill'], '')
        ti = TextInput(
            text=prefill, multiline=False,
            size_hint_y=None, height=dp(44),
            background_color=C_INPUT, foreground_color=C_TEXT,
            hint_text_color=(0.6, 0.6, 0.6, 1),
            padding=[dp(10), dp(10)], font_size=dp(15),
            cursor_color=C_GREEN,
        )
        btn = rounded_btn('Siguiente >', height=dp(46),
                          on_press=lambda x: self._submit_text(q, ti.text.strip()))
        self.input_area.add_widget(ti)
        self.input_area.add_widget(btn)

    def _ui_time(self, q):
        now = datetime.now()
        state = {'h': now.hour, 'm': now.minute}

        lbl = Label(
            text=f'{state["h"]:02d} : {state["m"]:02d}',
            font_size=dp(38), bold=True, color=C_GREEN,
            size_hint_y=None, height=dp(54), halign='center',
        )
        lbl.bind(size=lbl.setter('text_size'))

        def refresh():
            lbl.text = f'{state["h"]:02d} : {state["m"]:02d}'

        btn_now = rounded_btn('Usar hora actual', height=dp(36))

        def _set_now(x):
            n = datetime.now()
            state['h'] = n.hour
            state['m'] = n.minute
            refresh()

        btn_now.bind(on_press=_set_now)

        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
        for label, key, delta in [('-1h', 'h', -1), ('+1h', 'h', 1),
                                   ('-5m', 'm', -5), ('+5m', 'm', 5)]:
            b = RoundedButton(text=label, bg_color=C_GREEN, text_color=C_WHITE,
                              radius=dp(8), size_hint_y=None, height=dp(46),
                              font_size=dp(14))

            def _tap(x, k=key, d=delta):
                if k == 'h':
                    state['h'] = (state['h'] + d) % 24
                else:
                    state['m'] = (state['m'] + d) % 60
                refresh()

            b.bind(on_press=_tap)
            row.add_widget(b)

        self.input_area.add_widget(lbl)
        self.input_area.add_widget(btn_now)
        self.input_area.add_widget(row)
        self.input_area.add_widget(
            rounded_btn('Siguiente >', height=dp(46),
                        on_press=lambda x: self._submit_text(
                            q, f'{state["h"]:02d}:{state["m"]:02d}'))
        )

    def _ui_date(self, q):
        now = datetime.now()
        state = {'year': now.year, 'month': now.month, 'day': now.day}

        def fmt():
            return f'{state["day"]:02d}/{state["month"]:02d}/{state["year"]}'

        lbl = Label(
            text=fmt(), font_size=dp(32), bold=True, color=C_GREEN,
            size_hint_y=None, height=dp(50), halign='center',
        )
        lbl.bind(size=lbl.setter('text_size'))

        btn_cal = rounded_btn('Abrir calendario', height=dp(44),
                              on_press=lambda x: self._open_calendar(state, lbl, fmt))
        self.input_area.add_widget(lbl)
        self.input_area.add_widget(btn_cal)
        self.input_area.add_widget(
            rounded_btn('Siguiente >', height=dp(46),
                        on_press=lambda x: self._submit_text(q, fmt()))
        )

    def _open_calendar(self, state, lbl_date, fmt):
        content = BoxLayout(orientation='vertical', spacing=dp(4), padding=[dp(4), dp(4)])

        nav = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        lbl_mes = Label(
            text=f'{_MESES[state["month"]]} {state["year"]}',
            font_size=dp(15), bold=True, color=C_TEXT,
        )

        pop = Popup(title='Seleccionar fecha', content=content,
                    size_hint=(0.94, None), height=dp(390))

        def rebuild():
            lbl_mes.text = f'{_MESES[state["month"]]} {state["year"]}'
            grid.clear_widgets()
            for week in _cal.monthcalendar(state['year'], state['month']):
                for day in week:
                    if day == 0:
                        grid.add_widget(Label())
                    else:
                        is_sel = (day == state['day'])
                        b = RoundedButton(
                            text=str(day),
                            bg_color=C_GREEN if is_sel else (0.88, 0.88, 0.88, 1),
                            text_color=C_WHITE if is_sel else C_TEXT,
                            radius=dp(4), size_hint_y=None, height=dp(36),
                            font_size=dp(13),
                        )

                        def _sel(x, d=day):
                            state['day'] = d
                            lbl_date.text = fmt()
                            pop.dismiss()

                        b.bind(on_press=_sel)
                        grid.add_widget(b)

        def prev_m(x):
            if state['month'] == 1:
                state['month'] = 12; state['year'] -= 1
            else:
                state['month'] -= 1
            state['day'] = min(state['day'],
                               _cal.monthrange(state['year'], state['month'])[1])
            rebuild()

        def next_m(x):
            if state['month'] == 12:
                state['month'] = 1; state['year'] += 1
            else:
                state['month'] += 1
            state['day'] = min(state['day'],
                               _cal.monthrange(state['year'], state['month'])[1])
            rebuild()

        btn_prev = RoundedButton(text='<', bg_color=C_GREEN, text_color=C_WHITE,
                                 radius=dp(8), size_hint_x=None, width=dp(42),
                                 size_hint_y=None, height=dp(38), font_size=dp(16))
        btn_next = RoundedButton(text='>', bg_color=C_GREEN, text_color=C_WHITE,
                                 radius=dp(8), size_hint_x=None, width=dp(42),
                                 size_hint_y=None, height=dp(38), font_size=dp(16))
        btn_prev.bind(on_press=prev_m)
        btn_next.bind(on_press=next_m)
        nav.add_widget(btn_prev)
        nav.add_widget(lbl_mes)
        nav.add_widget(btn_next)
        content.add_widget(nav)

        hdr = GridLayout(cols=7, size_hint_y=None, height=dp(26))
        for d in ['L', 'M', 'X', 'J', 'V', 'S', 'D']:
            hdr.add_widget(Label(text=d, font_size=dp(11), bold=True, color=C_GRAY))
        content.add_widget(hdr)

        grid = GridLayout(cols=7, size_hint_y=None, spacing=dp(2))
        grid.bind(minimum_height=grid.setter('height'))
        content.add_widget(grid)

        rebuild()
        pop.open()

    def _ui_longtext(self, q):
        ti = TextInput(
            hint_text='Escribe aqui...', multiline=True,
            size_hint_y=None, height=dp(100),
            background_color=C_INPUT, foreground_color=C_TEXT,
            hint_text_color=(0.6, 0.6, 0.6, 1),
            padding=[dp(10), dp(10)], font_size=dp(14),
            cursor_color=C_GREEN,
        )
        btn = rounded_btn('Siguiente >', height=dp(46),
                          on_press=lambda x: self._submit_text(q, ti.text.strip()))
        self.input_area.add_widget(ti)
        self.input_area.add_widget(btn)

    def _ui_yesno(self, q):
        row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        b_si = rounded_btn('Si', height=dp(50),
                            on_press=lambda x: self._submit_choice(q, 'Si'))
        b_no = rounded_btn('No', bg=C_RED, height=dp(50),
                            on_press=lambda x: self._submit_choice(q, 'No'))
        row.add_widget(b_si)
        row.add_widget(b_no)
        self.input_area.add_widget(row)

    def _ui_choice(self, q):
        sc = ScrollView(size_hint_y=None,
                        height=min(dp(210), dp(48) * len(q['opciones'])))
        inner = GridLayout(cols=1, spacing=dp(5), size_hint_y=None,
                           padding=[0, dp(2)])
        inner.bind(minimum_height=inner.setter('height'))
        for opt in q['opciones']:
            b = RoundedButton(
                text=opt, bg_color=C_CHOICE, text_color=C_TEXT,
                radius=dp(8), size_hint_y=None, height=dp(44),
                font_size=dp(13), bold=False,
            )
            b.bind(on_press=lambda x, o=opt: self._submit_choice(q, o))
            inner.add_widget(b)
        sc.add_widget(inner)
        self.input_area.add_widget(sc)

    def _ui_multiselect(self, q):
        self.multiselect_selected = []
        self._ms_btns = {}
        sc = ScrollView(size_hint_y=None,
                        height=min(dp(180), dp(46) * len(q['opciones'])))
        inner = GridLayout(cols=1, spacing=dp(4), size_hint_y=None,
                           padding=[0, dp(2)])
        inner.bind(minimum_height=inner.setter('height'))
        for opt in q['opciones']:
            b = RoundedButton(
                text=opt, bg_color=C_CHOICE, text_color=C_TEXT,
                radius=dp(8), size_hint_y=None, height=dp(42), font_size=dp(12),
            )
            b.bind(on_press=lambda x, o=opt: self._toggle(o, x))
            inner.add_widget(b)
            self._ms_btns[opt] = b
        sc.add_widget(inner)
        self.input_area.add_widget(sc)
        self.input_area.add_widget(
            rounded_btn('Confirmar seleccion >', height=dp(46),
                        on_press=lambda x: self._submit_multi(q))
        )

    def _toggle(self, opt, btn):
        if opt in self.multiselect_selected:
            self.multiselect_selected.remove(opt)
            btn.set_color(C_CHOICE)
            btn.color = C_TEXT
        else:
            self.multiselect_selected.append(opt)
            btn.set_color(C_GREEN)
            btn.color = C_WHITE

    def _ui_choice_search(self, q, options):
        """Selector con barra de busqueda y entrada manual."""
        search = TextInput(
            hint_text='Buscar...', multiline=False,
            size_hint_y=None, height=dp(40),
            background_color=C_INPUT, foreground_color=C_TEXT,
            hint_text_color=(0.6, 0.6, 0.6, 1),
            padding=[dp(10), dp(8)], font_size=dp(14),
            cursor_color=C_GREEN,
        )

        sc = ScrollView(size_hint_y=None, height=dp(155))
        inner = GridLayout(cols=1, spacing=dp(3), size_hint_y=None, padding=[0, dp(2)])
        inner.bind(minimum_height=inner.setter('height'))

        def _filter(instance, text):
            inner.clear_widgets()
            q_text = text.strip().lower()
            filtered = [o for o in options if q_text in o.lower()] if q_text else options
            for opt in filtered[:40]:
                b = RoundedButton(
                    text=opt, bg_color=C_CHOICE, text_color=C_TEXT,
                    radius=dp(6), size_hint_y=None, height=dp(40), font_size=dp(13),
                )
                b.bind(on_press=lambda x, o=opt: self._submit_choice(q, o))
                inner.add_widget(b)

        search.bind(text=_filter)
        _filter(None, '')
        sc.add_widget(inner)

        sep = Label(
            text='- O escribe manualmente -', font_size=dp(11), color=C_GRAY,
            size_hint_y=None, height=dp(20), halign='center',
        )
        sep.bind(size=sep.setter('text_size'))

        manual_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        manual_input = TextInput(
            hint_text='Escribe aqui...', multiline=False,
            size_hint_y=None, height=dp(42),
            background_color=C_INPUT, foreground_color=C_TEXT,
            padding=[dp(10), dp(10)], font_size=dp(14),
            cursor_color=C_GREEN,
        )
        btn_ok = RoundedButton(
            text='OK', bg_color=C_GREEN, text_color=C_WHITE,
            radius=dp(8), size_hint_x=None, width=dp(52),
            size_hint_y=None, height=dp(42), font_size=dp(14),
        )
        btn_ok.bind(on_press=lambda x: self._submit_text(q, manual_input.text.strip()))
        manual_row.add_widget(manual_input)
        manual_row.add_widget(btn_ok)

        self.input_area.add_widget(search)
        self.input_area.add_widget(sc)
        self.input_area.add_widget(sep)
        self.input_area.add_widget(manual_row)

    def _ui_estado_mx(self, q):
        from data.mexico_locations import ESTADOS_MEXICO
        self._ui_choice_search(q, ESTADOS_MEXICO)

    def _ui_municipio_mx(self, q):
        from data.mexico_locations import MUNICIPIOS_POR_ESTADO
        estado = self.form_data.get('entidad_federativa', '')
        options = MUNICIPIOS_POR_ESTADO.get(estado, [])
        if options:
            self._ui_choice_search(q, options)
        else:
            self._ui_text(q)

    def _ui_coordinates(self, q):
        from kivy.utils import platform

        lbl_status = Label(
            text='Ingresa las coordenadas o usa el GPS',
            font_size=dp(12), color=C_GRAY,
            size_hint_y=None, height=dp(22), halign='center',
        )
        lbl_status.bind(size=lbl_status.setter('text_size'))

        ti = TextInput(
            hint_text='Latitud,Longitud  (ej: 24.7994,-107.3884) o N/A',
            text='', multiline=False,
            size_hint_y=None, height=dp(44),
            background_color=C_INPUT, foreground_color=C_TEXT,
            hint_text_color=(0.6, 0.6, 0.6, 1),
            padding=[dp(10), dp(10)], font_size=dp(14),
            cursor_color=C_GREEN,
        )

        def _get_gps(x):
            if platform == 'android':
                try:
                    from plyer import gps

                    def _on_location(**kwargs):
                        lat = kwargs.get('lat')
                        lon = kwargs.get('lon')
                        if lat is not None and lon is not None:
                            Clock.schedule_once(
                                lambda dt: setattr(ti, 'text',
                                                   f'{lat:.6f},{lon:.6f}'), 0)
                            Clock.schedule_once(
                                lambda dt: setattr(lbl_status, 'text',
                                                   'GPS obtenido correctamente'), 0)

                    gps.configure(on_location=_on_location)
                    gps.start(minTime=1000, minDistance=0)
                    lbl_status.text = 'Obteniendo GPS...'
                except ImportError:
                    lbl_status.text = 'GPS no disponible en esta version'
                except Exception as e:
                    lbl_status.text = f'GPS no disponible: {e}'
            else:
                lbl_status.text = 'GPS solo disponible en el dispositivo Android'

        btn_gps = rounded_btn('Coordenadas actuales (GPS)', height=dp(42))
        btn_gps.bind(on_press=_get_gps)

        self.input_area.add_widget(lbl_status)
        self.input_area.add_widget(btn_gps)
        self.input_area.add_widget(ti)
        self.input_area.add_widget(
            rounded_btn('Siguiente >', height=dp(46),
                        on_press=lambda x: self._submit_text(
                            q, ti.text.strip() or 'N/A'))
        )

    # ── Submit ────────────────────────────────────────────────────────────────

    def _submit_text(self, q, val):
        qi = self.current_index
        self.form_data[q['campo']] = val or 'N/A'
        self._user_msg(val or 'N/A', qi=qi)
        self.current_index += 1
        self.questions = get_question_list(self.form_data)
        self._update_progress()
        Clock.schedule_once(lambda dt: self._ask(), 0.3)

    def _submit_choice(self, q, val):
        qi = self.current_index
        self.form_data[q['campo']] = val
        self._user_msg(val, qi=qi)
        self.current_index += 1
        self.questions = get_question_list(self.form_data)
        self._update_progress()
        Clock.schedule_once(lambda dt: self._ask(), 0.3)

    def _submit_multi(self, q):
        qi = self.current_index
        sel = list(self.multiselect_selected) or ['Ninguno']
        self.form_data[q['campo']] = sel
        self._user_msg(', '.join(sel), qi=qi)
        self.current_index += 1
        self.questions = get_question_list(self.form_data)
        self._update_progress()
        Clock.schedule_once(lambda dt: self._ask(), 0.3)

    # ── Editar respuesta ──────────────────────────────────────────────────────

    def _confirm_edit(self, qi):
        content = popup_content()
        content.add_widget(Label(
            text='Editar esta respuesta?\nLas siguientes se borraran.',
            color=C_TEXT, font_size=dp(14), halign='center',
            size_hint_y=None, height=dp(54),
        ))
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        b1 = rounded_btn('Cancelar', bg=(0.75, 0.75, 0.75, 1),
                          color=C_TEXT, height=dp(46))
        b2 = rounded_btn('Editar', height=dp(46))
        row.add_widget(b1)
        row.add_widget(b2)
        content.add_widget(row)
        pop = Popup(title='Editar', content=content,
                    size_hint=(0.82, None), height=dp(210))
        b1.bind(on_press=pop.dismiss)
        b2.bind(on_press=lambda x: (pop.dismiss(), self._edit_at(qi)))
        pop.open()

    def _edit_at(self, qi):
        all_qs = get_question_list(self.form_data)
        for q in all_qs[qi:]:
            campo = q.get('campo')
            if campo and campo in self.form_data:
                del self.form_data[campo]

        to_remove = [w for w, i in self._chat_log if i >= qi]
        for w in to_remove:
            if w.parent:
                self.chat.remove_widget(w)
        self._chat_log = [(w, i) for w, i in self._chat_log if i < qi]

        self.current_index = qi
        self.questions = get_question_list(self.form_data)
        self.input_area.clear_widgets()
        Clock.schedule_once(lambda dt: self._ask(), 0.3)

    # ── Finalizar ─────────────────────────────────────────────────────────────

    def _show_finish(self):
        self._bar_fill.width = self._bar_outer.width
        self.lbl_pct.text = '100%'
        self.lbl_progress.text = '¡Formulario completo!'
        self.input_area.clear_widgets()
        self._bot('[b]¡Formulario completado![/b]\n'
                  'Presiona el boton para generar el PDF oficial.')
        self.input_area.add_widget(
            rounded_btn('Generar PDF oficial', height=dp(50),
                        on_press=self._generate_pdf)
        )

    def _generate_pdf(self, *a):
        self._bot('Generando PDF...')
        user = api_client.get_user() or {}

        from kivy.app import App
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_dir = os.path.join(App.get_running_app().user_data_dir, 'IPH_Reportes')
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f'IPH_{ts}.pdf')

        # Guardar reporte en historial del servidor
        api_client.save_report(
            self.form_data,
            on_success=lambda r: None,
            on_error=lambda e: None,  # silencioso, no interrumpir flujo
        )

        api_client.generate_pdf(
            self.form_data, user, path,
            on_success=lambda p: Clock.schedule_once(lambda dt: self._pdf_ok(p), 0),
            on_error=lambda m: Clock.schedule_once(
                lambda dt, msg=m: self._bot(f'Error al generar PDF: {msg}'), 0),
        )

    def _pdf_ok(self, path):
        from kivy.utils import platform
        if platform == 'android':
            # Copiar a Descargas para que sea accesible
            try:
                import shutil
                dest = f'/sdcard/Download/{os.path.basename(path)}'
                shutil.copy2(path, dest)
                self._bot(
                    f'[b]PDF generado correctamente.[/b]\n'
                    f'Guardado en:\nDescargas/{os.path.basename(path)}\n'
                    f'Abrelo desde tu gestor de archivos.'
                )
            except Exception as e:
                self._bot(
                    f'[b]PDF generado.[/b]\n'
                    f'Archivo: {os.path.basename(path)}\n'
                    f'Ubicacion: {path}'
                )
        else:
            self._bot(
                f'[b]PDF generado correctamente.[/b]\n'
                f'Archivo: {os.path.basename(path)}'
            )

    def _abrir_pdf(self, path):
        try:
            from android.runnable import run_on_ui_thread
            from jnius import autoclass

            filename = os.path.basename(path)

            @run_on_ui_thread
            def _do():
                try:
                    Intent         = autoclass('android.content.Intent')
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    VERSION        = autoclass('android.os.Build$VERSION')

                    if VERSION.SDK_INT >= 29:
                        ContentValues = autoclass('android.content.ContentValues')
                        MSDl          = autoclass('android.provider.MediaStore$Downloads')

                        vals = ContentValues()
                        vals.put('_display_name', filename)
                        vals.put('mime_type', 'application/pdf')
                        vals.put('relative_path', 'Download/')

                        resolver = PythonActivity.mActivity.getContentResolver()
                        uri = resolver.insert(MSDl.EXTERNAL_CONTENT_URI, vals)

                        with open(path, 'rb') as f:
                            data = f.read()
                        out = resolver.openOutputStream(uri)
                        out.write(data)
                        out.flush()
                        out.close()
                    else:
                        Environment = autoclass('android.os.Environment')
                        StrictMode  = autoclass('android.os.StrictMode')
                        VmBuilder   = autoclass('android.os.StrictMode$VmPolicy$Builder')
                        Uri         = autoclass('android.net.Uri')
                        File        = autoclass('java.io.File')

                        StrictMode.setVmPolicy(VmBuilder().build())
                        dl_dir = Environment.getExternalStoragePublicDirectory(
                            Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
                        dest = os.path.join(str(dl_dir), filename)
                        shutil.copy2(path, dest)
                        uri = Uri.fromFile(File(dest))

                    intent = Intent(Intent.ACTION_VIEW)
                    intent.setDataAndType(uri, 'application/pdf')
                    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION
                                    | Intent.FLAG_ACTIVITY_NEW_TASK)
                    PythonActivity.mActivity.startActivity(intent)

                except Exception as e:
                    Clock.schedule_once(
                        lambda dt, err=str(e): self._bot(
                            f'PDF guardado pero no se pudo abrir: {err}\n'
                            f'Buscalo en Descargas.'), 0)

            _do()
        except ImportError:
            pass

    # ── Dialogos ──────────────────────────────────────────────────────────────

    def _confirm_reset(self, *a):
        content = popup_content()
        content.add_widget(Label(
            text='Se borrara toda la informacion\nde este formulario.',
            color=C_TEXT, font_size=dp(14), halign='center',
            size_hint_y=None, height=dp(54),
        ))
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        b1 = rounded_btn('Seguir anadiendo', bg=(0.75, 0.75, 0.75, 1),
                          color=C_TEXT, height=dp(46))
        b2 = rounded_btn('Borrar', bg=C_RED, height=dp(46))
        row.add_widget(b1)
        row.add_widget(b2)
        content.add_widget(row)
        pop = Popup(title='Reiniciar formulario', content=content,
                    size_hint=(0.82, None), height=dp(220))
        b1.bind(on_press=pop.dismiss)
        b2.bind(on_press=lambda x: (pop.dismiss(), self.on_enter()))
        pop.open()

    def _confirm_exit(self, *a):
        content = popup_content()
        content.add_widget(Label(
            text='Salir del IPH?\nSe perdera el progreso actual.',
            color=C_TEXT, font_size=dp(14), halign='center',
            size_hint_y=None, height=dp(54),
        ))
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        b1 = rounded_btn('Continuar', bg=(0.75, 0.75, 0.75, 1),
                          color=C_TEXT, height=dp(46))
        b2 = rounded_btn('Salir', bg=C_RED, height=dp(46))
        row.add_widget(b1)
        row.add_widget(b2)
        content.add_widget(row)
        pop = Popup(title='Salir', content=content,
                    size_hint=(0.82, None), height=dp(210))
        b1.bind(on_press=pop.dismiss)
        b2.bind(on_press=lambda x: (pop.dismiss(),
                                     setattr(self.manager, 'current', 'home')))
        pop.open()
