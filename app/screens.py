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
import concurrent.futures
from config_handler import read_from_config, write_to_config
import datetime

keep_playing_alarm = True

fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode, use_hanafi_method = read_from_config()


def update_fajr_alarm(checkbox, value):
  """
  Updates the boolean that controls the fajr alarm, and updates the config file.
  :param checkbox: The checkbox, given by Kivy
  :param value: The value of the checkbox, given by Kivy
  :return:  None
  """
  global fajr_alarm
  global tahajjud_alarm
  global is_fahrenheit
  global enable_dark_mode
  global use_hanafi_method

  fajr_alarm = value

  write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode, use_hanafi_method)


default_text_color = [0.65, 0.81, 0.17, 1]
default_clock_color = [0, 0, 0, 1]

if enable_dark_mode:
  default_text_color = [0.61, 0.81, 0.01, 0.76]
  default_clock_color = [1, 1, 1, 1]


def update_tahajjud_alarm(checkbox, value):
  """
  Updates the boolean that controls the tahajjud alarm, and updates the config file.
  :param checkbox: The checkbox, given by Kivy
  :param value: The value of the checkbox, given by Kivy
  :return:  None
  """
  global fajr_alarm
  global tahajjud_alarm
  global is_fahrenheit
  global enable_dark_mode
  global use_hanafi_method

  tahajjud_alarm = value

  write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode, use_hanafi_method)


def update_fahrenheit_boolean(checkbox, value):
  """
  Updates the boolean that controls fahrenheit/celcius, and updates the config file.
  :param checkbox: The checkbox, given by Kivy
  :param value: The value of the checkbox, given by Kivy
  :return:  None
  """
  global fajr_alarm
  global tahajjud_alarm
  global is_fahrenheit
  global enable_dark_mode
  global use_hanafi_method

  is_fahrenheit = value

  write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode, use_hanafi_method)


def update_asr_juristic_method(checkbox, value):
  """
  Updates the boolean that controls fahrenheit/celcius, and updates the config file.
  :param checkbox: The checkbox, given by Kivy
  :param value: The value of the checkbox, given by Kivy
  :return:  None
  """
  global fajr_alarm
  global tahajjud_alarm
  global is_fahrenheit
  global enable_dark_mode
  global use_hanafi_method

  use_hanafi_method = value

  write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode, use_hanafi_method)


def update_enable_dark_mode(checkbox, value):
  """
  Updates the boolean that controls dark mode, updates the config file, and opens popup to exit app.
  :param checkbox: The checkbox, given by Kivy
  :param value: The value of the checkbox, given by Kivy
  :return:  None
  """
  global fajr_alarm
  global tahajjud_alarm
  global is_fahrenheit
  global enable_dark_mode
  global use_hanafi_method

  if value != enable_dark_mode:
    enable_dark_mode = value
    write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode, use_hanafi_method)

    exit_button = MDRaisedButton(text="Exit App")
    exit_button.bind(on_press=close_app)

    restart_popup = MDDialog(title='To update changes, you must restart app.',
                             size_hint=(0.75, 0.75),
                             buttons=[exit_button])
    restart_popup.open()


def close_app(*args):
  """
  Stops app
  :param args: Args given by Kivy
  :return: None
  """
  MDApp.get_running_app().stop()


def update_keep_playing_alarm(value):
  """
  Controls whether or not to continue playing the alarm
  :param value: A boolean to control whether or not to continue playing the alarm
  :return: None
  """
  global keep_playing_alarm

  keep_playing_alarm = value
  if not value:
    alarm.stop()
    alarm.seek(0)


def celcius_to_fahrenheit(celsius):
  """
  Converts a temperature from celcius to fahrenheit
  :param celsius: The temperature in Celcius
  :return: The converted fahrenheit temperature
  """
  return round((celsius * 9 / 5) + 32, 2)


adhan = SoundLoader.load('res/adhan.mp3')
adhan.seek(0)

alarm = SoundLoader.load('res/alarm/alarm.mp3')
alarm.seek(0)


def get_tomorrow_date():
  """
  Creates and returns a datetime object representing tomorrow at midnight
  :return: A datetime object representing tomorrow at midnight
  """
  today = datetime.datetime.today()
  today = today.replace(hour=0, minute=0, second=0, microsecond=0)
  return today + datetime.timedelta(days=1)


class MuezzinCarousel(Carousel):
  """
  Defines a Carousel that swipes left/right and holds an InformationScreen, MainScreen and SettingsScreen.
  """

  def __init__(self, **kwargs):
    """
    Creates a MuezzinCarousel.
    :param kwargs: Kwargs for MDGridLayout
    """
    super(MuezzinCarousel, self).__init__(**kwargs)
    self.information_screen = InformationScreen()
    self.main_screen = MainScreen()
    self.settings_screen = SettingsScreen()

    self.add_widget(self.information_screen)
    self.add_widget(self.main_screen)
    self.add_widget(self.settings_screen)
    self.index = 1

  def on_index(self, *args):
    """
    Updates different widgets when the Carousel index changes to the corresponding respective widget
    :param args: Args given by kivy
    :return: None
    """
    if self.index == 1:
      self.main_screen.prayer_pane.update()
    if self.index == 0:
      self.information_screen.update()
    Carousel.on_index(self, *args)


class InformationScreen(MDGridLayout):
  """
  Defines a wrapper widget which holds a moon widget, and weather widget along with some display text
  """

  def __init__(self, **kwargs):
    """
    Creates a InformationScreen.
    :param kwargs: Kwargs for MDGridLayout
    """
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
    """
    Updates MoonWidget and WeatherWidget
    :return: None
    """
    self.moon_widget.update()
    self.weather_widget.update()


class WeatherWidget(MDGridLayout):
  """
  Defines a Widget which displays the current weather condition, current temp, high temp, low temp and
  corresponding image of current weather.
  """

  def __init__(self, **kwargs):
    """
    Creates a WeatherWidgetLayout.
    :param kwargs: Kwargs for MDGridLayout
    """
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
    """
    Obtain image of a weather state given the abbreviation code for the weather state
    :param weather_state_abbr: The abbreviation code for the weather state
    :return: Image of current weather condition, in bytes
    """
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_weather_image, weather_state_abbr)
    image = future.result()
    return image

  def update_weather_location_woeid(self):
    """
    Updates woeid, which is the location ID for getting weather from the metaweather API.
    :return: None
    """
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_weather_location_woeid)
    self.woeid = future.result()

  def update_weather(self):
    """
    Calls API to get weather results from
    :return: Results from weather API call
    """
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_weather, self.woeid)
    weather = future.result()
    return weather

  def update(self, *args):
    """
    Updates text for current weather condition, current temp, high temp, low temp and the weather picture.
    :param args: Args given by Kivy
    :return: None
    """
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
  """
  A widget that displays the current moon phase along with a picture. Updates moon phase daily.
  """

  def __init__(self, **kwargs):
    """
    Creates a MoonWidget object
    :param kwargs: Kwargs for MDGridLayout
    """
    super(MoonWidget, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 2
    moon_phase = self.update_moon_phase()
    self.size_hint = (0.8, 0.8)
    self.orientation = "horizontal"
    self.moon_text = Label(text=moon_phase, color=default_text_color, font_name="RobotoMono-Regular", size_hint=(1, 1),
                           font_size="15sp")
    self.image = Image(source=self.get_moon_pic(moon_phase))

    self.add_widget(self.moon_text)
    self.add_widget(self.image)
    Clock.schedule_once(self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds + 60)

  def update_moon_phase(self):
    """
    Calls API to get current moon phase
    :return: Results of API call to get current moon phase
    """
    return getter.get_moon_phase()

  def update(self, *args):
    """
    Updates moon phase text and moon phase image and schedules daily updates.
    :param args: Args given by Kivy
    :return: None
    """
    moon_phase = self.update_moon_phase()
    self.moon_text.text = moon_phase
    self.image.source = self.get_moon_pic(moon_phase)

    Clock.schedule_once(self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds + 60)

  def get_moon_pic(self, moon_phase_text):
    """
    Returns a file path to a picture of a moon phase given a text describing the current moon phase
    :param moon_phase_text: The text describing the current moon phase
    :return: the file path to the current moon phase picture
    """

    # Images courtesy of freepik/flaticon
    if moon_phase_text.lower() == "full moon":
      return "res/full_moon.png"
    elif moon_phase_text.lower() == "new moon":
      return "res/new_moon.png"
    elif moon_phase_text.lower() == "first quarter":
      return "res/first_quarter.png"
    elif moon_phase_text.lower() == "last quarter":
      return "res/third_quarter.png"
    elif moon_phase_text.lower() == "new moon":
      return "res/new_moon.png"
    elif moon_phase_text.lower() == "waxing gibbous":
      return "res/waxing_gibbous.png"
    elif moon_phase_text.lower() == "waning gibbous":
      return "res/waning_gibbous.png"
    elif moon_phase_text.lower() == "waxing crescent":
      return "res/waxing_crescent.png"
    else:
      return "res/waning_crescent.png"


class MainScreen(MDGridLayout):
  """
  Root widget for the main screen which shows the clock time, hijri and gregorian dates and prayer times.
  """

  def __init__(self, **kwargs):
    """
    Create a MainScreen object
    :param kwargs: Kwargs for MDGridLayout
    """
    super(MainScreen, self).__init__(**kwargs)
    self.cols = 2

    self.add_widget(TimePane())

    self.prayer_pane = PrayerPane(size_hint=(0.3, 1))
    self.add_widget(self.prayer_pane)


class TimePane(MDGridLayout):
  """
  Displays and updates the current clock time
  """

  def __init__(self, **kwargs):
    """
    Create a TimePane object
    :param kwargs: Kwargs for MDGridLayout
    """
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
    """
    Schedules the clock time to update every minute
    :param args: Args given by Kivy
    :return: None
    """
    self.time_widget.text = datetime.datetime.now().strftime("%I:%M %p")
    Clock.schedule_once(self.update, 60 - datetime.datetime.now().second % 60)


class CalendarBox(MDGridLayout):
  """
  Holds Labels for displaying hijri and gregorian date, and
  holds logic for updating these dates, at their respective times of change.
  """

  def __init__(self, **kwargs):
    """
    Create a CalendarBox object
    :param kwargs: Kwargs for MDGridLayout
    """
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
    """
    Schedules a Clock schedule to update Gregorian date at midnight.
    :param args: Args given by Kivy
    :return: None
    """
    gregorian_date = getter.get_gregorian_date()
    self.gregorian_widget.text = gregorian_date["formatted_string"]

    Clock.schedule_once(self.update_gregorian, (self.get_tomorrow_date() - datetime.datetime.now()).seconds)

  def update_hijri(self, *args):
    """
    Schedules a Clock schedule to update Hijri date at maghrib time.
    :param args: Args given by Kivy
    :return: None
    """
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
    """
    Takes a clock time string and returns a datetime object of today with that time string
    :param time_string: A string of format "xx:xx pm/am" showing a certain clock time
    :param shift_tomorrow: A boolean that states whether to shift to the next Islamic day, if it's after maghrib
    :return: A datetime object with today's date, and the clock time corresponding to the time string
    """

    adhan_time = datetime.datetime.strptime(time_string, "%I:%M %p")
    today = datetime.datetime.today()
    today = today.replace(hour=adhan_time.hour, minute=adhan_time.minute, second=0, microsecond=0)
    if shift_tomorrow:
      today = today + datetime.timedelta(days=1)
    return today

  def update_hijri_date(self, is_tomorrow):
    """
    Updates the hijri date label
    :param is_tomorrow: A boolean that states whether it's after maghrib, i.e. is it the next Islamic day
    :return: None
    """
    future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_hijri_date, is_tomorrow)
    hijri_date = future.result()
    self.hijri_widget.text = str(hijri_date['day']) + " " + hijri_date['month'] + " " + str(hijri_date['year']) + " AH"

  def check_before_after_maghrib(self):
    """
    Checks whether current time is before or after maghrib
    :return: A boolean stating whether current time is before or after maghrib
    """
    current_time = datetime.datetime.now()
    maghrib_today = self.get_time_of_prayer(self.get_prayer_times()["Maghrib"])
    return current_time > maghrib_today

  def get_prayer_times(self):
    """
    Obtains today's prayer times from API
    :return: Returns today's prayer times in dict format
    """
    juristic_method = 0
    if use_hanafi_method:
      juristic_method = 1
    todays_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_today, juristic_method)
    return todays_times_future.result()

  def get_prayer_times_tomorrow(self):
    """
    Obtains tomorrow's prayer times from API
    :return: Returns tomorrow's prayer times in dict format
    """
    juristic_method = 0
    if use_hanafi_method:
      juristic_method = 1
    tomorrow_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_tomorrow,
                                                                           juristic_method)
    return tomorrow_times_future.result()


class PrayerPane(MDGridLayout):
  """
  Defines the pane holding the children PrayerTimeLayout widgets. Also defines logic for updating prayer times,
  and for scheduling a tahajjud alarm.
  """

  def __init__(self, **kwargs):
    """
    Create a PrayerPane object
    :param kwargs: Kwargs for MDGridLayout
    """
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
    """
    Updates today's and tomorrow's prayer times
    :return: None
    """
    juristic_method = 0
    if use_hanafi_method:
      juristic_method = 1
    todays_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_today, juristic_method)
    self.todays_times = todays_times_future.result()
    tomorrow_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_tomorrow,
                                                                           juristic_method)
    self.tomorrow_times = tomorrow_times_future.result()

  def update(self, *args):
    """
    Updates all child PrayerTimeLayout widgets and schedules tahajjud alarm if applicable.
    :param args: Args given by Kivy
    :return: None
    """
    self.get_prayer_times()
    for prayer_time in ["Fajr", "Duha", "Dhuhr", "Asr", "Maghrib", "Isha"]:
      self.prayer_time_widgets[prayer_time].update(self.todays_times, self.tomorrow_times)
    Clock.schedule_once(self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds)
    if tahajjud_alarm:
      self.schedule_alarm_tahajjud()

  def schedule_alarm_tahajjud(self):
    """
    Schedules alarm for the last third of night (for tahajjud).
    :return: None
    """
    tomorrows_fajr = self.get_time_of_prayer(self.tomorrow_times["Fajr"]) + datetime.timedelta(days=1)
    todays_isha = self.get_time_of_prayer(self.todays_times["Isha"])

    time_between_fajr_isha = (tomorrows_fajr - todays_isha).total_seconds()
    third_of_night = 2 / 3 * time_between_fajr_isha
    time_of_alarm = todays_isha + datetime.timedelta(seconds=third_of_night)
    Clock.schedule_once(self.play_alarm, (time_of_alarm - datetime.datetime.now()).total_seconds())
    Clock.schedule_once(self.reset_alarm, (time_of_alarm - datetime.datetime.now()).total_seconds() + 17)

  def get_time_of_prayer(self, time_string):
    """
    Takes a clock time string and returns a datetime object of today with that time string
    :param time_string: A string of format "xx:xx pm/am" showing a certain clock time
    :return: A datetime object with today's date, and the clock time corresponding to the time string
    """
    adhan_time = datetime.datetime.strptime(time_string, "%I:%M %p")
    today = datetime.datetime.today()
    today = today.replace(hour=adhan_time.hour, minute=adhan_time.minute, second=0, microsecond=0)
    return today

  def play_alarm(self, *args):
    """
    Plays alarm sound, and displays alarm popup
    :param args: Args given by Kivy
    :return: None
    """
    if not self.alarm_popup_service.is_open:
      self.alarm_popup_service.open()
    alarm.play()

  def reset_alarm(self, *args):
    """
    Resets alarm sound to the 0th time, and reschedules alarm if it's not dismissed yet.
    :param args: Args given by Kivy
    :return: None
    """
    alarm.seek(0)
    global keep_playing_alarm

    if keep_playing_alarm:
      Clock.schedule_once(self.play_alarm, 0)
      Clock.schedule_once(self.reset_alarm, 17)
    else:
      keep_playing_alarm = True


class PrayerTimeLayout(MDGridLayout):
  """
  Holds the UI logic, updating prayer time logic, adhan scheduling logic,
  and alarm scheduling logic (for Fajr) for a specific prayer time.
  """

  def __init__(self, prayer_time, todays_times, tomorrow_times, **kwargs):
    """
    Creates a PrayerTimeLayout object
    :param prayer_time: The prayer time as a string corresponding to this object
    :param todays_times: Today's prayer times in dict format
    :param tomorrow_times: Tomorrow's prayer times in dict format
    :param kwargs: Kwargs for MDGridLayout
    """
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
    """
    Schedules adhan to play at the specific prayer time
    :return: None
    """
    time_of_prayer = self.get_time_of_prayer(self.todays_times[self.prayer_time])
    if time_of_prayer < datetime.datetime.now():
      time_of_prayer = self.get_time_of_prayer(self.tomorrow_times[self.prayer_time]) + datetime.timedelta(days=1)
    Clock.schedule_once(self.play_adhan, (time_of_prayer - datetime.datetime.now()).total_seconds())
    Clock.schedule_once(self.reset_adhan, (time_of_prayer - datetime.datetime.now()).total_seconds() + 120)

    if fajr_alarm and self.prayer_time == 'Fajr':
      self.schedule_alarm_before_prayer()

  def schedule_alarm_before_prayer(self):
    """
    Schedules alarm 10 minutes before Fajr time
    :return: None
    """
    time_of_prayer = self.get_time_of_prayer(self.todays_times[self.prayer_time])
    if time_of_prayer < datetime.datetime.now():
      time_of_prayer = self.get_time_of_prayer(self.tomorrow_times[self.prayer_time]) + datetime.timedelta(days=1)
    Clock.schedule_once(self.play_alarm, (time_of_prayer - datetime.datetime.now()).total_seconds() - 600)
    Clock.schedule_once(self.reset_alarm, (time_of_prayer - datetime.datetime.now()).total_seconds() - 600 + 17)

  def play_alarm(self, *args):
    """
    Plays alarm sound, and displays alarm popup
    :param args: Args given by Kivy
    :return: None
    """
    alarm.play()
    if not self.alarm_popup_service.is_open:
      self.alarm_popup_service.open()

  def play_adhan(self, *args):
    """
    Plays adhan sound
    :param args: Args given by Kivy
    :return: None
    """
    adhan.play()

  def reset_alarm(self, *args):
    """
    Resets alarm sound to the 0th time, and reschedules alarm if it's not dismissed yet.
    :param args: Args given by Kivy
    :return: None
    """
    alarm.seek(0)
    global keep_playing_alarm

    if keep_playing_alarm:
      Clock.schedule_once(self.play_alarm, 0)
      Clock.schedule_once(self.reset_alarm, 17)
    else:
      keep_playing_alarm = True

  def reset_adhan(self, *args):
    """
    Resets adhan sound to the 0th time
    :param args: Args given by Kivy
    :return: None
    """
    adhan.seek(0)

  def get_time_of_prayer(self, time_string):
    """
    Takes a clock time string and returns a datetime object of today with that time string
    :param time_string: A string of format "xx:xx pm/am" showing a certain clock time
    :return: A datetime object with today's date, and the clock time corresponding to the time string
    """
    adhan_time = datetime.datetime.strptime(time_string, "%I:%M %p")
    today = datetime.datetime.today()
    today = today.replace(hour=adhan_time.hour, minute=adhan_time.minute, second=0, microsecond=0)
    return today

  def update(self, todays_times, tomorrow_times):
    """
    Updates the Labels and updates the adhan schedule with newly updated times.
    :param todays_times: Today's prayer times in dict format
    :param tomorrow_times: Tomorrow's prayer times in dict format
    :return: None
    """
    self.todays_times = todays_times
    self.tomorrow_times = tomorrow_times
    self.todays_time_widget.text = self.prayer_time + ": " + todays_times[self.prayer_time]
    self.tomorrows_time_widget.text = "Tomorrow: " + tomorrow_times[self.prayer_time]
    self.schedule_adhan()


class WrappedLabel(Label):
  """
  A subclass of Label which supports wrapping text automatically.
  """

  # Courtesy of https://stackoverflow.com/questions/43666381/wrapping-the-text-of-a-kivy-label
  def __init__(self, **kwargs):
    """
    Creates a WrappedLabel object
    :param kwargs: Arguments for Label
    """
    super().__init__(**kwargs)
    self.bind(
      width=lambda *x:
      self.setter('text_size')(self, (self.width, None)),
      texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))


class SettingsScreen(MDGridLayout):
  """
  Holds the different setting objects
  """

  def __init__(self, **kwargs):
    """
    Creates a SettingsScreen object
    :param kwargs: Arguments for MDGridLayout
    """
    super(SettingsScreen, self).__init__(**kwargs)
    self.cols = 1
    self.rows = 6

    self.add_widget(Label(text="Settings", color=default_text_color,
                          font_name="RobotoMono-Regular",
                          size_hint=(1, 0.5), font_size="30sp"))
    self.add_widget(FajrAlarmSetting())
    self.add_widget(TahajjudAlarmSetting())
    self.add_widget(AsrJuristicMethodSetting())
    self.add_widget(TemperatureUnitSetting())
    self.add_widget(EnableDarkModeSetting())


class FajrAlarmSetting(AnchorLayout):
  """
  Holds a Label and MDSwitch which controls whether or not a Fajr Alarm is on
  """

  def __init__(self, **kwargs):
    """
    Creates a FajrAlarmSetting object
    :param kwargs: Arguments for Anchor Layout
    """
    super(FajrAlarmSetting, self).__init__(**kwargs)

    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(
      Label(text="Set alarm for 10 minutes before Fajr", color=default_text_color, font_name="RobotoMono-Regular",
            size_hint=(1, 0.5), font_size="10sp"))

    self.alarm_checkbox = MDSwitch(active=fajr_alarm)
    self.alarm_checkbox.bind(active=update_fajr_alarm)
    self.alarm_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
    self.alarm_checkbox_anchor_layout.add_widget(self.alarm_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.alarm_checkbox_anchor_layout)


class TahajjudAlarmSetting(AnchorLayout):
  """
  Holds a Label and MDSwitch which controls whether or not a Tahajjud Alarm is on
  """

  def __init__(self, **kwargs):
    """
    Creates a TahajjudAlarmSetting object
    :param kwargs: Arguments for Anchor Layout
    """
    super(TahajjudAlarmSetting, self).__init__(**kwargs)

    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(Label(text="Set alarm for last third of night", color=default_text_color,
                                             font_name="RobotoMono-Regular",
                                             size_hint=(1, 0.5), font_size="10sp"))

    self.alarm_checkbox = MDSwitch(active=tahajjud_alarm)
    self.alarm_checkbox.bind(active=update_tahajjud_alarm)
    self.alarm_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
    self.alarm_checkbox_anchor_layout.add_widget(self.alarm_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.alarm_checkbox_anchor_layout)


class TemperatureUnitSetting(AnchorLayout):
  """
  Holds a Label and MDSwitch which controls whether or not we use fahrenheit/celcius.
  """

  def __init__(self, **kwargs):
    """
    Creates a TemperatureUnitSetting object
    :param kwargs: Arguments for Anchor Layout
    """
    super(TemperatureUnitSetting, self).__init__(**kwargs)
    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(
      Label(text="Display temp in Fahrenheit (default: Celcius)", color=default_text_color,
            font_name="RobotoMono-Regular",
            size_hint=(1, 0.5), font_size="10sp"))

    self.temp_checkbox = MDSwitch(active=is_fahrenheit)
    self.temp_checkbox.bind(active=update_fahrenheit_boolean)
    self.temp_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
    self.temp_checkbox_anchor_layout.add_widget(self.temp_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.temp_checkbox_anchor_layout)


class AsrJuristicMethodSetting(AnchorLayout):
  """
  Holds a Label and MDSwitch which controls what juristic method is used to calculate Asr times.
  """

  def __init__(self, **kwargs):
    """
    Creates a AsrJuristicMethodSetting object
    :param kwargs: Arguments for Anchor Layout
    """
    super(AsrJuristicMethodSetting, self).__init__(**kwargs)
    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(
      Label(text="Use Hanaji juristic method for Asr", color=default_text_color,
            font_name="RobotoMono-Regular",
            size_hint=(1, 0.5), font_size="10sp"))

    self.asr_juristic_checkbox = MDSwitch(active=use_hanafi_method)
    self.asr_juristic_checkbox.bind(active=update_asr_juristic_method)
    self.asr_juristic_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
    self.asr_juristic_checkbox_anchor_layout.add_widget(self.asr_juristic_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.asr_juristic_checkbox_anchor_layout)


class EnableDarkModeSetting(AnchorLayout):
  """
  Holds a Label and MDSwitch which controls whether or not dark mode is on.
  """

  def __init__(self, **kwargs):
    """
    Creates an EnableDarkModeSetting object
    :param kwargs: Arguments for Anchor Layout
    """
    super(EnableDarkModeSetting, self).__init__(**kwargs)
    self.text_anchor_layout = AnchorLayout(anchor_x='left', anchor_y='top')
    self.text_anchor_layout.add_widget(
      Label(text="Enable Dark Mode", color=default_text_color, font_name="RobotoMono-Regular", size_hint=(1, 0.5),
            font_size="10sp"))

    self.dark_mode_checkbox = MDSwitch(active=enable_dark_mode)
    self.dark_mode_checkbox.bind(active=update_enable_dark_mode)
    self.dark_mode_checkbox_anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')
    self.dark_mode_checkbox_anchor_layout.add_widget(self.dark_mode_checkbox)

    self.add_widget(self.text_anchor_layout)
    self.add_widget(self.dark_mode_checkbox_anchor_layout)


class AlarmDismissPopup:
  """
  Creates a MDDialog to dismiss the alarm and holds logic to show dialog, dismiss dialog and shut off alarm.
  """

  def __init__(self):
    """
    Creates an AlarmDismissPopup
    """
    self.popup_layout = MDGridLayout(cols=1, padding=10)

    self.dismiss_button = MDRaisedButton(text="Dismiss")
    self.dismiss_button.bind(on_press=self.dismiss)

    self.alarm_popup = MDDialog(title='Dismiss Alarm',
                                size_hint=(0.75, 0.75),
                                buttons=[self.dismiss_button])
    self.alarm_popup.on_touch_up(self.dismiss)
    self.is_open = False

  def dismiss(self, *args):
    """
    Dismisses the alarm popup and silences the alarm.
    :param args: Args sent by Kivy
    :return: None
    """
    self.alarm_popup.dismiss()
    update_keep_playing_alarm(False)
    self.is_open = False

  def open(self):
    """
    Opens the alarm dismissal popup
    :return: None
    """
    self.alarm_popup.open()
    self.is_open = True
