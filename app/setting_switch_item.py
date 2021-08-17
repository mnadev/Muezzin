from constants import (
    CONFIG_ENABLE_DARK_MODE_KEY,
    DARK_THEME_TEXT_COLOR,
    LIGHT_THEME_TEXT_COLOR,
)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivymd.uix.selectioncontrol import MDSwitch


class SettingSwitchItem(AnchorLayout):
    """
    Holds a Label and MDSwitch which controls whether or not some setting is on.
    """

    def __init__(self, display_text, config_handler, setting_key, **kwargs):
        """
        Creates an SettingSwitchItem object
        :param kwargs: Arguments for Anchor Layout
        """
        super(SettingSwitchItem, self).__init__(**kwargs)

        self.config_handler = config_handler

        self.text_anchor_layout = AnchorLayout(anchor_x="left", anchor_y="top")
        self.text_anchor_layout.add_widget(
            Label(
                text=display_text,
                color=DARK_THEME_TEXT_COLOR
                if self.config_handler.get_setting(CONFIG_ENABLE_DARK_MODE_KEY)
                else LIGHT_THEME_TEXT_COLOR,
                font_name="RobotoMono-Regular",
                size_hint=(1, 0.5),
                font_size="10sp",
            )
        )

        self.setting_key = setting_key

        self.dark_mode_checkbox = MDSwitch(
            active=config_handler.get_setting(setting_key)
        )
        self.dark_mode_checkbox.bind(active=self.update_setting)
        self.dark_mode_checkbox_anchor_layout = AnchorLayout(
            anchor_x="center", anchor_y="bottom"
        )
        self.dark_mode_checkbox_anchor_layout.add_widget(self.dark_mode_checkbox)

        self.add_widget(self.text_anchor_layout)
        self.add_widget(self.dark_mode_checkbox_anchor_layout)

    def update_setting(self, checkbox, value):
        self.config_handler.update_settings(self.setting_key, value)
