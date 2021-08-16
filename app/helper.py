import datetime


def celcius_to_fahrenheit(celsius):
    """
    Converts a temperature from celcius to fahrenheit
    :param celsius: The temperature in Celcius
    :return: The converted fahrenheit temperature
    """
    return round((celsius * 9 / 5) + 32, 2)


def get_tomorrow_date():
    """
    Creates and returns a datetime object representing tomorrow at midnight
    :return: A datetime object representing tomorrow at midnight
    """
    today = datetime.datetime.today()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    return today + datetime.timedelta(days=1)
