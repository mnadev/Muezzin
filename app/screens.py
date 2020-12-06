from kivy.core.audio import SoundLoader
from kivy.uix.carousel import Carousel
from kivy.clock import Clock
from kivy.uix.image import CoreImage, Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.label import MDLabel
import api_controller as getter
import arrow
import concurrent.futures
import datetime
import re
import time

fajr_alarm = False
is_fahrenheit = False
tahajjud_alarm = False
keep_playing_alarm = True


def update_fajr_alarm(checkbox, value):
  global fajr_alarm
  fajr_alarm = value


def update_tahajjud_alarm(checkbox, value):
  global tahajjud_alarm
  tahajjud_alarm = value


def update_fahrenheit_boolean(checkbox, value):
  global is_fahrenheit
  is_fahrenheit = value


def update_keep_playing_alarm(value):
  global keep_playing_alarm

  keep_playing_alarm = value
  if not value:
    alarm.stop()
    time.sleep(1)
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
    self.add_widget(Label(text="Current moon phase", color=[0.61, 0.81, 0.01, 0.76], font_name="RobotoMono-Regular",
                          size_hint=(0.5, 0.5), font_size="25sp"))
    self.add_widget(self.moon_widget)
    self.add_widget(
      Label(text="Current Weather", color=[0.61, 0.81, 0.01, 0.76], font_name="RobotoMono-Regular", size_hint=(1, 0.5),
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

    self.weather_text = Label(text=self.weather["weather_state_name"], color=[0.61, 0.81, 0.01, 0.76],
                              font_name="RobotoMono-Regular", size_hint=(1, 1), font_size="15sp")
    self.current_text = Label(color=[0.61, 0.81, 0.01, 0.76], font_name="RobotoMono-Regular", size_hint=(1, 1),
                              font_size="15sp")
    self.low_text = Label(color=[0.61, 0.81, 0.01, 0.76], font_name="RobotoMono-Regular", size_hint=(1, 1),
                          font_size="10sp")
    self.high_text = Label(color=[0.61, 0.81, 0.01, 0.76], font_name="RobotoMono-Regular", size_hint=(1, 1),
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
                           color=[0.61, 0.81, 0.01, 0.76], font_name="RobotoMono-Regular", size_hint=(1, 1),
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
    self.time_widget = Label(text=datetime.datetime.now().strftime("%I:%M %p"), color=[1, 1, 1, 1],
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
    self.gregorian_widget = WrappedLabel(text=gregorian_date["formatted_string"], color=[0.61, 0.81, 0.01, 0.76],
                                         font_name="Roboto-Bold", font_size="16sp", size_hint=(0.5, 1),
                                         padding=("10sp", "0sp"))

    self.hijri_widget = WrappedLabel(text="14 Ramadan 1440 AH", color=[0.61, 0.81, 0.01, 0.76], font_name="Roboto-Bold",
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
                                           color=[0.61, 0.81, 0.01, 0.76], font_name="Roboto-BoldItalic",
                                           font_size="15sp")
    self.tomorrows_time_widget = WrappedLabel(text="Tomorrow: " + self.tomorrow_times[self.prayer_time],
                                              color=[0.61, 0.81, 0.01, 0.76], font_name="Roboto-BoldItalic",
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
    self.rows = 4

    self.add_widget(Label(text="Settings", color=[0.61, 0.81, 0.01, 0.76],
                          font_name="RobotoMono-Regular",
                          size_hint=(1, 0.5), font_size="40sp"))
    self.add_widget(FajrAlarmSetting())
    self.add_widget(TahajjudAlarmSetting())
    self.add_widget(TemperatureUnitSetting())


class FajrAlarmSetting(AnchorLayout):
  def __init__(self, **kwargs):
    super(FajrAlarmSetting, self).__init__(**kwargs)

    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(
      Label(text="Set alarm for 10 minutes before Fajr", color=[0.61, 0.81, 0.01, 0.76], font_name="RobotoMono-Regular",
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
    self.text_anchor_layout.add_widget(Label(text="Set alarm for last third of night", color=[0.61, 0.81, 0.01, 0.76],
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
      Label(text="Check for Fahrenheit (default: Celcius)", color=[0.61, 0.81, 0.01, 0.76],
            font_name="RobotoMono-Regular",
            size_hint=(1, 0.5), font_size="10sp"))

    self.temp_checkbox = MDSwitch(active=is_fahrenheit)
    self.temp_checkbox.bind(active=update_fahrenheit_boolean)
    self.temp_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
    self.temp_checkbox_anchor_layout.add_widget(self.temp_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.temp_checkbox_anchor_layout)


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
