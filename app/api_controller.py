import arrow
import constants
from io import BytesIO
import re
import requests
import time


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
  gregorian_date["formatted_string"] = gregorian_date['weekday'] + ", " + gregorian_date['month'] + " " + \
                                       str(gregorian_date['day']) + ", " + str(gregorian_date['year'])
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
    "country": country,
    "date": time.strftime("%Y-%m-%d")
  }

  prayer_times_response = requests.get(constants.PRAYER_TIMES_URL, params=params)
  if prayer_times_response.status_code != 200:
    return None
  results = prayer_times_response.json()['results']
  for prayer_time in results:
    results[prayer_time] = re.sub('%', '', results[prayer_time])

  return results


def get_prayer_times_today(country=None, zipcode=None, latitude=None, longitude=None, time_zone=None):
  return _get_prayer_times(country=country, zipcode=zipcode, latitude=latitude, longitude=longitude,
                           time_zone=time_zone)


def get_prayer_times_tomorrow(country=None, zipcode=None, latitude=None, longitude=None, time_zone=None):
  return _get_prayer_times(country=country, zipcode=zipcode, latitude=latitude, longitude=longitude,
                           time_zone=time_zone, time=arrow.now().shift(days=1))


def get_weather_image(weather_abbrv):
  image_request = requests.get(constants.WEATHER_API_ICONS_BASE_URL + weather_abbrv + ".png")
  return BytesIO(image_request.content)


def get_weather_location_woeid():
  location = get_location()
  latitude = location["latitude"]
  longitude = location["longitude"]
  params = {"lattlong": str(latitude) + "," + str(longitude)}
  location_request = requests.get(constants.WEATHER_API_LOCATION_SEARCH_URL, params=params)
  return location_request.json()[0]['woeid']


def get_weather(woeid):
  weather_request = requests.get(constants.WEATHER_API_URL + str(woeid))
  return weather_request.json()["consolidated_weather"][4]


def get_moon_phase():
  time = arrow.now()
  params = {
    "lang": "en",
    "month": time.strftime("%m"),
    "year": time.strftime("%Y"),
    "size": 100,
    "lightColor": "rgb(245, 245, 245)",
    "shadeColor": "rgb(17, 17, 17)",
    "LDZ": time.time()
  }
  moon_phase_request = requests.get(constants.MOON_API_URL, params=params)
  return moon_phase_request.json()
