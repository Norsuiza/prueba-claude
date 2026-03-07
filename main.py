from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10

        self.label = Label(
            text='Hello, World!',
            font_size='24sp'
        )
        self.add_widget(self.label)

        btn = Button(
            text='Press me',
            size_hint=(1, 0.2),
            font_size='18sp'
        )
        btn.bind(on_press=self.on_button_press)
        self.add_widget(btn)

    def on_button_press(self, instance):
        self.label.text = 'Button pressed!'


class MyApp(App):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    MyApp().run()
