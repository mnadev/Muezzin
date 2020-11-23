from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import datetime

class MainScreen(GridLayout):
  def __init__(self, **kwargs):
    super(MainScreen, self).__init__(**kwargs)
    self.cols = 3
    self.add_widget(CalendarPane())
    self.add_widget(Label(text=datetime.datetime.now().strftime("%I:%M") , color=[0, 0, 0, 1]))
    self.add_widget(PrayerPane())

class CalendarPane(GridLayout):
  def __init__(self, **kwargs):
    super(CalendarPane, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2
    self.add_widget(Label(text="Saturday, October 20, 2020", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="14 Ramadan 1440 AH", color=[0, 0, 0, 1]))

class PrayerPane(GridLayout):
  def __init__(self, **kwargs):
    super(PrayerPane, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 6
    self.add_widget(Label(text="Fajr: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Duha: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Dhuhr: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Asr: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Maghrib: 5:04 AM", color=[0, 0, 0, 1]))
    self.add_widget(Label(text="Isha: 5:04 AM", color=[0, 0, 0, 1]))
