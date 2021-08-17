import kivy

kivy.require("2.0.0")

from kivy.config import Config

Config.set("graphics", "width", "480")
Config.set("graphics", "height", "320")

from kivymd.app import MDApp

from audio_player import AudioPlayer
from config_handler import ConfigHandler
from constants import CONFIG_ENABLE_DARK_MODE_KEY
from muezzin_carousel import MuezzinCarousel

audio_player = AudioPlayer()
config_handler = ConfigHandler()
enable_dark_mode = config_handler.get_setting(CONFIG_ENABLE_DARK_MODE_KEY)


class MuezzinApp(MDApp):
    """
    Main app for Muezzing
    """

    def build(self):
        """
        Sets the icon and theme parameters of Kivy, and returns an instance of the MuezzinCarousel
        :return: an instance of MuezzinCarousel
        """
        self.icon = "res/mosque_green.png"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "600"
        if enable_dark_mode:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"
        return MuezzinCarousel(audio_player, config_handler, direction="right")


if __name__ == "__main__":
    MuezzinApp().run()
