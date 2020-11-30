from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

import api_controller as getter
import concurrent.futures
import datetime

sound = SoundLoader.load('res/adhan.mp3')
sound.seek(0)


def get_tomorrow_date():
  today = datetime.datetime.today()
  today = today.replace(hour=0, minute=0, second=0, microsecond=0)
  return today + datetime.timedelta(days=1)


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
                             size_hint=(1, 0.5), font_size="50sp")

    self.add_widget(CalendarBox(size_hint=(1, 0.5)))
    self.add_widget(self.time_widget)

    Clock.schedule_once(self.update, 60 - datetime.datetime.now().second % 60)

  def update(self, *args):
    self.time_widget.text = datetime.datetime.now().strftime("%I:%M %p")
    Clock.schedule_once(self.update, 60 - datetime.datetime.now().second % 60)

class CalendarBox(GridLayout):
  def __init__(self, **kwargs):
    super(CalendarBox, self).__init__(**kwargs)
    self.cols = 3
    self.rows = 1

    gregorian_date = getter.get_gregorian_date()
    self.gregorian_widget = WrappedLabel(text=gregorian_date["formatted_string"], color=[0, 0, 0, 1],
                                         font_name="Roboto-Bold", font_size="16sp", size_hint=(0.5, 1),
                                         padding=("10sp", "0sp"))

    self.hijri_widget = WrappedLabel(text="14 Ramadan 1440 AH", color=[0, 0, 0, 1], font_name="Roboto-Bold",
                                     font_size="16sp", size_hint=(0.5, 1), padding=("10sp", "0sp"))
    self.update_hijri_date()
    # Logo courtesy of flaticon
    self.add_widget(Image(source="res/mosque.png", keep_ratio=True, size_hint_x=0.1, pos=(0, 0)))
    self.add_widget(self.gregorian_widget)
    self.add_widget(self.hijri_widget)

    Clock.schedule_once(self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds)

  def update(self, *args):
    gregorian_date = getter.get_gregorian_date()
    self.gregorian_widget.text = gregorian_date["formatted_string"]
    self.update_hijri_date()
    Clock.schedule_once(self.update, (self.get_tomorrow_date() - datetime.datetime.now()).seconds)

  def update_hijri_date(self):
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_hijri_date)
    hijri_date = future.result()
    self.hijri_widget.text = str(hijri_date['day']) + " " + hijri_date['month'] + " " + str(hijri_date['year']) + " AH"


class PrayerPane(GridLayout):
  def __init__(self, **kwargs):
    super(PrayerPane, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 6
    self.todays_times = {'Fajr': '12:00 am', 'Duha': '12:00 am', 'Dhuhr': '12:00 am', 'Asr': '12:00 am',
                         'Maghrib': '12:00 am', 'Isha': '12:00 am'}

    self.tomorrow_times = {'Fajr': '12:00 am', 'Duha': '12:00 am', 'Dhuhr': '12:00 am', 'Asr': '12:00 am',
                           'Maghrib': '12:00 am', 'Isha': '12:00 am'}

    self.prayer_time_widgets = dict()
    for prayer_time in ["Fajr", "Duha", "Dhuhr", "Asr", "Maghrib", "Isha"]:
      self.prayer_time_widgets[prayer_time] = PrayerTimeLayout(prayer_time, self.todays_times,
                                                               self.tomorrow_times)
      self.add_widget(self.prayer_time_widgets[prayer_time])

    self.get_prayer_times()

  def get_prayer_times(self):
    todays_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_today)
    self.todays_times = todays_times_future.result()
    tomorrow_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_tomorrow)
    self.tomorrow_times = tomorrow_times_future.result()
    Clock.schedule_once(self.update, 0)

  def update(self, *args):
    for prayer_time in ["Fajr", "Duha", "Dhuhr", "Asr", "Maghrib", "Isha"]:
      self.prayer_time_widgets[prayer_time].update(self.todays_times, self.tomorrow_times)
    Clock.schedule_once(self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds)


class PrayerTimeLayout(GridLayout):
  def __init__(self, prayer_time, todays_times, tomorrow_times, **kwargs):
    super(PrayerTimeLayout, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2

    self.prayer_time = prayer_time
    self.todays_times = todays_times
    self.tomorrow_times = tomorrow_times

    self.todays_time_widget = WrappedLabel(text=self.prayer_time + ": " + self.todays_times[self.prayer_time],
                                           color=[0, 0, 0, 1], font_name="Roboto-BoldItalic", font_size="15sp")
    self.tomorrows_time_widget = WrappedLabel(text="Tomorrow: " + self.tomorrow_times[self.prayer_time],
                                              color=[0, 0, 0, 0.9], font_name="Roboto-BoldItalic", font_size="8sp")
    self.add_widget(self.todays_time_widget)
    self.add_widget(self.tomorrows_time_widget)

  def schedule_adhan(self):
    time_of_prayer = self.get_time_of_prayer(self.todays_times[self.prayer_time])
    if time_of_prayer < datetime.datetime.now():
      time_of_prayer = self.get_time_of_prayer(self.tomorrow_times[self.prayer_time]) + datetime.timedelta(days=1)
    Clock.schedule_once(self.play_adhan, (time_of_prayer - datetime.datetime.now()).total_seconds())

  def play_adhan(self, *args):
    sound.play()

  def get_time_of_prayer(self, time_string):
    adhan_time = datetime.datetime.strptime(time_string, "%I:%M %p")
    today = datetime.datetime.today()
    today = today.replace(hour=adhan_time.hour, minute=adhan_time.minute, second=0, microsecond=0)
    return today

  def update(self, todays_times, tomorrow_times):
    self.todays_times = todays_times
    self.tomorrow_times = tomorrow_times
    self.todays_time_widget.text = self.prayer_time + ": " + todays_times[self.prayer_time]
    self.tomorrows_time_widget.text = "Tomorrow: " + tomorrow_times[self.prayer_time]
    self.schedule_adhan()


class WrappedLabel(Label):
  # Courtesy of https://stackoverflow.com/questions/43666381/wrapping-the-text-of-a-kivy-label
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.bind(
      width=lambda *x:
      self.setter('text_size')(self, (self.width, None)),
      texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))
