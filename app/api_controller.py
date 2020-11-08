import constants
import datetime
import requests

def get_hijri_date(time=None):
  if time is None:
    time = datetime.datetime.now()
  hijri_query = requests.get(constants.HIJRI_DATE_URL, params={"date": time.strftime("%m-%d-%Y")})
  if hijri_query.status_code != 200:
    return None
  return hijri_query.json()['data']['hijri']

