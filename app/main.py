import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.label import Label
from main_screen import MainScreen

class MuezzinApp(App):
  def build(self):
    return MainScreen()

if __name__ == '__main__':
  MuezzinApp().run()
