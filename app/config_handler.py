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
        if not config_file.exists():
            self.enable_dark_mode = False
            self.set_fajr_alarm = False
            self.set_tahajjud_alarm = False
            self.use_fahrenheit = False
            self.use_hanafi_method = False
        else:
            config = ConfigParser()
            config.read(FILE)

            self.enable_dark_mode = config.getboolean(
                constants.CONFIG_THEME_SECTION, "ENABLE_DARK_MODE"
            )
            self.set_fajr_alarm = config.getboolean(
                constants.CONFIG_ALARM_SECTION, "FAJR_ALARM"
            )
            self.set_tahajjud_alarm = config.getboolean(
                constants.CONFIG_ALARM_SECTION, "TAHAJJUD_ALARM"
            )
            self.use_fahrenheit = config.getboolean(
                constants.CONFIG_MISC_SECTION, "USE_FAHRENHEIT"
            )
            self.use_hanafi_method = config.getboolean(
                constants.CONFIG_MISC_SECTION, "USE_HANAFI_METHOD"
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
            "ENABLE_DARK_MODE",
            str(self.enable_dark_mode),
        )
        config.set(
            constants.CONFIG_ALARM_SECTION, "FAJR_ALARM", str(self.set_fajr_alarm)
        )
        config.set(
            constants.CONFIG_ALARM_SECTION,
            "TAHAJJUD_ALARM",
            str(self.set_tahajjud_alarm),
        )
        config.set(
            constants.CONFIG_MISC_SECTION, "USE_FAHRENHEIT", str(self.use_fahrenheit)
        )
        config.set(
            constants.CONFIG_MISC_SECTION,
            "USE_HANAFI_METHOD",
            str(self.use_hanafi_method),
        )
        with open(file, "w+") as configfile:
            config.write(configfile)

    def set_enable_dark_mode(self, enable_dark_mode_):
        self.enable_dark_mode = enable_dark_mode_

    def set_set_fajr_alarm(self, set_fajr_alarm_):
        self.set_fajr_alarm = set_fajr_alarm_

    def set_set_tahajjud_alarm(self, set_tahajjud_alarm_):
        self.set_tahajjud_alarm = set_tahajjud_alarm_

    def set_use_fahrenheit(self, use_fahrenheit_):
        self.use_fahrenheit = use_fahrenheit_

    def set_use_hanafi_method(self, use_hanafi_method_):
        self.use_hanafi_method = use_hanafi_method_
