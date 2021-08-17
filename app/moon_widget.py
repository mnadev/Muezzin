import datetime

import api_controller as getter
from constants import (
    CONFIG_ENABLE_DARK_MODE_KEY,
    DARK_THEME_TEXT_COLOR,
    LIGHT_THEME_TEXT_COLOR,
)
from helper import get_tomorrow_date
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivymd.uix.gridlayout import MDGridLayout


class MoonWidget(MDGridLayout):
    """
    A widget that displays the current moon phase along with a picture. Updates moon phase daily.
    """

    def __init__(self, config_handler, **kwargs):
        """
        Creates a MoonWidget object
        :param kwargs: Kwargs for MDGridLayout
        """
        super(MoonWidget, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 2

        self.config_handler = config_handler

        moon_phase = self.update_moon_phase()
        self.size_hint = (0.8, 0.8)
        self.orientation = "horizontal"
        self.moon_text = Label(
            text=moon_phase,
            color=DARK_THEME_TEXT_COLOR
            if self.config_handler.get_setting(CONFIG_ENABLE_DARK_MODE_KEY)
            else LIGHT_THEME_TEXT_COLOR,
            font_name="RobotoMono-Regular",
            size_hint=(1, 1),
            font_size="15sp",
        )
        self.image = Image(source=self.get_moon_pic(moon_phase))

        self.add_widget(self.moon_text)
        self.add_widget(self.image)
        self.moon_schedule = Clock.schedule_once(
            self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds + 60
        )

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

        self.moon_schedule.cancel()
        self.moon_schedule = Clock.schedule_once(
            self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds + 60
        )

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
