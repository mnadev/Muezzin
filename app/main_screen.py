from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

class MainScreen(GridLayout):
  def __init__(self, **kwargs):
    super(MainScreen, self).__init__(**kwargs)
    self.cols = 5
    self.add_widget(Label(text="8:49 PM"))
    self.add_widget(Label(text="Saturday, October 20, 2020"))
    self.add_widget(Label(text="14 Ramadan 1440 AH"))
    self.add_widget(Label(text="Fajr: 5:04 AM"))
    self.add_widget(Label(text="Sunrise: 5:04 AM"))
    self.add_widget(Label(text="Dhuhr: 5:04 AM"))
    self.add_widget(Label(text="Asr: 5:04 AM"))
    self.add_widget(Label(text="Maghrib: 5:04 AM"))
    self.add_widget(Label(text="Isha: 5:04 AM"))
