from audio_player import AudioPlayer
from config_handler import ConfigHandler
from kivy.core.audio import SoundLoader
from kivymd.uix.gridlayout import MDGridLayout
from prayer_pane import PrayerPane
from time_pane import TimePane

default_text_color = [0.65, 0.7, 0.01, 1]
default_clock_color = [0, 0, 0, 1]

if True:
    default_text_color = [0.61, 0.81, 0.01, 0.76]
    default_clock_color = [1, 1, 1, 1]


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

        self.prayer_pane = PrayerPane(audio_player, config_handler, size_hint=(0.3, 1))
        self.add_widget(self.prayer_pane)
        self.prayer_pane.update()
