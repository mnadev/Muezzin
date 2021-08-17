from constants import (
    CONFIG_ENABLE_DARK_MODE_KEY,
    DARK_THEME_TEXT_COLOR,
    LIGHT_THEME_TEXT_COLOR,
)
from kivy.uix.label import Label
from kivymd.uix.gridlayout import MDGridLayout
from moon_widget import MoonWidget
from weather_widget import WeatherWidget


class InformationScreen(MDGridLayout):
    """
    Defines a wrapper widget which holds a moon widget, and weather widget along with some display text
    """

    def __init__(self, config_handler, **kwargs):
        """
        Creates a InformationScreen.
        :param kwargs: Kwargs for MDGridLayout
        """
        super(InformationScreen, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 4

        self.config_handler = config_handler

        self.moon_widget = MoonWidget(config_handler)
        self.weather_widget = WeatherWidget(config_handler)
        self.add_widget(
            Label(
                text="Current moon phase",
                color=DARK_THEME_TEXT_COLOR
                if self.config_handler.get_setting(CONFIG_ENABLE_DARK_MODE_KEY)
                else LIGHT_THEME_TEXT_COLOR,
                font_name="RobotoMono-Regular",
                size_hint=(0.5, 0.5),
                font_size="25sp",
            )
        )
        self.add_widget(self.moon_widget)
        self.add_widget(
            Label(
                text="Current Weather",
                color=DARK_THEME_TEXT_COLOR
                if self.config_handler.get_setting(CONFIG_ENABLE_DARK_MODE_KEY)
                else LIGHT_THEME_TEXT_COLOR,
                font_name="RobotoMono-Regular",
                size_hint=(1, 0.5),
                font_size="25sp",
            )
        )
        self.add_widget(self.weather_widget)

    def update(self):
        """
        Updates MoonWidget and WeatherWidget
        :return: None
        """
        self.moon_widget.update()
        self.weather_widget.update()
