from kivy.core.audio import SoundLoader
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.carousel import Carousel
from kivy.clock import Clock
from kivy.uix.image import CoreImage, Image
from kivy.uix.label import Label

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.selectioncontrol import MDSwitch

import api_controller as getter
import arrow
import concurrent.futures
from config_handler import read_from_config, write_to_config
import datetime
import re

keep_playing_alarm = True

fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode = read_from_config()


def update_fajr_alarm(checkbox, value):
  global fajr_alarm
  global tahajjud_alarm
  global is_fahrenheit
  global enable_dark_mode

  fajr_alarm = value

  write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode)


default_text_color = [0.65, 0.81, 0.17, 1]
default_clock_color = [0, 0, 0, 1]

if enable_dark_mode:
  default_text_color = [0.61, 0.81, 0.01, 0.76]
  default_clock_color = [1, 1, 1, 1]


def update_tahajjud_alarm(checkbox, value):
  global fajr_alarm
  global tahajjud_alarm
  global is_fahrenheit
  global enable_dark_mode

  tahajjud_alarm = value

  write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode)


def update_fahrenheit_boolean(checkbox, value):
  global fajr_alarm
  global tahajjud_alarm
  global is_fahrenheit
  global enable_dark_mode

  is_fahrenheit = value

  write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode)


def update_enable_dark_mode(checkbox, value):
  global fajr_alarm
  global tahajjud_alarm
  global is_fahrenheit
  global enable_dark_mode

  if value != enable_dark_mode:
    enable_dark_mode = value
    write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode)

    exit_button = MDRaisedButton(text="Exit App")
    exit_button.bind(on_press=close_app)

    restart_popup = MDDialog(title='To update changes, you must restart app.',
                             size_hint=(0.75, 0.75),
                             buttons=[exit_button])
    restart_popup.open()


def close_app(*args):
  MDApp.get_running_app().stop()


def update_keep_playing_alarm(value):
  global keep_playing_alarm

  keep_playing_alarm = value
  if not value:
    alarm.stop()
    alarm.seek(0)


def celcius_to_fahrenheit(celsius):
  return round((celsius * 9 / 5) + 32, 2)


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


class InformationScreen(MDGridLayout):
  def __init__(self, **kwargs):
    super(InformationScreen, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 4
    self.moon_widget = MoonWidget()
    self.weather_widget = WeatherWidget()
    self.add_widget(Label(text="Current moon phase", color=default_text_color, font_name="RobotoMono-Regular",
                          size_hint=(0.5, 0.5), font_size="25sp"))
    self.add_widget(self.moon_widget)
    self.add_widget(
      Label(text="Current Weather", color=default_text_color, font_name="RobotoMono-Regular", size_hint=(1, 0.5),
            font_size="25sp"))
    self.add_widget(self.weather_widget)

  def update(self):
    self.moon_widget.update()
    self.weather_widget.update()


class WeatherWidget(MDGridLayout):
  def __init__(self, **kwargs):
    super(WeatherWidget, self).__init__(**kwargs)
    self.cols = 2
    self.rows = 3
    self.woeid = None
    self.update_weather_location_woeid()
    self.weather = self.update_weather()

    self.weather_text = Label(text=self.weather["weather_state_name"], color=default_text_color,
                              font_name="RobotoMono-Regular", size_hint=(1, 1), font_size="15sp")
    self.current_text = Label(color=default_text_color, font_name="RobotoMono-Regular", size_hint=(1, 1),
                              font_size="15sp")
    self.low_text = Label(color=default_text_color, font_name="RobotoMono-Regular", size_hint=(1, 1),
                          font_size="10sp")
    self.high_text = Label(color=default_text_color, font_name="RobotoMono-Regular", size_hint=(1, 1),
                           font_size="10sp")
    if is_fahrenheit:
      self.current_text.text = "Current: " + ('%.2f' % celcius_to_fahrenheit(self.weather["the_temp"])) + " °F"
      self.low_text.text = "High: " + ('%.2f' % celcius_to_fahrenheit(self.weather["max_temp"])) + " °F"
      self.high_text.text = "Low: " + ('%.2f' % celcius_to_fahrenheit(self.weather["min_temp"])) + " °F"
    else:
      self.current_text.text = "Current: " + ('%.2f' % self.weather["the_temp"]) + " °C"
      self.low_text.text = "High: " + ('%.2f' % self.weather["max_temp"]) + " °C"
      self.high_text.text = "Low: " + ('%.2f' % self.weather["min_temp"]) + " °C"

    self.image = Image()
    self.image.texture = CoreImage(self.update_weather_image(self.weather["weather_state_abbr"]), ext='png').texture

    self.weather_text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.current_text_anchor_layout = AnchorLayout(anchor_x='right', anchor_y='top')
    self.low_text_anchor_layout = AnchorLayout(anchor_x='right', anchor_y='bottom')
    self.high_text_anchor_layout = AnchorLayout(anchor_x='right', anchor_y='center')
    self.image_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='bottom')

    self.weather_text_anchor_layout.add_widget(self.weather_text)
    self.current_text_anchor_layout.add_widget(self.current_text)
    self.high_text_anchor_layout.add_widget(self.low_text)
    self.low_text_anchor_layout.add_widget(self.high_text)
    self.image_anchor_layout.add_widget(self.image)

    self.add_widget(self.weather_text_anchor_layout)
    self.add_widget(self.current_text_anchor_layout)
    self.add_widget(self.high_text_anchor_layout)
    self.add_widget(self.image_anchor_layout)
    self.add_widget(self.low_text_anchor_layout)
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
      self.weather = self.update_weather()

      self.weather_text.text = self.weather["weather_state_name"]

      self.image.texture = CoreImage(self.update_weather_image(self.weather["weather_state_abbr"]), ext='png').texture
      self.last_update_time = datetime.datetime.now()

    if is_fahrenheit:
      self.current_text.text = "Current: " + ('%.2f' % celcius_to_fahrenheit(self.weather["the_temp"])) + " °F"
      self.low_text.text = "High: " + ('%.2f' % celcius_to_fahrenheit(self.weather["max_temp"])) + " °F"
      self.high_text.text = "Low: " + ('%.2f' % celcius_to_fahrenheit(self.weather["min_temp"])) + " °F"
    else:
      self.current_text.text = "Current: " + ('%.2f' % self.weather["the_temp"]) + " °C"
      self.low_text.text = "High: " + ('%.2f' % self.weather["max_temp"]) + " °C"
      self.high_text.text = "Low: " + ('%.2f' % self.weather["min_temp"]) + " °C"


class MoonWidget(MDGridLayout):
  def __init__(self, **kwargs):
    super(MoonWidget, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2
    moon_phase = self.update_moon_phase()
    self.size_hint = (0.8, 0.8)
    self.orientation = "horizontal"
    self.moon_text = Label(text=moon_phase["phase"][arrow.now().strftime("%-d")]["npWidget"],
                           color=default_text_color, font_name="RobotoMono-Regular", size_hint=(1, 1),
                           font_size="15sp")
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
      return "res/first_quarter.png"
    elif moon_phase_text.lower() == "last quarter":
      return "res/third_quarter.png"
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


class MainScreen(MDGridLayout):
  def __init__(self, **kwargs):
    super(MainScreen, self).__init__(**kwargs)
    self.cols = 2

    self.add_widget(TimePane())

    self.prayer_pane = PrayerPane(size_hint=(0.3, 1))
    self.add_widget(self.prayer_pane)


class TimePane(MDGridLayout):
  def __init__(self, **kwargs):
    super(TimePane, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2
    self.time_widget = Label(text=datetime.datetime.now().strftime("%I:%M %p"), color=default_clock_color,
                             font_name="RobotoMono-Regular",
                             size_hint=(1, 0.5), font_size="50sp")

    self.add_widget(CalendarBox(size_hint=(1, 0.5)))
    self.add_widget(self.time_widget)

    Clock.schedule_once(self.update, 60 - datetime.datetime.now().second % 60)

  def update(self, *args):
    self.time_widget.text = datetime.datetime.now().strftime("%I:%M %p")
    Clock.schedule_once(self.update, 60 - datetime.datetime.now().second % 60)


class CalendarBox(MDGridLayout):
  def __init__(self, **kwargs):
    super(CalendarBox, self).__init__(**kwargs)
    self.cols = 3
    self.rows = 1
    gregorian_date = getter.get_gregorian_date()
    self.gregorian_widget = WrappedLabel(text=gregorian_date["formatted_string"], color=default_text_color,
                                         font_name="Roboto-Bold", font_size="16sp", size_hint=(0.5, 1),
                                         padding=("10sp", "0sp"))

    self.hijri_widget = WrappedLabel(text="14 Ramadan 1440 AH", color=default_text_color, font_name="Roboto-Bold",
                                     font_size="16sp", size_hint=(0.5, 1), padding=("10sp", "0sp"))
    self.update_hijri()
    # Logo courtesy of flaticon
    if enable_dark_mode:
      self.add_widget(Image(source="res/mosque_white.png", keep_ratio=True, size_hint_x=0.1, pos=(0, 0)))
    else:
      self.add_widget(Image(source="res/mosque_dark.png", keep_ratio=True, size_hint_x=0.1, pos=(0, 0)))
    self.add_widget(self.gregorian_widget)
    self.add_widget(self.hijri_widget)

    Clock.schedule_once(self.update_gregorian, (get_tomorrow_date() - datetime.datetime.now()).seconds)

  def update_gregorian(self, *args):
    gregorian_date = getter.get_gregorian_date()
    self.gregorian_widget.text = gregorian_date["formatted_string"]

    Clock.schedule_once(self.update_gregorian, (self.get_tomorrow_date() - datetime.datetime.now()).seconds)

  def update_hijri(self, *args):
    is_after_maghrib = self.check_before_after_maghrib()
    self.update_hijri_date(is_after_maghrib)
    if is_after_maghrib:
      Clock.schedule_once(self.update_hijri, (
              self.get_time_of_prayer(self.get_prayer_times_tomorrow()["Maghrib"],
                                      shift_tomorrow=True) - datetime.datetime.now()).seconds)
    else:
      Clock.schedule_once(self.update_hijri, (
              self.get_time_of_prayer(self.get_prayer_times()["Maghrib"]) - datetime.datetime.now()).seconds)

  def get_time_of_prayer(self, time_string, shift_tomorrow=False):
    adhan_time = datetime.datetime.strptime(time_string, "%I:%M %p")
    today = datetime.datetime.today()
    today = today.replace(hour=adhan_time.hour, minute=adhan_time.minute, second=0, microsecond=0)
    if shift_tomorrow:
      today = today + datetime.timedelta(days=1)
    return today

  def update_hijri_date(self, is_tomorrow):
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_hijri_date, is_tomorrow)
    hijri_date = future.result()
    self.hijri_widget.text = str(hijri_date['day']) + " " + hijri_date['month'] + " " + str(hijri_date['year']) + " AH"

  def check_before_after_maghrib(self):
    current_time = datetime.datetime.now()
    maghrib_today = self.get_time_of_prayer(self.get_prayer_times()["Maghrib"])
    return current_time > maghrib_today

  def get_prayer_times(self):
    todays_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_today)
    return todays_times_future.result()

  def get_prayer_times_tomorrow(self):
    tomorrow_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_tomorrow)
    return tomorrow_times_future.result()


class PrayerPane(MDGridLayout):
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
    self.alarm_popup_service = AlarmDismissPopup()

  def get_prayer_times(self):
    todays_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_today)
    self.todays_times = todays_times_future.result()
    tomorrow_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_tomorrow)
    self.tomorrow_times = tomorrow_times_future.result()

  def update(self, *args):
    for prayer_time in ["Fajr", "Duha", "Dhuhr", "Asr", "Maghrib", "Isha"]:
      self.prayer_time_widgets[prayer_time].update(self.todays_times, self.tomorrow_times)
    Clock.schedule_once(self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds)
    if tahajjud_alarm:
      self.schedule_alarm_tahajjud()

  def schedule_alarm_tahajjud(self):
    tomorrows_fajr = self.get_time_of_prayer(self.tomorrow_times["Fajr"]) + datetime.timedelta(days=1)
    todays_isha = self.get_time_of_prayer(self.todays_times["Isha"])

    time_between_fajr_isha = (tomorrows_fajr - todays_isha).total_seconds()
    third_of_night = 2 / 3 * time_between_fajr_isha
    time_of_alarm = todays_isha + datetime.timedelta(seconds=third_of_night)
    Clock.schedule_once(self.play_alarm, (time_of_alarm - datetime.datetime.now()).total_seconds())
    Clock.schedule_once(self.reset_alarm, (time_of_alarm - datetime.datetime.now()).total_seconds() + 17)

  def get_time_of_prayer(self, time_string):
    adhan_time = datetime.datetime.strptime(time_string, "%I:%M %p")
    today = datetime.datetime.today()
    today = today.replace(hour=adhan_time.hour, minute=adhan_time.minute, second=0, microsecond=0)
    return today

  def play_alarm(self, *args):
    if not self.alarm_popup_service.is_open:
      self.alarm_popup_service.open()
    alarm.play()

  def reset_alarm(self, *args):
    alarm.seek(0)
    global keep_playing_alarm

    if keep_playing_alarm:
      Clock.schedule_once(self.play_alarm, 0)
      Clock.schedule_once(self.reset_alarm, 17)
    else:
      keep_playing_alarm = True


class PrayerTimeLayout(MDGridLayout):
  def __init__(self, prayer_time, todays_times, tomorrow_times, **kwargs):
    super(PrayerTimeLayout, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2

    self.prayer_time = prayer_time
    self.todays_times = todays_times
    self.tomorrow_times = tomorrow_times

    self.todays_time_widget = WrappedLabel(text=self.prayer_time + ": " + self.todays_times[self.prayer_time],
                                           color=default_text_color, font_name="Roboto-BoldItalic",
                                           font_size="15sp")
    self.tomorrows_time_widget = WrappedLabel(text="Tomorrow: " + self.tomorrow_times[self.prayer_time],
                                              color=default_text_color, font_name="Roboto-BoldItalic",
                                              font_size="8sp")
    self.add_widget(self.todays_time_widget)
    self.add_widget(self.tomorrows_time_widget)
    self.alarm_popup_service = AlarmDismissPopup()

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
    if not self.alarm_popup_service.is_open:
      self.alarm_popup_service.open()

  def play_adhan(self, *args):
    adhan.play()

  def reset_alarm(self, *args):
    alarm.seek(0)
    global keep_playing_alarm

    if keep_playing_alarm:
      Clock.schedule_once(self.play_alarm, 0)
      Clock.schedule_once(self.reset_alarm, 17)
    else:
      keep_playing_alarm = True

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


class SettingsScreen(MDGridLayout):
  def __init__(self, **kwargs):
    super(SettingsScreen, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 5

    self.add_widget(Label(text="Settings", color=default_text_color,
                          font_name="RobotoMono-Regular",
                          size_hint=(1, 0.5), font_size="40sp"))
    self.add_widget(FajrAlarmSetting())
    self.add_widget(TahajjudAlarmSetting())
    self.add_widget(TemperatureUnitSetting())
    self.add_widget(EnableDarkModeSetting())


class FajrAlarmSetting(AnchorLayout):
  def __init__(self, **kwargs):
    super(FajrAlarmSetting, self).__init__(**kwargs)

    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(
      Label(text="Set alarm for 10 minutes before Fajr", color=default_text_color, font_name="RobotoMono-Regular",
            size_hint=(1, 0.5), font_size="10sp"))

    self.alarm_checkbox = MDSwitch(active=fajr_alarm)
    self.alarm_checkbox.bind(active=update_fajr_alarm)
    self.alarm_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
    self.alarm_checkbox_anchor_layout.add_widget(self.alarm_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.alarm_checkbox_anchor_layout)


class TahajjudAlarmSetting(AnchorLayout):
  def __init__(self, **kwargs):
    super(TahajjudAlarmSetting, self).__init__(**kwargs)

    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(Label(text="Set alarm for last third of night", color=default_text_color,
                                             font_name="RobotoMono-Regular",
                                             size_hint=(1, 0.5), font_size="10sp"))

    self.alarm_checkbox = MDSwitch(active=tahajjud_alarm)
    self.alarm_checkbox.bind(active=update_tahajjud_alarm)
    self.alarm_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
    self.alarm_checkbox_anchor_layout.add_widget(self.alarm_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.alarm_checkbox_anchor_layout)


class TemperatureUnitSetting(AnchorLayout):
  def __init__(self, **kwargs):
    super(TemperatureUnitSetting, self).__init__(**kwargs)
    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(
      Label(text="Check for Fahrenheit (default: Celcius)", color=default_text_color,
            font_name="RobotoMono-Regular",
            size_hint=(1, 0.5), font_size="10sp"))

    self.temp_checkbox = MDSwitch(active=is_fahrenheit)
    self.temp_checkbox.bind(active=update_fahrenheit_boolean)
    self.temp_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
    self.temp_checkbox_anchor_layout.add_widget(self.temp_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.temp_checkbox_anchor_layout)


class EnableDarkModeSetting(AnchorLayout):
  def __init__(self, **kwargs):
    super(EnableDarkModeSetting, self).__init__(**kwargs)
    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(
      Label(text="Enable Dark Mode", color=default_text_color, font_name="RobotoMono-Regular", size_hint=(1, 0.5),
            font_size="10sp"))

    self.dark_mode_checkbox = MDSwitch(active=enable_dark_mode)
    self.dark_mode_checkbox.bind(active=update_enable_dark_mode)
    self.dark_mode_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
    self.dark_mode_checkbox_anchor_layout.add_widget(self.dark_mode_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.dark_mode_checkbox_anchor_layout)


class AlarmDismissPopup:
  def __init__(self):
    self.popup_layout = MDGridLayout(cols=1, padding=10)

    self.dismiss_button = MDRaisedButton(text="Dismiss")
    self.dismiss_button.bind(on_press=self.dismiss)

    self.alarm_popup = MDDialog(title='Dismiss Alarm',
                                size_hint=(0.75, 0.75),
                                buttons=[self.dismiss_button])
    self.alarm_popup.on_touch_up(self.dismiss)
    self.is_open = False

  def dismiss(self, *args):
    self.alarm_popup.dismiss()
    update_keep_playing_alarm(False)
    self.is_open = False

  def open(self):
    self.alarm_popup.open()
    self.is_open = True
