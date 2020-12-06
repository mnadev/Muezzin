from configparser import ConfigParser
from pathlib import Path

FILE_PATH = '~/muezzin/'
FILE = FILE_PATH + 'muezzin_config.ini'

Path(FILE_PATH).mkdir(parents=True, exist_ok=True)

def read_from_config():
  config_file = Path(FILE)
  if not config_file.exists():
    return False, False, False

  config = ConfigParser()
  config.read(FILE)

  fajr_alarm = config.getboolean('ALARMS', 'FAJR_ALARM')
  tahajjud_alarm = config.getboolean('ALARMS', 'TAHAJJUD_ALARM')
  is_fahrenheit = config.getboolean('MISC', 'USE_FAHRENHEIT')

  return fajr_alarm, tahajjud_alarm, is_fahrenheit


def write_to_config(fajr_alarm, tahajjud_alarm, is_fahrenheit):
  file = Path(FILE)
  file.touch(exist_ok=True)

  config = ConfigParser()
  config.add_section('ALARMS')
  config.add_section('MISC')
  config.set('ALARMS', 'FAJR_ALARM', str(fajr_alarm))
  config.set('ALARMS', 'TAHAJJUD_ALARM', str(tahajjud_alarm))
  config.set('MISC', 'USE_FAHRENHEIT', str(is_fahrenheit))
  with open(file, 'w+') as configfile:
    config.write(configfile)
