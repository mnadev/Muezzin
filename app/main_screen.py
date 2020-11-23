from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import datetime


class MainScreen(GridLayout):
  def __init__(self, **kwargs):
    super(MainScreen, self).__init__(**kwargs)
    self.cols = 2

    self.add_widget(TimePane())
    self.add_widget(PrayerPane(size_hint=(0.3, 1)))


class TimePane(GridLayout):
  def __init__(self, **kwargs):
    super(TimePane, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2
    self.time_widget = Label(text=datetime.datetime.now().strftime("%I:%M %p"), color=[1, 1, 1, 1],
                             font_name="RobotoMono-Regular",
                             size_hint=(1, 0.5), font_size="30sp")

    self.add_widget(CalendarBox(size_hint=(1, 0.5)))
    self.add_widget(self.time_widget)

    Clock.schedule_once(self.update, datetime.datetime.now().second % 60)

  def update(self, *args):
    self.time_widget.text = datetime.datetime.now().strftime("%I:%M %p")
    Clock.schedule_once(self.update, datetime.datetime.now().second % 60)


class CalendarBox(GridLayout):
  def __init__(self, **kwargs):
    super(CalendarBox, self).__init__(**kwargs)
    self.cols = 2
    self.rows = 1
    self.add_widget(
      WrappedLabel(text="Saturday, October 20, 2020", color=[0, 0, 0, 1], font_name="Roboto-Bold", font_size="16sp",
                   size_hint=(0.5, 1), padding=("10sp", "0sp")))
    self.add_widget(
      WrappedLabel(text="14 Ramadan 1440 AH", color=[0, 0, 0, 1], font_name="Roboto-Bold", font_size="16sp",
                   size_hint=(0.5, 1), padding=("10sp", "0sp")))


class PrayerPane(GridLayout):
  def __init__(self, **kwargs):
    super(PrayerPane, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 6
    self.add_widget(PrayerTimeLayout(prayer_time="Fajr"))
    self.add_widget(PrayerTimeLayout(prayer_time="Duha"))
    self.add_widget(PrayerTimeLayout(prayer_time="Dhuhr"))
    self.add_widget(PrayerTimeLayout(prayer_time="Asr"))
    self.add_widget(PrayerTimeLayout(prayer_time="Maghrib"))
    self.add_widget(PrayerTimeLayout(prayer_time="Isha"))


class PrayerTimeLayout(GridLayout):
  def __init__(self, prayer_time, **kwargs):
    super(PrayerTimeLayout, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2

    self.prayer_time = prayer_time
    self.todays_time = WrappedLabel(text=self.prayer_time + ": 5:04 AM", color=[0, 0, 0, 1],
                                    font_name="Roboto-BoldItalic", font_size="15sp")
    self.tomorrows_time = WrappedLabel(text="Tomorrow: 5:04 AM", color=[0, 0, 0, 0.9],
                                       font_name="Roboto-BoldItalic", font_size="8sp")
    self.add_widget(self.todays_time)
    self.add_widget(self.tomorrows_time)


class WrappedLabel(Label):
  # Courtesy of https://stackoverflow.com/questions/43666381/wrapping-the-text-of-a-kivy-label
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.bind(
      width=lambda *x:
      self.setter('text_size')(self, (self.width, None)),
      texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))
