import os
import sys

# Ensure mobile package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.clock import Clock
from kivy.core.window import Window

# Optional: set window size for desktop testing
Window.size = (400, 700)

from mobile.screens.login_screen import LoginScreen
from mobile.screens.register_screen import RegisterScreen
from mobile.screens.home_screen import HomeScreen
from mobile.screens.iph_screen import IPHScreen
from mobile.utils import api_client


class IPHApp(App):
    def build(self):
        self.title = 'Sistema IPH · Culiacán'
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(IPHScreen(name='iph'))
        return sm

    def on_start(self):
        """Auto-login si hay sesión guardada."""
        def check(dt):
            token = api_client.get_token()
            if token:
                api_client.check_auth(
                    on_success=self._auto_login_ok,
                    on_error=lambda msg: None,
                )
        Clock.schedule_once(check, 0.5)

    def _auto_login_ok(self, user):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._go_home(), 0)

    def _go_home(self):
        sm = self.root
        home = sm.get_screen('home')
        home.refresh_user()
        sm.current = 'home'


if __name__ == '__main__':
    IPHApp().run()
