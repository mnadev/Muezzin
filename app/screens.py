from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.label import Label

from kivymd.uix.button import MDRectangleFlatIconButton
from kivymd.uix.gridlayout import MDGridLayout

from alarm_popup import AlarmDismissPopup
import api_controller as getter
from audio_player import AudioPlayer
import concurrent.futures
from config_handler import ConfigHandler
import constants
import datetime
from helper import get_tomorrow_date
from moon_widget import MoonWidget
from weather_widget import WeatherWidget

audio_player = AudioPlayer()
config_handler = ConfigHandler()

default_text_color = [0.65, 0.7, 0.01, 1]
default_clock_color = [0, 0, 0, 1]

if True:
  default_text_color = [0.61, 0.81, 0.01, 0.76]
  default_clock_color = [1, 1, 1, 1]


adhan = SoundLoader.load('res/adhan.mp3')
adhan.seek(0)

fajr_adhan = SoundLoader.load('res/fajr_adhan.mp3')
fajr_adhan.seek(0)

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
    self.prayer_pane.update()


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
    self.rows = 3
    self.time_widget = Label(text=datetime.datetime.now().strftime("%I:%M %p"), color=default_clock_color,
                             font_name="RobotoMono-Regular",
                             size_hint=(1, 0.5), font_size="50sp")

    self.add_widget(CalendarBox(size_hint=(1, 0.5)))
    self.add_widget(self.time_widget)

    Clock.schedule_once(self.update, 60 - datetime.datetime.now().second % 60)

    self.adhan_play_button = MDRectangleFlatIconButton(icon="play",
                                                       text="Play adhan",
                                                       text_color=default_clock_color)
    self.adhan_play_button.bind(on_press=self.play_adhan)
    self.add_widget(self.adhan_play_button)


  def update(self, *args):
    """
    Schedules the clock time to update every minute
    :param args: Args given by Kivy
    :return: None
    """
    self.time_widget.text = datetime.datetime.now().strftime("%I:%M %p")
    Clock.schedule_once(self.update, 60 - datetime.datetime.now().second % 60)

  def play_adhan(self, *args):
    """
    Plays adhan sound
    :param args: Args given by Kivy
    :return: None
    """
    Clock.schedule_once(self.reset_adhan, 120)
    adhan.play()

  def reset_adhan(self, *args):
    """
    Resets adhan sound to the 0th time
    :param args: Args given by Kivy
    :return: None
    """
    adhan.seek(0)

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
    if config_handler.get_setting(constants.CONFIG_ENABLE_DARK_MODE_KEY):
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

    Clock.schedule_once(self.update_gregorian, (get_tomorrow_date() - datetime.datetime.now()).seconds)

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
    if config_handler.get_setting(constants.CONFIG_USE_HANAFI_METHOD_KEY):
      juristic_method = 1
    todays_times_future = concurrent.futures.ThreadPoolExecutor().submit(getter.get_prayer_times_today, juristic_method)
    return todays_times_future.result()

  def get_prayer_times_tomorrow(self):
    """
    Obtains tomorrow's prayer times from API
    :return: Returns tomorrow's prayer times in dict format
    """
    juristic_method = 0
    if config_handler.get_setting(constants.CONFIG_USE_HANAFI_METHOD_KEY):
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
    self.alarm_popup_service = AlarmDismissPopup(audio_player)
    self.alarm_schedule = None
    self.alarm_reset_schedule = None

  def get_prayer_times(self):
    """
    Updates today's and tomorrow's prayer times
    :return: None
    """
    juristic_method = 0
    if config_handler.get_setting(constants.CONFIG_USE_HANAFI_METHOD_KEY):
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
    if config_handler.get_setting(constants.CONFIG_TAHAJJUD_ALARM_KEY):
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
    if self.alarm_schedule is not None:
      self.alarm_schedule.cancel()
    if self.alarm_reset_schedule is not None:
      self.alarm_reset_schedule.cancel()
    self.alarm_schedule = Clock.schedule_once(self.play_alarm,
                                              (time_of_alarm - datetime.datetime.now()).total_seconds())

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
      audio_player.play_alarm()


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
    self.alarm_popup_service = AlarmDismissPopup(audio_player)

    self.adhan_schedule = None
    self.adhan_reset_schedule = None
    self.alarm_schedule = None
    self.alarm_reset_schedule = None

  def schedule_adhan(self):
    """
    Schedules adhan to play at the specific prayer time
    :return: None
    """
    time_of_prayer = self.get_time_of_prayer(self.todays_times[self.prayer_time])
    if time_of_prayer < datetime.datetime.now():
      time_of_prayer = self.get_time_of_prayer(self.tomorrow_times[self.prayer_time]) + datetime.timedelta(days=1)

    if self.adhan_schedule is not None:
      self.adhan_schedule.cancel()
    if self.adhan_reset_schedule is not None:
      self.adhan_reset_schedule.cancel()
    self.adhan_schedule = Clock.schedule_once(self.play_adhan,
                                              (time_of_prayer - datetime.datetime.now()).total_seconds())
    self.adhan_reset_schedule = Clock.schedule_once(self.reset_adhan,
                                                    (time_of_prayer - datetime.datetime.now()).total_seconds() + 120)

    if self.prayer_time == 'Fajr':
      self.schedule_alarm_before_prayer()

  def schedule_alarm_before_prayer(self):
    """
    Schedules alarm 10 minutes before Fajr time
    :return: None
    """
    time_of_prayer = self.get_time_of_prayer(self.todays_times[self.prayer_time])
    if time_of_prayer < datetime.datetime.now():
      time_of_prayer = self.get_time_of_prayer(self.tomorrow_times[self.prayer_time]) + datetime.timedelta(days=1)

    if self.alarm_schedule is not None:
      self.alarm_schedule.cancel()
    if self.alarm_reset_schedule is not None:
      self.alarm_reset_schedule.cancel()
    self.alarm_schedule = Clock.schedule_once(self.play_alarm,
                                              (time_of_prayer - datetime.datetime.now()).total_seconds() - 600)

  def play_alarm(self, *args):
    """
    Plays alarm sound, and displays alarm popup
    :param args: Args given by Kivy
    :return: None
    """
    if not self.alarm_popup_service.is_open:
      self.alarm_popup_service.open()
      audio_player.play_alarm()

  def play_adhan(self, *args):
    """
    Plays adhan sound
    :param args: Args given by Kivy
    :return: None
    """
    if self.prayer_time == 'Fajr':
      fajr_adhan.play()
    else:
      adhan.play()

  def reset_adhan(self, *args):
    """
    Resets adhan sound to the 0th time
    :param args: Args given by Kivy
    :return: None
    """
    if self.prayer_time == 'Fajr':
      fajr_adhan.seek(0)
    else:
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
