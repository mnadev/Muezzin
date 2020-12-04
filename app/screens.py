from kivy.core.audio import SoundLoader
from kivy.uix.carousel import Carousel
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import CoreImage, Image
from kivy.uix.label import Label

import api_controller as getter
import arrow
import concurrent.futures
import datetime
import re

fajr_alarm = False


def update_fajr_alarm(checkbox, value):
  global fajr_alarm
  fajr_alarm = value


adhan = SoundLoader.load('res/adhan.mp3')
adhan.seek(0)

alarm = SoundLoader.load('res/alarm/alarm.mp3')
alarm.seek(0)


def get_tomorrow_date():
  today = datetime.datetime.today()
  today = today.replace(hour=0, minute=0, second=0, microsecond=0)
  return today + datetime.timedelta(days=1)


class MuezzinCarousel(Carousel):
  def __init__(self, **kwargs):
    super(MuezzinCarousel, self).__init__(**kwargs)
    self.information_screen = InformationScreen()
    self.main_screen = MainScreen()
    self.settings_screen = SettingsScreen()

    self.add_widget(self.information_screen)
    self.add_widget(self.main_screen)
    self.add_widget(self.settings_screen)
    self.index = 1

  def on_index(self, *args):
    if self.index == 1:
      self.main_screen.prayer_pane.update()
    if self.index == 0:
      self.information_screen.update()
    Carousel.on_index(self, *args)


class InformationScreen(GridLayout):
  def __init__(self, **kwargs):
    super(InformationScreen, self).__init__(**kwargs)
    self.cols = 2
    self.rows = 1
    self.moon_widget = MoonWidget()
    self.weather_widget = WeatherWidget()
    self.add_widget(self.moon_widget)
    self.add_widget(self.weather_widget)

  def update(self):
    self.moon_widget.update()
    self.weather_widget.update()

class WeatherWidget(GridLayout):
  def __init__(self, **kwargs):
    super(WeatherWidget, self).__init__(**kwargs)
    self.cols = 2
    self.rows = 2
    self.woeid = None
    self.update_weather_location_woeid()
    weather = self.update_weather()

    self.weather_text = Label(text=weather["weather_state_name"])
    self.low_text = Label(text="High: " + str(weather["max_temp"]) + " °C")
    self.high_text = Label(text="Low: " + str(weather["min_temp"]) + " °C")

    self.image = Image()
    self.image.texture = CoreImage(self.update_weather_image(weather["weather_state_abbr"]), ext='png').texture

    self.add_widget(self.image)
    self.add_widget(self.weather_text)
    self.add_widget(self.high_text)
    self.add_widget(self.low_text)
    self.last_update_time = datetime.datetime.now()

  def update_weather_image(self, weather_state_abbr):
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_weather_image, weather_state_abbr)
    image = future.result()
    return image

  def update_weather_location_woeid(self):
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_weather_location_woeid)
    self.woeid = future.result()

  def update_weather(self):
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_weather, self.woeid)
    weather = future.result()
    return weather

  def update(self, *args):
    if (datetime.datetime.now() - self.last_update_time).total_seconds() >= 1800:
      self.update_weather_location_woeid()
      weather = self.update_weather()

      self.weather_text.text = weather["weather_state_name"]
      self.low_text.text = str(weather["max_temp"])
      self.high_text.text = str(weather["min_temp"])

      self.image.texture = CoreImage(self.update_weather_image(weather["weather_state_abbr"]), ext='png').texture
      self.last_update_time = datetime.datetime.now()


class MoonWidget(GridLayout):
  def __init__(self, **kwargs):
    super(MoonWidget, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2
    moon_phase = self.update_moon_phase()

    self.moon_text = Label(text=moon_phase["phase"][arrow.now().strftime("%-d")]["npWidget"])
    self.image = Image(source=self.get_moon_pic(moon_phase["phase"][arrow.now().strftime("%-d")]["npWidget"]))

    self.add_widget(self.moon_text)
    self.add_widget(self.image)
    Clock.schedule_once(self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds + 60)

  def update_moon_phase(self):
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_moon_phase)
    moon_phase = future.result()
    return moon_phase

  def update(self, *args):
    moon_phase = self.update_moon_phase()
    self.moon_text.text = moon_phase["phase"][moon_phase["firstDayMonth"]]["npWidget"]
    self.image.source = self.get_moon_pic(moon_phase["phase"][arrow.now().strftime("%-d")]["npWidget"])

    Clock.schedule_once(self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds + 60)

  def get_moon_pic(self, moon_phase_text):
    # Images courtesy of freepik/flaticon
    if moon_phase_text.lower() == "full moon":
      return "res/full_moon.png"
    elif moon_phase_text.lower() == "new moon":
      return "res/new_moon.png"
    elif moon_phase_text.lower() == "first quarter":
      return "res/full_moon.png"
    elif moon_phase_text.lower() == "last quarter":
      return "res/full_moon.png"
    else:
      split_moon_phase = re.compile("\((.*)\)").split(moon_phase_text)
      percentage = split_moon_phase[1][:-1]
      if "Waning" in moon_phase_text:
        if int(percentage) < 50:
          return "res/waning_crescent.png"
        else:
          return "res/waning_gibbous.png"
      else:
        if int(percentage) < 50:
          return "res/waxing_crescent.png"
        else:
          return "res/waxing_gibbous.png"


class MainScreen(GridLayout):
  def __init__(self, **kwargs):
    super(MainScreen, self).__init__(**kwargs)
    self.cols = 2

    self.add_widget(TimePane())

    self.prayer_pane = PrayerPane(size_hint=(0.3, 1))
    self.add_widget(self.prayer_pane)


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
    Clock.schedule_once(self.reset_adhan, (time_of_prayer - datetime.datetime.now()).total_seconds() + 120)

    if fajr_alarm and self.prayer_time == 'Fajr':
      self.schedule_alarm_before_prayer()

  def schedule_alarm_before_prayer(self):
    time_of_prayer = self.get_time_of_prayer(self.todays_times[self.prayer_time])
    if time_of_prayer < datetime.datetime.now():
      time_of_prayer = self.get_time_of_prayer(self.tomorrow_times[self.prayer_time]) + datetime.timedelta(days=1)
    Clock.schedule_once(self.play_alarm, (time_of_prayer - datetime.datetime.now()).total_seconds() - 600)
    Clock.schedule_once(self.reset_alarm, (time_of_prayer - datetime.datetime.now()).total_seconds() - 600 + 17)

  def play_alarm(self, *args):
    alarm.play()

  def play_adhan(self, *args):
    adhan.play()

  def reset_alarm(self, *args):
    alarm.seek(0)

  def reset_adhan(self, *args):
    adhan.seek(0)

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


class SettingsScreen(GridLayout):
  def __init__(self, **kwargs):
    super(SettingsScreen, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2

    self.add_widget(Label(text="Settings", color=[1, 1, 1, 1],
                          font_name="RobotoMono-Regular",
                          size_hint=(1, 0.5), font_size="30sp"))
    self.add_widget(AlarmSetting())


class AlarmSetting(GridLayout):
  def __init__(self, **kwargs):
    super(AlarmSetting, self).__init__(**kwargs)
    self.cols = 2
    self.rows = 1
    self.add_widget(Label(text="Set alarm for 10 minutes before Fajr", color=[1, 1, 1, 1],
                          font_name="RobotoMono-Regular",
                          size_hint=(1, 0.5), font_size="10sp"))
    self.alarm_checkbox = CheckBox(active=fajr_alarm)
    self.alarm_checkbox.bind(active=update_fajr_alarm)
    self.add_widget(self.alarm_checkbox)
