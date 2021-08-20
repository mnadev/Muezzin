import re
from io import BytesIO

import arrow
import constants
import requests
from moon_phase_calculator import phase, position


def get_hijri_date(is_tomorrow):
    """
    Gets the hijri date
    :param is_tomorrow: A boolean stating if it's after maghrib, and we want to update the hijri date to the next day.
    :return: Information about the hijri date in a dict format.
    """
    time = arrow.now()
    if is_tomorrow:
        time = arrow.now().shift(days=1)
    hijri_query = requests.get(
        constants.HIJRI_DATE_URL,
        params={
            "month": time.date().strftime("%m"),
            "day": time.date().strftime("%d"),
            "year": time.date().strftime("%Y"),
            "convert_to": 0,
        },
    )
    if hijri_query.status_code != 200:
        return None
    hijri_response = hijri_query.json()
    parsed_hijri_date = arrow.get(hijri_response["to"], hijri_response["format"])

    hijri_date = dict()
    hijri_date["month"] = constants.HIJRI_MONTH_STRING[parsed_hijri_date.month]
    hijri_date["day"] = parsed_hijri_date.day
    hijri_date["year"] = parsed_hijri_date.year

    return hijri_date


def get_gregorian_date():
    """
    Gets today's gregorian date
    :return: Information about the current gregorian date in a dict format.
    """
    time = arrow.now()

    gregorian_date = dict()
    gregorian_date["month"] = time.date().strftime("%B")
    gregorian_date["day"] = time.day
    gregorian_date["year"] = time.year
    gregorian_date["weekday"] = time.date().strftime("%A")
    gregorian_date["formatted_string"] = (
        gregorian_date["weekday"]
        + ", "
        + gregorian_date["month"]
        + " "
        + str(gregorian_date["day"])
        + ", "
        + str(gregorian_date["year"])
    )
    return gregorian_date


def get_location():
    """
    Gets the location using a Geolocation API.
    :return: The location response
    """
    location_response = requests.get(constants.GEOLOCATION_URL)
    if location_response.status_code != 200:
        return None
    return location_response.json()


def _get_prayer_times(
    juristic_method, country, zipcode, latitude, longitude, time_zone, time=arrow.now()
):
    """
    Gets prayer times for the defined parameters, including the defined time
    :param juristic_method: The juristic method to calculate asr times (0 shafi/hanbali/maliki, 1 for hanafi)
    :param country: The country where you want prayer times
    :param zipcode: The zipcode where you want prayer times
    :param latitude: The latitude where you want prayer times
    :param longitude: The longitude where you want prayer times
    :param time_zone: The time zone where you want prayer times
    :return: Prayer times in dict format
    """
    print(time)
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
        "date": time.strftime("%Y-%m-%d"),
        "juristic": juristic_method,
    }

    prayer_times_response = requests.get(constants.PRAYER_TIMES_URL, params=params)
    if prayer_times_response.status_code != 200:
        return None
    results = prayer_times_response.json()["results"]
    for prayer_time in results:
        results[prayer_time] = re.sub("%", "", results[prayer_time])
    print("Results: ")
    print(results)
    return results


def get_prayer_times_today(
    juristic_method=0,
    country=None,
    zipcode=None,
    latitude=None,
    longitude=None,
    time_zone=None,
):
    """
    Gets prayer times for today for the given parameters.
    :param juristic_method: The juristic method to calculate asr times (0 shafi/hanbali/maliki, 1 for hanafi)
    :param country: The country where you want prayer times
    :param zipcode: The zipcode where you want prayer times
    :param latitude: The latitude where you want prayer times
    :param longitude: The longitude where you want prayer times
    :param time_zone: The time zone where you want prayer times
    :return: Today's prayer times in dict format
    """
    print("Getting today's times")
    return _get_prayer_times(
        juristic_method,
        country=country,
        zipcode=zipcode,
        latitude=latitude,
        longitude=longitude,
        time_zone=time_zone,
    )


def get_prayer_times_tomorrow(
    juristic_method=0,
    country=None,
    zipcode=None,
    latitude=None,
    longitude=None,
    time_zone=None,
):
    """
    Gets prayer times for tomorrow for the given parameters.
    :param juristic_method: The juristic method to calculate asr times (0 shafi/hanbali/maliki, 1 for hanafi)
    :param country: The country where you want prayer times
    :param zipcode: The zipcode where you want prayer times
    :param latitude: The latitude where you want prayer times
    :param longitude: The longitude where you want prayer times
    :param time_zone: The time zone where you want prayer times
    :return: Tomorrow's prayer times in dict format
    """
    print("Getting tomorrows's times")
    return _get_prayer_times(
        juristic_method,
        country=country,
        zipcode=zipcode,
        latitude=latitude,
        longitude=longitude,
        time_zone=time_zone,
        time=arrow.now().shift(days=1),
    )


def get_weather_image(weather_abbrv):
    """
    Gets an image of the current weather condition from the API
    :param weather_abbrv: An abbreviation of the current weather condition, as defined by the weather API
    :return: The image bytes of the weather icon
    """
    image_request = requests.get(
        constants.WEATHER_API_ICONS_BASE_URL + weather_abbrv + ".png"
    )
    return BytesIO(image_request.content)


def get_weather_location_woeid():
    """
    Gets woeid (ID) for a certain location after giving the latitude and longitude
    :return: The response from the weather API giving the woeid
    """
    location = get_location()
    latitude = location["latitude"]
    longitude = location["longitude"]
    params = {"lattlong": str(latitude) + "," + str(longitude)}
    location_request = requests.get(
        constants.WEATHER_API_LOCATION_SEARCH_URL, params=params
    )
    return location_request.json()[0]["woeid"]


def get_weather(woeid):
    """
    Gets weather for a certain location represented by the woeid
    :param woeid: The id representing the location
    :return: The response from the weather API
    """
    weather_request = requests.get(constants.WEATHER_API_URL + str(woeid))
    return weather_request.json()["consolidated_weather"][4]


def get_moon_phase():
    """
    Calculate today's moon phase
    :return: The current moon phase
    """
    return phase(position())
