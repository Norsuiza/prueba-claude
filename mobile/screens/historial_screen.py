from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

from utils import api_client
from utils.widgets import rounded_btn

C_WHITE  = (1, 1, 1, 1)
C_BG     = (0.94, 0.94, 0.94, 1)
C_GREEN  = (0.0, 0.408, 0.278, 1)
C_RED    = (0.808, 0.067, 0.149, 1)
C_TEXT   = (0.1, 0.1, 0.1, 1)
C_GRAY   = (0.5, 0.5, 0.5, 1)
C_CARD   = (1, 1, 1, 1)


class HistorialScreen(Screen):
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
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))

        lbl_title = Label(text='Historial de IPH', font_size=dp(15),
                          bold=True, color=C_WHITE)

        btn_refresh = Button(
            text='[R]', size_hint_x=None, width=dp(44),
            background_color=(0, 0, 0, 0), background_normal='', background_down='',
            color=C_WHITE, font_size=dp(13),
        )
        btn_refresh.bind(on_press=lambda x: self._cargar())

        hdr.add_widget(btn_back)
        hdr.add_widget(lbl_title)
        hdr.add_widget(btn_refresh)
        outer.add_widget(hdr)

        # Estado/cargando
        self.lbl_estado = Label(
            text='Cargando...', font_size=dp(13), color=C_GRAY,
            size_hint_y=None, height=dp(40), halign='center',
        )
        self.lbl_estado.bind(size=self.lbl_estado.setter('text_size'))
        outer.add_widget(self.lbl_estado)

        # Lista de reportes
        scroll = ScrollView()
        self.lista = GridLayout(cols=1, spacing=dp(8), size_hint_y=None,
                                padding=[dp(10), dp(8)])
        self.lista.bind(minimum_height=self.lista.setter('height'))
        scroll.add_widget(self.lista)
        outer.add_widget(scroll)

        self.add_widget(outer)

    def on_enter(self):
        self._cargar()

    def _cargar(self):
        self.lista.clear_widgets()
        self.lbl_estado.text = 'Cargando historial...'
        api_client.get_reports(
            on_success=lambda r: Clock.schedule_once(
                lambda dt: self._mostrar(r), 0),
            on_error=lambda e: Clock.schedule_once(
                lambda dt: setattr(self.lbl_estado, 'text',
                                   f'Error: {e}'), 0),
        )

    def _mostrar(self, reportes):
        self.lista.clear_widgets()
        if not reportes:
            self.lbl_estado.text = 'No hay informes generados aun.'
            return
        self.lbl_estado.text = f'{len(reportes)} informe(s) encontrado(s)'
        for r in reportes:
            self.lista.add_widget(self._card(r))

    def _card(self, r):
        card = BoxLayout(
            orientation='vertical', size_hint_y=None, height=dp(100),
            padding=[dp(12), dp(10)], spacing=dp(4),
        )
        with card.canvas.before:
            Color(*C_CARD)
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda w, v: setattr(w._bg, 'pos', v),
                  size=lambda w, v: setattr(w._bg, 'size', v))

        # Fila superior: expediente + fecha
        row1 = BoxLayout(size_hint_y=None, height=dp(22))
        lbl_exp = Label(
            text=f'Expediente: {r.get("expediente", "N/A")}',
            font_size=dp(13), bold=True, color=C_GREEN,
            halign='left', size_hint_x=0.6,
        )
        lbl_exp.bind(size=lbl_exp.setter('text_size'))
        lbl_fecha = Label(
            text=r.get('fecha', ''),
            font_size=dp(11), color=C_GRAY,
            halign='right', size_hint_x=0.4,
        )
        lbl_fecha.bind(size=lbl_fecha.setter('text_size'))
        row1.add_widget(lbl_exp)
        row1.add_widget(lbl_fecha)

        # Detenido
        lbl_det = Label(
            text=f'Detenido: {r.get("detenido", "Sin detenido")}',
            font_size=dp(12), color=C_TEXT,
            halign='left', size_hint_y=None, height=dp(20),
        )
        lbl_det.bind(size=lbl_det.setter('text_size'))

        # Fecha creacion + boton PDF
        row2 = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        lbl_created = Label(
            text=f'Generado: {r.get("created_at", "")}',
            font_size=dp(10), color=C_GRAY, halign='left',
        )
        lbl_created.bind(size=lbl_created.setter('text_size'))
        btn_pdf = rounded_btn('Ver PDF', height=dp(32),
                              on_press=lambda x, rid=r['id']: self._ver_pdf(rid))
        row2.add_widget(lbl_created)
        row2.add_widget(btn_pdf)

        card.add_widget(row1)
        card.add_widget(lbl_det)
        card.add_widget(row2)
        return card

    def _ver_pdf(self, report_id):
        from kivy.utils import platform
        import threading, os, shutil
        from kivy.app import App

        def _run():
            try:
                import requests
                url = f'{api_client._get_base_url()}/api/reports/{report_id}/pdf'
                resp = requests.get(url, headers=api_client._headers(), timeout=30)
                if resp.status_code == 200:
                    ts = report_id
                    out_dir = os.path.join(
                        App.get_running_app().user_data_dir, 'IPH_Reportes')
                    os.makedirs(out_dir, exist_ok=True)
                    path = os.path.join(out_dir, f'IPH_hist_{ts}.pdf')
                    with open(path, 'wb') as f:
                        f.write(resp.content)
                    if platform == 'android':
                        try:
                            dest = f'/sdcard/Download/IPH_hist_{ts}.pdf'
                            shutil.copy2(path, dest)
                            msg = f'PDF guardado en:\nDescargas/IPH_hist_{ts}.pdf'
                        except Exception:
                            msg = f'PDF guardado en:\n{path}'
                    else:
                        msg = f'PDF guardado en:\n{path}'
                    Clock.schedule_once(
                        lambda dt: setattr(self.lbl_estado, 'text', msg), 0)
                else:
                    Clock.schedule_once(
                        lambda dt: setattr(self.lbl_estado, 'text',
                                           'Error al descargar PDF'), 0)
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: setattr(self.lbl_estado, 'text',
                                       f'Error: {e}'), 0)

        self.lbl_estado.text = 'Descargando PDF...'
        threading.Thread(target=_run, daemon=True).start()
