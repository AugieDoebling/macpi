import datetime as dt
from skyfield import almanac
from skyfield.api import N, W, wgs84, load
from pytz import timezone
import requests
import json
import math
import re

ts = load.timescale()
eph = load('de421.bsp')
tz = timezone('US/Pacific')
slo = wgs84.latlon(35.297639 * N, 120.682344 * W)
observer = eph['earth'] + slo

now = dt.datetime.now(tz)
midnight_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
midnight_tomorrow = midnight_today + dt.timedelta(days=1)
start_time = ts.from_datetime(midnight_today)
end_time = ts.from_datetime(midnight_tomorrow)

f = almanac.dark_twilight_day(eph, slo)
times, events = almanac.find_discrete(start_time, end_time, f)
astronomical_twighlight_ends = times[7].astimezone(tz)

sleepy_time = now.replace(hour=23, minute=59, second=0, microsecond=0)


bodies = [
   {
      'name': 'Mercury',
      'key': 'Mercury BARYCENTER',
      'priority': 1,
      'statusFunc': None,
      'type': 'planet'
   },
   {
      'name': 'Venus',
      'key': 'Venus BARYCENTER',
      'priority': 0,
      'statusFunc': None,
      'type': 'planet'
   },
   {
      'name': 'Moon',
      'key': 'Moon',
      'priority': 1,
      'statusFunc': lambda: 'Phase: {:.1f} degrees'.format(almanac.moon_phase(eph, ts.from_datetime(now)).degrees),
      'type': 'planet'
   },
   {
      'name': 'Mars',
      'key': 'Mars BARYCENTER',
      'priority': 0,
      'statusFunc': None,
      'type': 'planet'
   },
   {
      'name': 'Saturn',
      'key': 'Saturn BARYCENTER',
      'priority': 0,
      'statusFunc': None,
      'type': 'planet'
   },
   {
      'name': 'Jupiter',
      'key': 'Jupiter BARYCENTER',
      'priority': 0,
      'statusFunc': None,
      'type': 'planet'
   },
   {
      'name': 'Neptune',
      'key': 'Neptune BARYCENTER',
      'priority': 2,
      'statusFunc': None,
      'type': 'planet'
   },
   {
      'name': 'Uranus',
      'key': 'Uranus BARYCENTER',
      'priority': 2,
      'statusFunc': None,
      'type': 'planet'
   }
]

def get_next_event(cycle, status_func):
   rising = cycle[0]
   setting = cycle[1]
   event = "Hard to say"
   time = ""
   riseset = ""
   short = ""

   if astronomical_twighlight_ends < rising:
      event = rising.strftime('Rising %-H:%M')
      time = rising.strftime('%-H:%M')
      riseset = 'Rising'
      short = rising.strftime('↗ %-H:%M')
   elif astronomical_twighlight_ends < setting:
      event = setting.strftime('Setting %-H:%M')
      time = setting.strftime('%-H:%M')
      riseset = 'Setting'
      short = setting.strftime('↘ %-H:%M')
   else:
      event = setting.strftime('Not out')
      riseset = 'Not out'
   
   if status_func is not None:
      event += (f' ({status_func()})')

   return (event, time, riseset, short)


def get_cycle_times(body_key):
   target = eph[body_key]

   rising = almanac.find_risings(observer, target, start_time, end_time)[0].astimezone(tz)[0]
   rising_plus_24hr = ts.from_datetime(rising + dt.timedelta(days=1))
   setting = almanac.find_settings(observer, target, ts.from_datetime(rising), rising_plus_24hr)[0].astimezone(tz)[0]

   return (rising, setting)

def moon_phase():
   phase = almanac.moon_phase(eph, ts.from_datetime(now))
   return 'Phase: {:.1f}°'.format(phase.degrees)

def is_visible_in_prime_window(cycle):
   # print(astronomical_twighlight_ends)
   # print(sleepy_time)
   # print(cycle[0] < sleepy_time, astronomical_twighlight_ends < cycle[1])
   return cycle[0] < sleepy_time and astronomical_twighlight_ends < cycle[1]


def get_viewing_infos():
   viewing_infos = []
   bodies.sort(key=lambda b: b['priority'])
   for body in bodies:
      # print(body)
      cycle = get_cycle_times(body['key'])
      # print(cycle)
      event, event_time, event_desc, short_event = get_next_event(cycle, body['statusFunc'])
      # print(event)
      prime = is_visible_in_prime_window(cycle)
      # print(prime)
      view_info = {
         'body': body,
         'cycle': cycle,
         'event': event,
         'event_time': event_time,
         'event_desc': event_desc,
         'short_event': short_event,
         # 'prime': prime
      }
      # print(view_info)
      if prime:
         viewing_infos.append(view_info)

   return viewing_infos

def get_cloud_cover_for_tonight():
   weather_page = requests.get('https://api.weather.gov/gridpoints/LOX/77,115')
   weather_data = json.loads(weather_page.text)
   cloud_cover_data = weather_data['properties']['skyCover']['values']
   tonight_timestamp = midnight_tomorrow.strftime('%Y-%m-%dT00:00:00+00:00')

   tonight_forcast = next(forcast for forcast in cloud_cover_data if tonight_timestamp in forcast['validTime'])
   # print(tonight_forcast)
   return tonight_forcast['value']

   # print(cloud_cover_data)

def get_sunset():
   times, events = almanac.find_discrete(start_time, end_time, almanac.sunrise_sunset(eph, slo))
   # event is 1 for sunrise, 0 for sunset
   sunsets = [time for time, event in zip(times, events) if event == 0]
   if len(sunsets) == 0:
      return None
   return sunsets[0].astimezone(tz)

def get_moon_phase_tonight():
   # phase angle in degrees at 10pm today: 0 new, 90 first quarter, 180 full, 270 last quarter
   ten_pm = now.replace(hour=22, minute=0, second=0, microsecond=0)
   return almanac.moon_phase(eph, ts.from_datetime(ten_pm)).degrees

def parse_valid_time(valid_time):
   # weather.gov intervals look like '2026-10-12T15:00:00+00:00/PT13H' or '.../P6DT12H'
   start_text, duration_text = valid_time.split('/')
   start = dt.datetime.fromisoformat(start_text)
   match = re.fullmatch(r'P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?)?', duration_text)
   days, hours, minutes = [int(group or 0) for group in match.groups()]
   return (start, start + dt.timedelta(days=days, hours=hours, minutes=minutes))

def get_values_for_today(forecast_values):
   values = []
   for forecast in forecast_values:
      start, end = parse_valid_time(forecast['validTime'])
      if start < midnight_tomorrow and midnight_today < end and forecast['value'] is not None:
         values.append(forecast['value'])
   return values

def get_tonight_lows(min_temperature_values):
   # the overnight low is the forecast period that runs through midnight tonight (e.g. 8pm -> 10am)
   values = []
   for forecast in min_temperature_values:
      start, end = parse_valid_time(forecast['validTime'])
      if start <= midnight_tomorrow < end and forecast['value'] is not None:
         values.append(forecast['value'])
   return values

def celsius_to_fahrenheit(celsius):
   return celsius * 9 / 5 + 32

def get_weather_today():
   # high / tonight's low in fahrenheit and chance of rain in percent, None for anything missing from the forecast
   weather_page = requests.get('https://api.weather.gov/gridpoints/LOX/77,115')
   properties = json.loads(weather_page.text)['properties']

   highs = get_values_for_today(properties['maxTemperature']['values'])
   tonight_lows = get_tonight_lows(properties['minTemperature']['values'])
   rain_chances = get_values_for_today(properties['probabilityOfPrecipitation']['values'])

   return {
      'high': round(celsius_to_fahrenheit(max(highs))) if highs else None,
      'tonight_low': round(celsius_to_fahrenheit(tonight_lows[0])) if tonight_lows else None,
      'rain': round(max(rain_chances)) if rain_chances else None
   }

# get_cloud_cover_for_tonight()


# views = get_viewing_infos()

# print(views




# print(moon_phase())