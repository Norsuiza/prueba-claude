import os
import sys

# Asegurar que mobile/ esté en el path (funciona en Android y desktop)
MOBILE_DIR = os.path.dirname(os.path.abspath(__file__))
if MOBILE_DIR not in sys.path:
    sys.path.insert(0, MOBILE_DIR)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

# Solo fijar tamaño en desktop, no en Android
if platform != 'android':
    Window.size = (400, 700)

from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.home_screen import HomeScreen
from screens.iph_screen import IPHScreen
from utils import api_client


class IPHApp(App):
    def build(self):
        self.title = 'ChatPoli'
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(IPHScreen(name='iph'))
        return sm

    def on_resume(self):
        """Evita pantalla negra al volver de otra app (PDF viewer, etc.)."""
        Window.canvas.ask_update()
        Clock.schedule_once(lambda dt: Window.canvas.ask_update(), 0.1)


if __name__ == '__main__':
    IPHApp().run()
