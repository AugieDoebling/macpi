import os
import datetime as dt
from desktop import render_desktop

# Renders the desktop dashboard for a handful of fake scenarios and writes them to
# screenshots/desktop/ so layout changes show up as image diffs.
#
#   python test_desktop_screenshots.py
#
# No display, skyfield or network needed.

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots', 'desktop')

today = dt.datetime(2026, 10, 12)

def at(hour, minute, day_offset=0):
   return today.replace(hour=hour, minute=minute) + dt.timedelta(days=day_offset)

all_bodies = {
   'Venus':   {'name': 'Venus',   'rise': at(8, 5),   'set': at(20, 36)},
   'Saturn':  {'name': 'Saturn',  'rise': at(17, 48), 'set': at(5, 52, 1)},
   'Mars':    {'name': 'Mars',    'rise': at(23, 20), 'set': at(13, 15, 1)},
   'Jupiter': {'name': 'Jupiter', 'rise': at(21, 14), 'set': at(11, 2, 1)},
   'Mercury': {'name': 'Mercury', 'rise': at(7, 41),  'set': at(19, 58)},
   'Moon':    {'name': 'Moon',    'rise': at(15, 41), 'set': at(2, 10, 1)},
   'Neptune': {'name': 'Neptune', 'rise': at(17, 35), 'set': at(5, 30, 1)},
   'Uranus':  {'name': 'Uranus',  'rise': at(20, 12), 'set': at(10, 5, 1)},
}

def scenario(bodies, **overrides):
   data = {
      'date': today,
      'sunset': at(18, 31),
      'high': 74,
      'tonight_low': 52,
      'rain': 10,
      'moon_degrees': 124, # waxing gibbous
      'bodies': [all_bodies[name] for name in bodies],
   }
   data.update(overrides)
   return data

scenarios = {
   'typical_five_planets': scenario(['Venus', 'Saturn', 'Mars', 'Jupiter', 'Uranus']),
   'saturn_and_moon': scenario(['Saturn', 'Moon']),
   'one_body': scenario(['Jupiter']),
   'three_bodies': scenario(['Venus', 'Mars', 'Moon'], moon_degrees=55),
   'four_bodies': scenario(['Venus', 'Saturn', 'Jupiter', 'Mercury']),
   'all_eight_bodies': scenario(list(all_bodies.keys())),
   'nothing_visible': scenario([]),
   'new_moon': scenario(['Saturn', 'Jupiter', 'Mars'], moon_degrees=2),
   'first_quarter': scenario(['Saturn', 'Moon'], moon_degrees=90),
   'full_moon_rainy': scenario(['Moon', 'Saturn'], moon_degrees=180, high=58, tonight_low=47, rain=100),
   'waning_crescent': scenario(['Saturn', 'Mars', 'Jupiter', 'Uranus'], moon_degrees=315),
   'heat_wave': scenario(['Venus', 'Saturn', 'Mars'], high=108, tonight_low=71, rain=0),
   'freezing': scenario(['Saturn', 'Jupiter'], high=28, tonight_low=-4, rain=35),
   'weather_unavailable': scenario(['Saturn', 'Moon'], high=None, tonight_low=None, rain=None),
   'long_date_late_sunset': scenario(['Venus', 'Mars'], date=dt.datetime(2026, 9, 30), sunset=dt.datetime(2026, 9, 30, 20, 22)),
}

def write_screenshots():
   os.makedirs(output_dir, exist_ok=True)
   for name, data in scenarios.items():
      path = os.path.join(output_dir, f'{name}.png')
      render_desktop(data).save(path)
      print('wrote', os.path.relpath(path))

if __name__ == "__main__":
   write_screenshots()
