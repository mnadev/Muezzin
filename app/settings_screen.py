import constants
from kivy.uix.label import Label
from kivymd.uix.gridlayout import MDGridLayout
from setting_switch_item import SettingSwitchItem


class SettingsScreen(MDGridLayout):
    """
    Holds the different setting objects
    """

    def __init__(self, config_handler, **kwargs):
        """
        Creates a SettingsScreen object
        :param kwargs: Arguments for MDGridLayout
        """
        super(SettingsScreen, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 6

        self.add_widget(
            Label(
                text="Settings",
                color=constants.DEFAULT_TEXT_COLOR,
                font_name="RobotoMono-Regular",
                size_hint=(1, 0.5),
                font_size="30sp",
            )
        )
        self.add_widget(
            SettingSwitchItem(
                "Set alarm for 10 minutes before Fajr",
                config_handler,
                constants.CONFIG_FAJR_ALARM_KEY,
            )
        )
        self.add_widget(
            SettingSwitchItem(
                "Set alarm for last third of night",
                config_handler,
                constants.CONFIG_TAHAJJUD_ALARM_KEY,
            )
        )
        self.add_widget(
            SettingSwitchItem(
                "Use Hanaji juristic method for Asr",
                config_handler,
                constants.CONFIG_USE_HANAFI_METHOD_KEY,
            )
        )
        self.add_widget(
            SettingSwitchItem(
                "Display temp in Fahrenheit (default: Celcius)",
                config_handler,
                constants.CONFIG_USE_FAHRENHEIT_KEY,
            )
        )
        self.add_widget(
            SettingSwitchItem(
                "Enable Sith/Dark Mode (default: Jedi/light mode)",
                config_handler,
                constants.CONFIG_ENABLE_DARK_MODE_KEY,
            )
        )
