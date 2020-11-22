import constants
import arrow
import requests


def get_hijri_date(time=None):
  if time is None:
    time = arrow.now()
  hijri_query = requests.get(constants.HIJRI_DATE_URL, params={"month": time.date().strftime("%m"),
                                                               "day": time.date().strftime("%d"),
                                                               "year": time.date().strftime("%Y"),
                                                               "convert_to": 0})
  if hijri_query.status_code != 200:
    return None
  hijri_response = hijri_query.json()
  parsed_hijri_date = arrow.get(hijri_response['to'], hijri_response['format'])

  hijri_date = dict()
  hijri_date['month'] = constants.HIJRI_MONTH_STRING[parsed_hijri_date.month]
  hijri_date['day'] = parsed_hijri_date.day
  hijri_date['year'] = parsed_hijri_date.year

  return hijri_date

def get_gregorian_date():
  time = arrow.now()

  gregorian_date = dict()
  gregorian_date['month'] = time.date().strftime("%B")
  gregorian_date['day'] = time.day
  gregorian_date['year'] = time.year
  gregorian_date['weekday'] = time.date().strftime("%A")
  return gregorian_date
