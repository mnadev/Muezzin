import kivy

kivy.require('2.0.0')

from kivy.config import Config

Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')

from kivymd.app import MDApp
from screens import MuezzinCarousel


class MuezzinApp(MDApp):
  def build(self):
    self.theme_cls.primary_palette = "Green"
    self.theme_cls.primary_hue = "600"
    self.theme_cls.theme_style = "Dark"
    return MuezzinCarousel(direction='right')


if __name__ == '__main__':
  MuezzinApp().run()
