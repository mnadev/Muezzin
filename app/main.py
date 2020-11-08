import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.label import Label

class MuezzinApp(App):
  def build(self):
    return Label(text='Muezzin App')

if __name__ == '__main__':
  MuezzinApp().run()
