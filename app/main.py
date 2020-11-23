import kivy
kivy.require('2.0.0')

from kivy.config import Config
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')

from kivy.app import App
from kivy.core.window import Window
from main_screen import MainScreen

Window.clearcolor = (1, 1, 1, 1)

class MuezzinApp(App):
  def build(self):
    return MainScreen()

if __name__ == '__main__':
  MuezzinApp().run()
