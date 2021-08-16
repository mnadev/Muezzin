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


def read_from_config():
    """
    Reads the various setting parameters from a config file.
    :return: The following setting parameters: fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode
    """
    config_file = Path(FILE)
    if not config_file.exists():
        return False, False, False, False, False

    config = ConfigParser()
    config.read(FILE)

    enable_dark_mode = config.getboolean("THEME", "ENABLE_DARK_MODE")
    fajr_alarm = config.getboolean("ALARMS", "FAJR_ALARM")
    tahajjud_alarm = config.getboolean("ALARMS", "TAHAJJUD_ALARM")
    is_fahrenheit = config.getboolean("MISC", "USE_FAHRENHEIT")
    use_hanafi_method = config.getboolean("MISC", "USE_HANAFI_METHOD")

    return (
        fajr_alarm,
        tahajjud_alarm,
        is_fahrenheit,
        enable_dark_mode,
        use_hanafi_method,
    )


def write_to_config(
    fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode, use_hanafi_method
):
    """
    Write the various setting parameters to a config file to save setting state.
    :param fajr_alarm: Boolean controlling the fajr alarm
    :param tahajjud_alarm: Boolean controlling the tahajjud alarm
    :param is_fahrenheit: Boolean controlling fahrenheit/celcius
    :param enable_dark_mode: Boolean controlling dark mode
    :return: None
    """
    file = Path(FILE)
    file.touch(exist_ok=True)

    config = ConfigParser()
    config.add_section("THEME")
    config.add_section("ALARMS")
    config.add_section("MISC")
    config.set("THEME", "ENABLE_DARK_MODE", str(enable_dark_mode))
    config.set("ALARMS", "FAJR_ALARM", str(fajr_alarm))
    config.set("ALARMS", "TAHAJJUD_ALARM", str(tahajjud_alarm))
    config.set("MISC", "USE_FAHRENHEIT", str(is_fahrenheit))
    config.set("MISC", "USE_HANAFI_METHOD", str(use_hanafi_method))
    with open(file, "w+") as configfile:
        config.write(configfile)


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

    def get_setting(self, key):
        return self.settings[key]
