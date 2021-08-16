from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import CoreImage, Image
from kivy.uix.label import Label

from kivymd.uix.gridlayout import MDGridLayout

import api_controller as getter
import concurrent.futures
from constants import DEFAULT_TEXT_COLOR, CONFIG_USE_FAHRENHEIT_KEY
import datetime
from helper import celcius_to_fahrenheit


class WeatherWidget(MDGridLayout):
    """
    Defines a Widget which displays the current weather condition, current temp, high temp, low temp and
    corresponding image of current weather.
    """

    def __init__(self, config_handler, **kwargs):
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
        self.config_handler = config_handler

        self.weather_text = Label(
            text=self.weather["weather_state_name"],
            color=DEFAULT_TEXT_COLOR,
            font_name="RobotoMono-Regular",
            size_hint=(1, 1),
            font_size="15sp",
        )
        self.current_text = Label(
            color=DEFAULT_TEXT_COLOR,
            font_name="RobotoMono-Regular",
            size_hint=(1, 1),
            font_size="15sp",
        )
        self.low_text = Label(
            color=DEFAULT_TEXT_COLOR,
            font_name="RobotoMono-Regular",
            size_hint=(1, 1),
            font_size="10sp",
        )
        self.high_text = Label(
            color=DEFAULT_TEXT_COLOR,
            font_name="RobotoMono-Regular",
            size_hint=(1, 1),
            font_size="10sp",
        )
        if self.config_handler.get_setting(CONFIG_USE_FAHRENHEIT_KEY):
            self.current_text.text = (
                "Current: "
                + ("%.2f" % celcius_to_fahrenheit(self.weather["the_temp"]))
                + " °F"
            )
            self.low_text.text = (
                "High: "
                + ("%.2f" % celcius_to_fahrenheit(self.weather["max_temp"]))
                + " °F"
            )
            self.high_text.text = (
                "Low: "
                + ("%.2f" % celcius_to_fahrenheit(self.weather["min_temp"]))
                + " °F"
            )
        else:
            self.current_text.text = (
                "Current: " + ("%.2f" % self.weather["the_temp"]) + " °C"
            )
            self.low_text.text = "High: " + ("%.2f" % self.weather["max_temp"]) + " °C"
            self.high_text.text = "Low: " + ("%.2f" % self.weather["min_temp"]) + " °C"

        self.image = Image()
        self.image.texture = CoreImage(
            self.update_weather_image(self.weather["weather_state_abbr"]), ext="png"
        ).texture

        self.weather_text_anchor_layout = AnchorLayout(anchor_x="left", anchor_y="top")
        self.current_text_anchor_layout = AnchorLayout(anchor_x="right", anchor_y="top")
        self.low_text_anchor_layout = AnchorLayout(anchor_x="right", anchor_y="bottom")
        self.high_text_anchor_layout = AnchorLayout(anchor_x="right", anchor_y="center")
        self.image_anchor_layout = AnchorLayout(anchor_x="left", anchor_y="bottom")

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
        future = concurrent.futures.ThreadPoolExecutor().submit(
            getter.get_weather_image, weather_state_abbr
        )
        image = future.result()
        return image

    def update_weather_location_woeid(self):
        """
        Updates woeid, which is the location ID for getting weather from the metaweather API.
        :return: None
        """
        future = concurrent.futures.ThreadPoolExecutor().submit(
            getter.get_weather_location_woeid
        )
        self.woeid = future.result()

    def update_weather(self):
        """
        Calls API to get weather results from
        :return: Results from weather API call
        """
        future = concurrent.futures.ThreadPoolExecutor().submit(
            getter.get_weather, self.woeid
        )
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

            self.image.texture = CoreImage(
                self.update_weather_image(self.weather["weather_state_abbr"]), ext="png"
            ).texture
            self.last_update_time = datetime.datetime.now()

        if self.config_handler.get_setting(CONFIG_USE_FAHRENHEIT_KEY):
            self.current_text.text = (
                "Current: "
                + ("%.2f" % celcius_to_fahrenheit(self.weather["the_temp"]))
                + " °F"
            )
            self.low_text.text = (
                "High: "
                + ("%.2f" % celcius_to_fahrenheit(self.weather["max_temp"]))
                + " °F"
            )
            self.high_text.text = (
                "Low: "
                + ("%.2f" % celcius_to_fahrenheit(self.weather["min_temp"]))
                + " °F"
            )
        else:
            self.current_text.text = (
                "Current: " + ("%.2f" % self.weather["the_temp"]) + " °C"
            )
            self.low_text.text = "High: " + ("%.2f" % self.weather["max_temp"]) + " °C"
            self.high_text.text = "Low: " + ("%.2f" % self.weather["min_temp"]) + " °C"
