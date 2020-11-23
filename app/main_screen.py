from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import datetime


class MainScreen(GridLayout):
  def __init__(self, **kwargs):
    super(MainScreen, self).__init__(**kwargs)
    self.cols = 3
    self.add_widget(CalendarPane())
    self.add_widget(
      Label(text=datetime.datetime.now().strftime("%I:%M %p"), color=[0, 0, 0, 1], font_name="RobotoMono-Regular"))
    self.add_widget(PrayerPane())


class CalendarPane(GridLayout):
  def __init__(self, **kwargs):
    super(CalendarPane, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2
    self.add_widget(WrappedLabel(text="Saturday, October 20, 2020", color=[0, 0, 0, 1], font_name="Roboto-Bold"))
    self.add_widget(WrappedLabel(text="14 Ramadan 1440 AH", color=[0, 0, 0, 1], font_name="Roboto-Bold"))


class PrayerPane(GridLayout):
  def __init__(self, **kwargs):
    super(PrayerPane, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 6
    self.add_widget(WrappedLabel(text="Fajr: 5:04 AM", color=[0, 0, 0, 1], font_name="Roboto-Bold"))
    self.add_widget(WrappedLabel(text="Duha: 5:04 AM", color=[0, 0, 0, 1], font_name="Roboto-Bold"))
    self.add_widget(WrappedLabel(text="Dhuhr: 5:04 AM", color=[0, 0, 0, 1], font_name="Roboto-Bold"))
    self.add_widget(WrappedLabel(text="Asr: 5:04 AM", color=[0, 0, 0, 1], font_name="Roboto-Bold"))
    self.add_widget(WrappedLabel(text="Maghrib: 5:04 AM", color=[0, 0, 0, 1], font_name="Roboto-Bold"))
    self.add_widget(WrappedLabel(text="Isha: 5:04 AM", color=[0, 0, 0, 1], font_name="Roboto-BoldItalic"))


class WrappedLabel(Label):
  # Courtesy of https://stackoverflow.com/questions/43666381/wrapping-the-text-of-a-kivy-label
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.bind(
      width=lambda *x:
      self.setter('text_size')(self, (self.width, None)),
      texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))
