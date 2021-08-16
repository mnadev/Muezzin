from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

from kivymd.app import MDApp

from configparser import ConfigParser
from pathlib import Path
from sys import platform

import constants

FILE_PATH = ""
if platform == "linux" or platform == "linux2" or platform == "darwin":
    FILE_PATH = str(Path.home()) + "/muezzin/"
elif platform == "win32":
    FILE_PATH = "%PROGRAMDATA%\\muezzin\\config\\"

FILE = FILE_PATH + "muezzin_config.ini"

Path(FILE_PATH).mkdir(parents=True, exist_ok=True)


def close_app(*args):
    """
    Stops app
    :param args: Args given by Kivy
    :return: None
    """
    MDApp.get_running_app().stop()


class ConfigHandler:
    def __init__(self):
        """
        Reads the various setting parameters from a config file.
        """
        config_file = Path(FILE)

        self.settings = {}
        if not config_file.exists():
            self.settings[constants.CONFIG_ENABLE_DARK_MODE_KEY] = False
            self.settings[constants.CONFIG_FAJR_ALARM_KEY] = False
            self.settings[constants.CONFIG_TAHAJJUD_ALARM_KEY] = False
            self.settings[constants.CONFIG_USE_FAHRENHEIT_KEY] = False
            self.settings[constants.CONFIG_USE_HANAFI_METHOD_KEY] = False
        else:
            config = ConfigParser()
            config.read(FILE)

            self.settings[constants.CONFIG_ENABLE_DARK_MODE_KEY] = config.getboolean(
                constants.CONFIG_THEME_SECTION, constants.CONFIG_ENABLE_DARK_MODE_KEY
            )
            self.settings[constants.CONFIG_FAJR_ALARM_KEY] = config.getboolean(
                constants.CONFIG_ALARM_SECTION, constants.CONFIG_FAJR_ALARM_KEY
            )
            self.settings[constants.CONFIG_TAHAJJUD_ALARM_KEY] = config.getboolean(
                constants.CONFIG_ALARM_SECTION, constants.CONFIG_TAHAJJUD_ALARM_KEY
            )
            self.settings[constants.CONFIG_USE_FAHRENHEIT_KEY] = config.getboolean(
                constants.CONFIG_MISC_SECTION, constants.CONFIG_USE_FAHRENHEIT_KEY
            )
            self.settings[constants.CONFIG_USE_HANAFI_METHOD_KEY] = config.getboolean(
                constants.CONFIG_MISC_SECTION, constants.CONFIG_USE_HANAFI_METHOD_KEY
            )

    def write_to_config(self):
        """
        Write the various setting parameters to a config file to save setting state.
        :return: None
        """
        file = Path(FILE)
        file.touch(exist_ok=True)

        config = ConfigParser()
        config.add_section(constants.CONFIG_THEME_SECTION)
        config.add_section(constants.CONFIG_ALARM_SECTION)
        config.add_section(constants.CONFIG_MISC_SECTION)
        config.set(
            constants.CONFIG_THEME_SECTION,
            constants.CONFIG_ENABLE_DARK_MODE_KEY,
            str(self.enable_dark_mode),
        )
        config.set(
            constants.CONFIG_ALARM_SECTION,
            constants.CONFIG_FAJR_ALARM_KEY,
            str(self.set_fajr_alarm),
        )
        config.set(
            constants.CONFIG_ALARM_SECTION,
            constants.CONFIG_TAHAJJUD_ALARM_KEY,
            str(self.set_tahajjud_alarm),
        )
        config.set(
            constants.CONFIG_MISC_SECTION,
            constants.CONFIG_USE_FAHRENHEIT_KEY,
            str(self.use_fahrenheit),
        )
        config.set(
            constants.CONFIG_MISC_SECTION,
            constants.CONFIG_USE_HANAFI_METHOD_KEY,
            str(self.use_hanafi_method),
        )
        with open(file, "w+") as configfile:
            config.write(configfile)

    def update_settings(self, key, value):
        self.settings[key] = value

        if key == constants.CONFIG_ENABLE_DARK_MODE_KEY:
            exit_button = MDRaisedButton(text="Exit App")
            exit_button.bind(on_press=close_app)

            restart_popup = MDDialog(
                title="To update changes, you must restart app.",
                size_hint=(0.75, 0.75),
                buttons=[exit_button],
            )
            restart_popup.open()

    def get_setting(self, key):
        return self.settings[key]
