import os
import math
from PIL import Image,ImageDraw,ImageFont

# Rendering for the "desktop" dashboard. Kept free of display / skyfield imports
# so it can be run off the Pi (see test_desktop_screenshots.py)

WIDTH = 800
HEIGHT = 480

white = 255
black = 0

menu_bar_height = 39
menu_bar_font_size = 26
title_bar_height = 24

fonts = {}

def get_font(size):
   size = int(size)
   if size not in fonts:
      font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'default.ttc')
      fonts[size] = ImageFont.truetype(font_path, size)
   return fonts[size]

def draw_text(draw, xy, text, size, anchor='la', bold=False):
   # the font only has a regular weight, so bold is faked with a 1px stroke
   draw.text(xy, text, font=get_font(size), fill=black, anchor=anchor, stroke_width=1 if bold else 0, stroke_fill=black)

def format_time(time):
   if time is None:
      return '--'
   return time.strftime('%I:%M %p').lstrip('0')

def format_value(value, suffix):
   if value is None:
      return '--'
   return f'{round(value)}{suffix}'

def moon_illumination(degrees):
   return (1 - math.cos(math.radians(degrees))) / 2

def moon_phase_name(degrees):
   degrees = degrees % 360
   if degrees < 6 or degrees >= 354:
      return 'New Moon'
   if degrees < 84:
      return 'Waxing Crescent'
   if degrees < 96:
      return 'First Quarter'
   if degrees < 174:
      return 'Waxing Gibbous'
   if degrees < 186:
      return 'Full Moon'
   if degrees < 264:
      return 'Waning Gibbous'
   if degrees < 276:
      return 'Last Quarter'
   return 'Waning Crescent'


# ---- icons ----

def draw_triangle(draw, x, y, size, up):
   if up:
      draw.polygon([(x - size, y + size), (x + size, y + size), (x, y - size)], fill=black)
   else:
      draw.polygon([(x - size, y - size), (x + size, y - size), (x, y + size)], fill=black)

def draw_moon(draw, x, y, radius, degrees):
   # degrees is the skyfield moon phase: 0 new, 90 first quarter, 180 full, 270 last quarter
   degrees = degrees % 360
   lit = moon_illumination(degrees)
   waxing = degrees < 180
   circle = (x - radius, y - radius, x + radius, y + radius)
   draw.ellipse(circle, fill=white)
   for dy in range(-radius, radius + 1):
      half_width = math.sqrt(radius * radius - dy * dy)
      terminator = (1 - 2 * lit) * half_width
      # northern hemisphere: waxing moon is lit on the right
      (dark_start, dark_end) = (-half_width, terminator) if waxing else (-terminator, half_width)
      if round(dark_end) > round(dark_start):
         draw.line((x + round(dark_start), y + dy, x + round(dark_end), y + dy), fill=black)
   draw.ellipse(circle, outline=black, width=2)

def draw_body_icon(draw, name, x, y, radius, moon_degrees):
   circle = (x - radius, y - radius, x + radius, y + radius)
   inner = math.floor(radius * 0.62)
   inner_circle = (x - inner, y - inner, x + inner, y + inner)
   ring = math.floor(radius / 3)
   if name == 'Moon':
      draw_moon(draw, x, y, radius, moon_degrees)
   elif name == 'Saturn':
      draw.ellipse((x - radius - 3, y - ring, x + radius + 3, y + ring), outline=black, width=2)
      draw.ellipse(inner_circle, fill=black)
   elif name == 'Uranus':
      draw.ellipse((x - ring, y - radius - 3, x + ring, y + radius + 3), outline=black, width=2)
      draw.ellipse(inner_circle, fill=white, outline=black, width=2)
   elif name == 'Jupiter':
      draw.ellipse(circle, outline=black, width=2)
      for dy in (-math.floor(radius / 3), math.floor(radius / 4)):
         half_width = math.floor(math.sqrt(radius * radius - dy * dy)) - 1
         draw.line((x - half_width, y + dy, x + half_width, y + dy), fill=black, width=2)
   elif name == 'Mars':
      draw.ellipse((x - radius + 3, y - radius + 3, x + radius - 3, y + radius - 3), fill=black)
   elif name == 'Venus':
      inset = max(3, math.floor(radius * 0.28))
      draw.ellipse(circle, outline=black, width=2)
      draw.ellipse((x - radius + inset, y - radius + inset, x + radius - inset, y + radius - inset), outline=black, width=1)
   elif name == 'Mercury':
      small = math.floor(radius * 0.5)
      draw.ellipse((x - small, y - small, x + small, y + small), fill=black)
   elif name == 'Neptune':
      draw.ellipse(circle, outline=black, width=2)
      for dy in range(-radius + 4, radius - 3, 4):
         half_width = math.floor(math.sqrt(radius * radius - dy * dy)) - 3
         draw.line((x - half_width, y + dy, x + half_width, y + dy), fill=black, width=1)
   else:
      draw.ellipse(circle, outline=black, width=2)

def draw_sunset_icon(draw, x, y, radius):
   draw.pieslice((x - radius, y - radius, x + radius, y + radius), 180, 360, fill=black)
   for angle in range(180, 361, 36):
      radians = math.radians(angle)
      draw.line((
         x + (radius + 4) * math.cos(radians), y + (radius + 4) * math.sin(radians),
         x + (radius + 10) * math.cos(radians), y + (radius + 10) * math.sin(radians)
      ), fill=black, width=2)
   draw.line((x - radius - 12, y + 2, x + radius + 12, y + 2), fill=black, width=2)
   draw.line((x - radius - 4, y + 8, x + radius + 4, y + 8), fill=black, width=2)

def draw_raindrop(draw, x, y, size):
   draw.polygon([(x, y - size), (x - size * 0.62, y + size * 0.25), (x + size * 0.62, y + size * 0.25)], fill=black)
   draw.ellipse((x - size * 0.65, y - size * 0.2, x + size * 0.65, y + size * 1.1), fill=black)


# ---- desktop pieces ----

def new_desktop_image():
   # 1px checkerboard, reads as grey on the e-ink display
   row_bytes = WIDTH // 8
   rows = [bytes([0xAA]) * row_bytes, bytes([0x55]) * row_bytes]
   return Image.frombytes('1', (WIDTH, HEIGHT), b''.join(rows[y % 2] for y in range(HEIGHT)))

def draw_menu_bar(draw, data):
   draw.rectangle((0, 0, WIDTH, menu_bar_height), fill=white)
   draw.line((0, menu_bar_height, WIDTH, menu_bar_height), fill=black, width=2)
   middle_y = menu_bar_height // 2

   date_text = '{} {}'.format(data['date'].strftime('%A, %B'), data['date'].day)
   draw_text(draw, (16, middle_y), date_text, menu_bar_font_size, anchor='lm', bold=True)

   sunset_text = 'Sunset {}'.format(format_time(data['sunset']))
   draw_text(draw, (WIDTH - 16, middle_y), sunset_text, menu_bar_font_size, anchor='rm')
   draw_sunset_icon(draw, WIDTH - 16 - draw.textlength(sunset_text, font=get_font(menu_bar_font_size)) - 34, middle_y + 2, 9)

def draw_window(draw, box, title):
   # box is (left x, top y, right x, bottom y), returns the y of the bottom of the title bar
   (left, top, right, bottom) = box
   draw.rectangle((left + 3, top + 3, right + 3, bottom + 3), fill=black) # drop shadow
   draw.rectangle(box, fill=white, outline=black, width=1)
   title_bottom = top + title_bar_height
   draw.line((left, title_bottom, right, title_bottom), fill=black)
   for y in range(top + 5, title_bottom - 3, 3):
      draw.line((left + 3, y, right - 3, y), fill=black)
   draw.rectangle((left + 10, top + 5, left + 24, top + 19), fill=white, outline=black) # close box

   middle_x = (left + right) // 2
   title_width = draw.textlength(title, font=get_font(17))
   draw.rectangle((middle_x - title_width / 2 - 10, top + 2, middle_x + title_width / 2 + 10, title_bottom - 2), fill=white)
   draw_text(draw, (middle_x, top + title_bar_height // 2), title, 17, anchor='mm', bold=True)
   return title_bottom

def draw_body_row_stacked(draw, body, box, moon_degrees):
   # tall rows: big name with the rise / set times underneath
   (left, top, right, bottom) = box
   row_height = bottom - top
   middle_y = (top + bottom) // 2
   icon_radius = math.floor(min(44, row_height * 0.28))
   name_size = min(54, row_height * 0.3)
   time_size = min(26, row_height * 0.17)
   arrow_size = math.floor(time_size * 0.3)

   draw_body_icon(draw, body['name'], left + 74, middle_y, icon_radius, moon_degrees)

   text_x = left + 154
   name_y = middle_y - math.floor(name_size * 0.5)
   time_y = middle_y + math.floor(name_size * 0.65)
   draw_text(draw, (text_x, name_y), body['name'], name_size, anchor='lm', bold=True)

   set_x = text_x + math.floor(time_size * 6.2)
   draw_triangle(draw, text_x + arrow_size, time_y + 2, arrow_size, up=True)
   draw_text(draw, (text_x + arrow_size * 2 + 10, time_y), format_time(body['rise']), time_size, anchor='lm')
   draw_triangle(draw, set_x + arrow_size, time_y + 2, arrow_size, up=False)
   draw_text(draw, (set_x + arrow_size * 2 + 10, time_y), format_time(body['set']), time_size, anchor='lm')

def draw_body_row_inline(draw, body, box, moon_degrees):
   # short rows: name and times on one line, under the RISES / SETS headers
   (left, top, right, bottom) = box
   row_height = bottom - top
   middle_y = (top + bottom) // 2
   icon_radius = math.floor(min(18, row_height * 0.26))
   name_size = min(30, row_height * 0.5)
   time_size = min(22, row_height * 0.42)

   draw_body_icon(draw, body['name'], left + 38, middle_y, icon_radius, moon_degrees)
   draw_text(draw, (left + 76, middle_y), body['name'], name_size, anchor='lm')
   draw_triangle(draw, right - 262, middle_y, 6, up=True)
   draw_text(draw, (right - 156, middle_y), format_time(body['rise']), time_size, anchor='rm')
   draw_triangle(draw, right - 128, middle_y, 6, up=False)
   draw_text(draw, (right - 20, middle_y), format_time(body['set']), time_size, anchor='rm')

def draw_bodies_window(draw, box, data):
   (left, top, right, bottom) = box
   content_top = draw_window(draw, box, 'Visible Tonight')
   bodies = data['bodies']
   moon_degrees = data['moon_degrees']

   if len(bodies) == 0:
      middle = ((left + right) // 2, (content_top + bottom) // 2)
      draw_text(draw, middle, 'Nothing out tonight', 30, anchor='mm')
      return

   stacked = (bottom - content_top) / len(bodies) >= 120
   if not stacked:
      header_height = 32
      draw_text(draw, (right - 156, content_top + 18), 'RISES', 14, anchor='rm')
      draw_text(draw, (right - 20, content_top + 18), 'SETS', 14, anchor='rm')
      content_top += header_height
      draw.line((left + 1, content_top, right - 1, content_top), fill=black)

   row_height = (bottom - content_top) / len(bodies)
   for index, body in enumerate(bodies):
      row_top = math.floor(content_top + row_height * index)
      row_bottom = math.floor(content_top + row_height * (index + 1))
      row_box = (left, row_top, right, row_bottom)
      if stacked:
         draw_body_row_stacked(draw, body, row_box, moon_degrees)
      else:
         draw_body_row_inline(draw, body, row_box, moon_degrees)

      if index < len(bodies) - 1:
         if stacked:
            draw.line((left + 1, row_bottom, right - 1, row_bottom), fill=black)
         else:
            for x in range(left + 12, right - 12, 4):
               draw.point((x, row_bottom), fill=black)

def draw_moon_window(draw, box, data):
   (left, top, right, bottom) = box
   content_top = draw_window(draw, box, 'Moon at 10 PM')
   degrees = data['moon_degrees']
   draw_moon(draw, left + 68, content_top + 84, 52, degrees)

   text_x = left + 200
   phase_words = moon_phase_name(degrees).split(' ')
   draw_text(draw, (text_x, content_top + 62), format_value(moon_illumination(degrees) * 100, '%'), 40, anchor='mm', bold=True)
   draw_text(draw, (text_x, content_top + 100), phase_words[0], 20, anchor='mm')
   draw_text(draw, (text_x, content_top + 124), phase_words[1], 20, anchor='mm')

def draw_weather_window(draw, box, data):
   (left, top, right, bottom) = box
   content_top = draw_window(draw, box, 'Today')
   high = format_value(data['high'], '°')
   tonight_low = format_value(data['tonight_low'], '°')
   # 3 digit / negative temps need a smaller font to fit side by side
   temp_size = 58 if max(len(high), len(tonight_low)) <= 3 else 44
   tonight_x = left + 148

   draw_text(draw, (left + 18, content_top + 26), 'HIGH', 14, anchor='lm')
   draw_text(draw, (tonight_x + 2, content_top + 26), 'TONIGHT', 14, anchor='lm')
   draw_text(draw, (left + 16, content_top + 72), high, temp_size, anchor='lm', bold=True)
   draw_text(draw, (tonight_x, content_top + 72), tonight_low, temp_size, anchor='lm')

   draw.line((left + 1, content_top + 116, right - 1, content_top + 116), fill=black)
   draw_raindrop(draw, left + 36, content_top + 144, 14)
   draw_text(draw, (left + 64, content_top + 148), '{} rain'.format(format_value(data['rain'], '%')), 30, anchor='lm')


def render_desktop(data):
   '''
   data = {
      'date': date or datetime,
      'sunset': datetime (or None),
      'high': degrees F, 'tonight_low': overnight low in degrees F, 'rain': percent (any can be None),
      'moon_degrees': skyfield moon phase angle at 10pm,
      'bodies': [{'name': 'Saturn', 'rise': datetime, 'set': datetime}, ...]
   }
   '''
   image = new_desktop_image()
   draw = ImageDraw.Draw(image)

   draw_menu_bar(draw, data)
   draw_bodies_window(draw, (16, 55, 492, 462), data)
   draw_moon_window(draw, (512, 55, 780, 236), data)
   draw_weather_window(draw, (512, 256, 780, 462), data)

   return image
