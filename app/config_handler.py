from configparser import ConfigParser
from pathlib import Path

FILE_PATH = '~/muezzin/'
FILE = FILE_PATH + 'muezzin_config.ini'

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

  enable_dark_mode = config.getboolean('THEME', 'ENABLE_DARK_MODE')
  fajr_alarm = config.getboolean('ALARMS', 'FAJR_ALARM')
  tahajjud_alarm = config.getboolean('ALARMS', 'TAHAJJUD_ALARM')
  is_fahrenheit = config.getboolean('MISC', 'USE_FAHRENHEIT')
  use_hanafi_method = config.getboolean('MISC', 'USE_HANAFI_METHOD')

  return fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode, use_hanafi_method


def write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit, enable_dark_mode, use_hanafi_method):
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
  config.add_section('THEME')
  config.add_section('ALARMS')
  config.add_section('MISC')
  config.set('THEME', 'ENABLE_DARK_MODE', str(enable_dark_mode))
  config.set('ALARMS', 'FAJR_ALARM', str(fajr_alarm))
  config.set('ALARMS', 'TAHAJJUD_ALARM', str(tahajjud_alarm))
  config.set('MISC', 'USE_FAHRENHEIT', str(is_fahrenheit))
  config.set('MISC', 'USE_HANAFI_METHOD', str(use_hanafi_method))
  with open(file, 'w+') as configfile:
    config.write(configfile)
