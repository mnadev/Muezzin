from kivy.clock import Clock

from kivymd.uix.gridlayout import MDGridLayout

from alarm_popup import AlarmDismissPopup
from constants import DEFAULT_TEXT_COLOR
import datetime
from wrapped_label import WrappedLabel

class PrayerTimeLayout(MDGridLayout):
  """
  Holds the UI logic, updating prayer time logic, adhan scheduling logic,
  and alarm scheduling logic (for Fajr) for a specific prayer time.
  """

  def __init__(self, audio_player, prayer_time, todays_times, tomorrow_times, **kwargs):
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
                                           color=DEFAULT_TEXT_COLOR, font_name="Roboto-BoldItalic",
                                           font_size="15sp")
    self.tomorrows_time_widget = WrappedLabel(text="Tomorrow: " + self.tomorrow_times[self.prayer_time],
                                              color=DEFAULT_TEXT_COLOR, font_name="Roboto-BoldItalic",
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
