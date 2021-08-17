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

moon_phase_images = {
    "full moon": "res/full_moon.png",
    "new moon": "res/new_moon.png",
    "first quarter": "res/first_quarter.png",
    "last quarter": "res/third_quarter.png",
    "new moon": "res/new_moon.png",
    "waxing gibbous": "res/waxing_gibbous.png",
    "waning gibbous": "res/waning_gibbous.png",
    "waxing crescent": "res/waxing_crescent.png",
    "waning crescent": "res/waning_crescent.png",
}


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
        self.image = Image(source=moon_phase_images[moon_phase.lower()])

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
        self.image.source = moon_phase_images[moon_phase.lower()]

        self.moon_schedule.cancel()
        self.moon_schedule = Clock.schedule_once(
            self.update, (get_tomorrow_date() - datetime.datetime.now()).seconds + 60
        )
