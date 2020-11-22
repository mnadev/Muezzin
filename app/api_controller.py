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


def get_location():
  location_response = requests.get(constants.GEOLOCATION_URL)
  if location_response.status_code != 200:
    return None
  return location_response.json()


def _get_prayer_times(country, zipcode, latitude, longitude, time_zone, time=arrow.now()):
  location = get_location()

  if latitude is None or longitude is None:
    latitude = location["latitude"]
    longitude = location["longitude"]

  if time_zone is None:
    time_zone = location["time_zone"]

  if zipcode is None:
    zipcode = location["zip_code"]

  if country is None:
    country = location["country_code"]

  params = {
    "latitude": latitude,
    "longitude": longitude,
    "time_zone": time_zone,
    "zipcode": zipcode,
    "country": country
  }

  prayer_times_response = requests.get(constants.PRAYER_TIMES_URL, params=params)
  if prayer_times_response.status_code != 200:
    return None
  return prayer_times_response.json()['results']


def get_prayer_times_day(country=None, zipcode=None, latitude=None, longitude=None, time_zone=None):
  return _get_prayer_times(country=country, zipcode=zipcode, latitude=latitude, longitude=longitude, )


def get_prayer_times_tomorrow(country=None, zipcode=None, latitude=None, longitude=None, time_zone=None):
  return _get_prayer_times(country=country, zipcode=zipcode, latitude=latitude, longitude=longitude,
                           time_zone=time_zone, time=arrow.now().shift(days=1))
