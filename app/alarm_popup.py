from constants import CONFIG_ENABLE_DARK_MODE_KEY
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout


class AlarmDismissPopup:
    """
    Creates a MDDialog to dismiss the alarm and holds logic to show dialog, dismiss dialog and shut off alarm.
    """

    def __init__(self, audio_player, config_handler):
        """
        Creates an AlarmDismissPopup
        """
        self.popup_layout = MDGridLayout(cols=1, padding=10)

        self.dismiss_button = MDRaisedButton(text="Dismiss")
        self.dismiss_button.bind(on_press=self.dismiss)

        dialog_text = "[color=000000]Dismiss Alarm[/color]"
        if config_handler.get_setting(CONFIG_ENABLE_DARK_MODE_KEY):
            "[color=ffffff]Dismiss Alarm[/color]"

        self.alarm_popup = MDDialog(
            title=dialog_text,
            size_hint=(0.75, 0.75),
            buttons=[self.dismiss_button],
        )
        self.alarm_popup.on_touch_up(self.dismiss)
        self.is_open = False

        self.audio_player = audio_player

    def dismiss(self, *args):
        """
        Dismisses the alarm popup and silences the alarm.
        :param args: Args sent by Kivy
        :return: None
        """
        self.alarm_popup.dismiss()
        self.is_open = False
        self.audio_player.stop_alarm()

    def open(self):
        """
        Opens the alarm dismissal popup
        :return: None
        """
        self.alarm_popup.open()
        self.is_open = True
