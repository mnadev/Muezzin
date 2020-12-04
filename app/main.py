import kivy

kivy.require('2.0.0')

from kivy.config import Config

Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')

from kivy.app import App
from kivy.core.window import Window
from screens import MuezzinCarousel

Window.clearcolor = (0.1, 0.61, 0.2, 0.91)


class MuezzinApp(App):
  def build(self):
    return MuezzinCarousel(direction='right')


if __name__ == '__main__':
  MuezzinApp().run()
