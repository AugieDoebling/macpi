import logging
# from lib/waveshare_epd import epd7in5_V2
import epd7in5_V2
from planets import now, get_viewing_infos, get_sunset, get_moon_phase_tonight, get_weather_today
from desktop import render_desktop


logging.basicConfig(level=logging.DEBUG)

def get_weather():
   try:
      return get_weather_today()
   except Exception:
      # still worth showing the sky if the forecast is down
      logging.exception('could not load weather')
      return {'high': None, 'low': None, 'rain': None}

def get_desktop_data():
   weather = get_weather()
   viewing_infos = get_viewing_infos()

   return {
      'date': now,
      'sunset': get_sunset(),
      'high': weather['high'],
      'low': weather['low'],
      'rain': weather['rain'],
      'moon_degrees': get_moon_phase_tonight(),
      'bodies': [
         {'name': vi['body']['name'], 'rise': vi['cycle'][0], 'set': vi['cycle'][1]}
         for vi in viewing_infos
      ]
   }

def display_desktop():
   data = get_desktop_data()
   logging.info(data)

   epd = epd7in5_V2.EPD()

   epd.init()
   epd.Clear()

   Himage = render_desktop(data)

   epd.display(epd.getbuffer(Himage))
   epd.sleep()


if __name__ == "__main__":
   display_desktop()
