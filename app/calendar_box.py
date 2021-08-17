from kivy.clock import Clock
from kivy.uix.image import Image

from kivymd.uix.gridlayout import MDGridLayout

import api_controller as getter
import concurrent.futures
from constants import (
    DEFAULT_TEXT_COLOR,
    CONFIG_ENABLE_DARK_MODE_KEY,
    CONFIG_USE_HANAFI_METHOD_KEY,
)
import datetime
from helper import get_tomorrow_date
from wrapped_label import WrappedLabel


class CalendarBox(MDGridLayout):
    """
    Holds Labels for displaying hijri and gregorian date, and
    holds logic for updating these dates, at their respective times of change.
    """

    def __init__(self, config_handler, **kwargs):
        """
        Create a CalendarBox object
        :param kwargs: Kwargs for MDGridLayout
        """
        super(CalendarBox, self).__init__(**kwargs)
        self.cols = 3
        self.rows = 1

        self.config_handler = config_handler

        gregorian_date = getter.get_gregorian_date()
        self.gregorian_widget = WrappedLabel(
            text=gregorian_date["formatted_string"],
            color=DEFAULT_TEXT_COLOR,
            font_name="Roboto-Bold",
            font_size="16sp",
            size_hint=(0.5, 1),
            padding=("10sp", "0sp"),
        )

        self.hijri_widget = WrappedLabel(
            text="14 Ramadan 1440 AH",
            color=DEFAULT_TEXT_COLOR,
            font_name="Roboto-Bold",
            font_size="16sp",
            size_hint=(0.5, 1),
            padding=("10sp", "0sp"),
        )
        self.update_hijri()
        # Logo courtesy of flaticon
        if self.config_handler.get_setting(CONFIG_ENABLE_DARK_MODE_KEY):
            self.add_widget(
                Image(
                    source="res/mosque_white.png",
                    keep_ratio=True,
                    size_hint_x=0.1,
                    pos=(0, 0),
                )
            )
        else:
            self.add_widget(
                Image(
                    source="res/mosque_dark.png",
                    keep_ratio=True,
                    size_hint_x=0.1,
                    pos=(0, 0),
                )
            )
        self.add_widget(self.gregorian_widget)
        self.add_widget(self.hijri_widget)

        Clock.schedule_once(
            self.update_gregorian,
            (get_tomorrow_date() - datetime.datetime.now()).seconds,
        )

    def update_gregorian(self, *args):
        """
        Schedules a Clock schedule to update Gregorian date at midnight.
        :param args: Args given by Kivy
        :return: None
        """
        gregorian_date = getter.get_gregorian_date()
        self.gregorian_widget.text = gregorian_date["formatted_string"]

        Clock.schedule_once(
            self.update_gregorian,
            (get_tomorrow_date() - datetime.datetime.now()).seconds,
        )

    def update_hijri(self, *args):
        """
        Schedules a Clock schedule to update Hijri date at maghrib time.
        :param args: Args given by Kivy
        :return: None
        """
        is_after_maghrib = self.check_before_after_maghrib()
        self.update_hijri_date(is_after_maghrib)
        if is_after_maghrib:
            Clock.schedule_once(
                self.update_hijri,
                (
                    self.get_time_of_prayer(
                        self.get_prayer_times_tomorrow()["Maghrib"], shift_tomorrow=True
                    )
                    - datetime.datetime.now()
                ).seconds,
            )
        else:
            Clock.schedule_once(
                self.update_hijri,
                (
                    self.get_time_of_prayer(self.get_prayer_times()["Maghrib"])
                    - datetime.datetime.now()
                ).seconds,
            )

    def get_time_of_prayer(self, time_string, shift_tomorrow=False):
        """
        Takes a clock time string and returns a datetime object of today with that time string
        :param time_string: A string of format "xx:xx pm/am" showing a certain clock time
        :param shift_tomorrow: A boolean that states whether to shift to the next Islamic day, if it's after maghrib
        :return: A datetime object with today's date, and the clock time corresponding to the time string
        """

        adhan_time = datetime.datetime.strptime(time_string, "%I:%M %p")
        today = datetime.datetime.today()
        today = today.replace(
            hour=adhan_time.hour, minute=adhan_time.minute, second=0, microsecond=0
        )
        if shift_tomorrow:
            today = today + datetime.timedelta(days=1)
        return today

    def update_hijri_date(self, is_tomorrow):
        """
        Updates the hijri date label
        :param is_tomorrow: A boolean that states whether it's after maghrib, i.e. is it the next Islamic day
        :return: None
        """
        future = concurrent.futures.ThreadPoolExecutor().submit(
            getter.get_hijri_date, is_tomorrow
        )
        hijri_date = future.result()
        self.hijri_widget.text = (
            str(hijri_date["day"])
            + " "
            + hijri_date["month"]
            + " "
            + str(hijri_date["year"])
            + " AH"
        )

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
        if self.config_handler.get_setting(CONFIG_USE_HANAFI_METHOD_KEY):
            juristic_method = 1
        todays_times_future = concurrent.futures.ThreadPoolExecutor().submit(
            getter.get_prayer_times_today, juristic_method
        )
        return todays_times_future.result()

    def get_prayer_times_tomorrow(self):
        """
        Obtains tomorrow's prayer times from API
        :return: Returns tomorrow's prayer times in dict format
        """
        juristic_method = 0
        if self.config_handler.get_setting(CONFIG_USE_HANAFI_METHOD_KEY):
            juristic_method = 1
        tomorrow_times_future = concurrent.futures.ThreadPoolExecutor().submit(
            getter.get_prayer_times_tomorrow, juristic_method
        )
        return tomorrow_times_future.result()
