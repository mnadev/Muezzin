import kivy

kivy.require('2.0.0')

from kivy.config import Config

Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')

from kivymd.app import MDApp

from config_handler import read_from_config
from screens import MuezzinCarousel

_, _, _, enable_dark_mode = read_from_config()

class MuezzinApp(MDApp):
  def build(self):
    self.theme_cls.primary_palette = "Green"
    self.theme_cls.primary_hue = "600"
    if enable_dark_mode:
      self.theme_cls.theme_style = "Dark"
    else:
      self.theme_cls.theme_style = "Light"
    return MuezzinCarousel(direction='right')


if __name__ == '__main__':
  MuezzinApp().run()
