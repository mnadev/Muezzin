from kivy.clock import Clock
from kivy.core.audio import SoundLoader


class AudioPlayer:
    def __init__(self):
        self.adhan = SoundLoader.load("res/adhan.mp3")
        self.adhan.seek(0)

        self.fajr_adhan = SoundLoader.load("res/fajr_adhan.mp3")
        self.fajr_adhan.seek(0)

        self.alarm = SoundLoader.load("res/alarm.mp3")
        self.alarm.seek(0)

        self.reschedule_alarm_event = None

    def play_adhan(self):
        Clock.schedule_once(self.reset_adhan, 120)
        self.adhan.play()

    def reset_adhan(self, *args):
        self.adhan.seek(0)

    def play_fajr_adhan(self):
        Clock.schedule_once(self.reset_fajr_adhan, 220)
        self.fajr_adhan.play()

    def reset_fajr_adhan(self, *args):
        self.fajr_adhan.seek(0)

    def play_alarm(self):
        self.alarm.play()
        self.reschedule_alarm_event = Clock.schedule_once(self.reset_alarm, 17)

    def stop_alarm(self):
        self.reschedule_alarm_event.cancel()
        self.alarm.stop()
        self.alarm.seek(0)

    def reset_alarm(self, *args):
        self.alarm.seek(0)
        self.alarm.play()
        self.reschedule_alarm_event = Clock.schedule_once(self.reset_alarm, 17)
