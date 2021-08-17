from kivy.clock import Clock
from kivy.uix.label import Label

from kivymd.uix.button import MDRectangleFlatIconButton
from kivymd.uix.gridlayout import MDGridLayout

import datetime

from calendar_box import CalendarBox
from constants import DEFAULT_CLOCK_COLOR


class TimePane(MDGridLayout):
    """
    Displays and updates the current clock time
    """

    def __init__(self, audio_player, config_handler, **kwargs):
        """
        Create a TimePane object
        :param kwargs: Kwargs for MDGridLayout
        """
        super(TimePane, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 3
        self.time_widget = Label(
            text=datetime.datetime.now().strftime("%I:%M %p"),
            color=DEFAULT_CLOCK_COLOR,
            font_name="RobotoMono-Regular",
            size_hint=(1, 0.5),
            font_size="50sp",
        )

        self.add_widget(CalendarBox(config_handler, size_hint=(1, 0.5)))
        self.add_widget(self.time_widget)

        Clock.schedule_once(self.update, 60 - datetime.datetime.now().second % 60)

        self.adhan_play_button = MDRectangleFlatIconButton(
            icon="play", text="Play adhan", text_color=DEFAULT_CLOCK_COLOR
        )
        self.adhan_play_button.bind(on_press=self.play_adhan)
        self.add_widget(self.adhan_play_button)

        self.audio_player = audio_player

    def update(self, *args):
        """
        Schedules the clock time to update every minute
        :param args: Args given by Kivy
        :return: None
        """
        self.time_widget.text = datetime.datetime.now().strftime("%I:%M %p")
        Clock.schedule_once(self.update, 60 - datetime.datetime.now().second % 60)

    def play_adhan(self, *args):
        """
        Plays adhan sound
        :param args: Args given by Kivy
        :return: None
        """
        self.audio_player.play_adhan()
