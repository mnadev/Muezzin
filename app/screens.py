from kivy.core.audio import SoundLoader
from kivy.clock import Clock

from kivymd.uix.gridlayout import MDGridLayout

from alarm_popup import AlarmDismissPopup
import api_controller as getter
from audio_player import AudioPlayer
import concurrent.futures
from config_handler import ConfigHandler
import constants
import datetime
from helper import get_tomorrow_date
from prayer_time_layout import PrayerTimeLayout
from time_pane import TimePane

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

  def __init__(self, audio_player, config_handler, **kwargs):
    """
    Create a MainScreen object
    :param kwargs: Kwargs for MDGridLayout
    """
    super(MainScreen, self).__init__(**kwargs)
    self.cols = 2

    self.add_widget(TimePane(audio_player, config_handler))

    self.prayer_pane = PrayerPane(audio_player, size_hint=(0.3, 1))
    self.add_widget(self.prayer_pane)
    self.prayer_pane.update()


class PrayerPane(MDGridLayout):
  """
  Defines the pane holding the children PrayerTimeLayout widgets. Also defines logic for updating prayer times,
  and for scheduling a tahajjud alarm.
  """

  def __init__(self, audio_player, **kwargs):
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
      self.prayer_time_widgets[prayer_time] = PrayerTimeLayout(audio_player, prayer_time, self.todays_times,
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
