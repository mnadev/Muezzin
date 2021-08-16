from kivy.uix.carousel import Carousel

from settings_screen import SettingsScreen
from screens import InformationScreen, MainScreen


class MuezzinCarousel(Carousel):
    """
    Defines a Carousel that swipes left/right and holds an InformationScreen, MainScreen and SettingsScreen.
    """

    def __init__(self, config_handler, **kwargs):
        """
        Creates a MuezzinCarousel.
        :param kwargs: Kwargs for MDGridLayout
        """
        super(MuezzinCarousel, self).__init__(**kwargs)
        self.information_screen = InformationScreen()
        self.main_screen = MainScreen()
        self.settings_screen = SettingsScreen(config_handler)

        self.add_widget(self.information_screen)
        self.add_widget(self.main_screen)
        self.add_widget(self.settings_screen)
        self.index = 1

    def on_index(self, *args):
        """
        Updates different widgets when the Carousel index changes to the corresponding respective widget
        :param args: Args given by kivy
        :return: None
        """
        if self.index == 1:
            self.main_screen.prayer_pane.update()
        if self.index == 0:
            self.information_screen.update()
        Carousel.on_index(self, *args)
