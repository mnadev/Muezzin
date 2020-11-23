from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import datetime

class MainScreen(GridLayout):
  def __init__(self, **kwargs):
    super(MainScreen, self).__init__(**kwargs)
    self.cols = 5
    self.add_widget(Label(text=datetime.datetime.now().strftime("%I:%M") , color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Saturday, October 20, 2020", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="14 Ramadan 1440 AH", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Fajr: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Sunrise: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Dhuhr: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Asr: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Maghrib: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Isha: 5:04 AM", color=[0, 0, 0, 1]))
