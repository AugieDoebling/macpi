from screenshot_helpers import install_fake_display, install_fake_module, capture_display, write_screenshots

# Renders the astronomy dashboard for a handful of fake scenarios and writes them to
# screenshots/astronomy/ so layout changes show up as image diffs.
#
#   python test_astronomy_screenshots.py
#
# No display, skyfield or network needed.

install_fake_display()
install_fake_module('planets', get_cloud_cover_for_tonight=None, get_viewing_infos=None)

import run_astronomy

# same priorities as planets.py
priorities = {
   'Venus': 0, 'Mars': 0, 'Saturn': 0, 'Jupiter': 0,
   'Mercury': 1, 'Moon': 1,
   'Neptune': 2, 'Uranus': 2,
}

def viewing(name, event_desc, event_time):
   # mirrors what planets.get_viewing_infos returns for a visible body
   arrow = '↗' if event_desc == 'Rising' else '↘'
   return {
      'body': {'name': name, 'priority': priorities[name]},
      'cycle': (None, None),
      'event': f'{event_desc} {event_time}',
      'event_time': event_time,
      'event_desc': event_desc,
      'short_event': f'{arrow} {event_time}',
   }

all_viewings = {
   'Venus': viewing('Venus', 'Setting', '20:36'),
   'Mars': viewing('Mars', 'Rising', '23:20'),
   'Saturn': viewing('Saturn', 'Setting', '5:52'),
   'Jupiter': viewing('Jupiter', 'Rising', '21:14'),
   'Mercury': viewing('Mercury', 'Setting', '19:58'),
   'Moon': viewing('Moon', 'Setting', '2:10'),
   'Neptune': viewing('Neptune', 'Setting', '5:30'),
   'Uranus': viewing('Uranus', 'Rising', '20:12'),
}

def scenario(bodies, cloud_cover=20):
   viewings = [all_viewings[name] for name in bodies]
   viewings.sort(key=lambda v: v['body']['priority'])
   return {'cloud_cover': cloud_cover, 'viewing_infos': viewings}

scenarios = {
   'typical_four_planets': scenario(['Venus', 'Mars', 'Saturn', 'Jupiter']),
   'saturn_and_moon': scenario(['Saturn', 'Moon']),
   'one_body': scenario(['Jupiter']),
   'mixed_priorities': scenario(['Venus', 'Saturn', 'Moon', 'Uranus']),
   'all_eight_bodies': scenario(list(all_viewings.keys())),
   'only_faint_planets': scenario(['Neptune', 'Uranus']),
   'nothing_visible': scenario([]),
   'clear_sky': scenario(['Mars', 'Saturn', 'Jupiter'], cloud_cover=0),
   'half_cloudy': scenario(['Mars', 'Saturn', 'Jupiter'], cloud_cover=50),
   'overcast': scenario(['Mars', 'Saturn', 'Jupiter'], cloud_cover=100),
}

def render(data):
   run_astronomy.get_cloud_cover_for_tonight = lambda: data['cloud_cover']
   run_astronomy.get_viewing_infos = lambda: data['viewing_infos']
   return capture_display(run_astronomy.display_astronomy)

if __name__ == "__main__":
   write_screenshots('astronomy', scenarios, render)
