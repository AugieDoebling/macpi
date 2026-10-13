import os
import logging
# from lib/waveshare_epd import epd7in5_V2
import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont,ImageChops
from planets import get_cloud_cover_for_tonight, get_viewing_infos
import math
import random


logging.basicConfig(level=logging.DEBUG)

white = 255
grey = 128
black = 0

time_font_size = 48
time_desc_font_size = 30

fonts = {}

def load_fonts(font_sizes):
    for size in font_sizes:
        fonts[size] = ImageFont.truetype(os.path.join('fonts', 'default.ttc'), size)

def calc_row_heights(total_height, viewing_infos):
   min_row_height = 12

   priorities = [vi['body']['priority'] for vi in viewing_infos]
   # print(priorities)
   lowest_priority = max(priorities)
   # print('lowest_priority', lowest_priority)

   # lowest priority is 1*line
   # lowest + 1 priorities is 2*line, etc
   lines = sum([lowest_priority + 1 - p for p in priorities])

   line_height = max(total_height / lines, min_row_height)
   print('line height', line_height)

   # error correct if line_height < min_row_height
   additional_multiplier = 1
   while True:
      heights = [math.floor(line_height + (i * additional_multiplier * line_height)) for i in range(lowest_priority + 0, -1, -1)]

      current_height = sum([heights[p] for p in priorities])
      # print('heights', heights)
      # print(current_height, total_height)
      if current_height <= total_height:
         print('viewing box height', current_height)
         break
      additional_multiplier -= 0.1
      

      if (additional_multiplier <= 0):
         print(f'dropping priority {lowest_priority} objects')
         higher_priorities = calc_row_heights([vi for vi in viewing_infos if vi['body']['priority'] < lowest_priority])
         higher_priorities.append(0)
         return higher_priorities
    
   return heights

def draw_viewing(draw, viewing, rect_box, font_sizes):
   body_name = viewing["body"]["name"]
   body_priority = viewing["body"]["priority"]
   print(f'drawing {body_name} (pri. {body_priority}) at {rect_box}')
   print('cycle', viewing['cycle'])
   row_height = rect_box[3]-rect_box[1]
   # icon box
   # draw.rectangle((rect_box[0], rect_box[1]+1, row_height, rect_box[3]-1), fill=black)
   # icon
   # ADD

   # row_background = 

   # border
   draw.line((0, rect_box[1], rect_box[2], rect_box[1]), fill=black, width=1) # top
   draw.line((0, rect_box[3], rect_box[2], rect_box[3]), fill=black, width=1) # bottom
   # draw.line((rect_box[2], rect_box[1], rect_box[2], rect_box[3]), fill=black, width=1) # right

   # text
   # text_box = (row_height+10, rect_box[1], rect_box[2], rect_box[3])
   # print('text box', text_box)
   middle_y = rect_box[1] + math.floor(row_height / 2)


   print('font_sizes', font_sizes, fonts.keys())
   font_size = font_sizes[body_priority]
   # time_font_size = font_sizes[min(body_priority+1, len(font_sizes)-1)]
   print('font size', font_size)
   # left_middle = (row_height + 10, middle_y, row_height + 10, middle_y)
   # print('left_middle', left_middle)
   # draw.text(left_middle, viewing['event'], font=fonts[time_font_size], fill=black, anchor='lm')
   # right_middle = (rect_box[2], middle_y, rect_box[2], middle_y)
   # print('right_middle', right_middle)
   # draw.text(right_middle, body_name, font=fonts[font_size], fill=black, align='right', anchor='rm')

   left_side_text_box = (10, middle_y, 10, middle_y)
   print('left_side_text_box', left_side_text_box)
   draw.text(left_side_text_box, body_name, font=fonts[font_size], fill=black, align='left', anchor='lm')


   # right side event box
   event_box_width = 220
   print('event_box_width', event_box_width)
   event_box = (rect_box[2] - event_box_width, rect_box[1], rect_box[2], rect_box[3])
   print('event_box', event_box)
   draw.rectangle(event_box, fill=black)
   # event box border
   draw.line((rect_box[2] - event_box_width, rect_box[1], rect_box[2], rect_box[1]), width=1, fill=white)
   draw.line((rect_box[2] - event_box_width, rect_box[3], rect_box[2], rect_box[3]), width=1, fill=white)


   # event box text
   time_x = (event_box[2] + event_box[0]) / 2;
   time_y = (event_box[3] + event_box[1]) / 2;
   use_compact_time = row_height < time_font_size * 2
   print('time', time_x, time_y, time_font_size, font_size, use_compact_time)



   if use_compact_time:
      draw.text((time_x, time_y, time_x, time_y), viewing['short_event'], font=fonts[min(time_font_size, font_size)], fill=white, align='center', anchor='mm')
   else:
      event_desc_y = time_y - time_desc_font_size - 10 if viewing['event_desc'] == 'Rising' else time_y + time_desc_font_size + 10
      draw.text((time_x, time_y, time_x, time_y), viewing['event_time'], font=fonts[time_font_size], fill=white, align='center', anchor='mm')
      draw.text((time_x, event_desc_y, time_x, event_desc_y), viewing['event_desc'], font=fonts[time_desc_font_size], fill=white, align='center', anchor='mm')

def draw_star(draw, x, y):
   size = random.randint(2, 4)
   draw.line((x-size, y, x+size, y), fill=black, width=1) # horizontal
   draw.line((x, y-size, x, y+size), fill=black, width=1) # vertical


def display_astronomy():
   cloud_cover = get_cloud_cover_for_tonight()
   viewing_infos = get_viewing_infos()

   epd = epd7in5_V2.EPD()

   epd.init()
   epd.Clear()

   Himage = Image.new('1', (epd.width, epd.height), white)  # 255: clear the frame
   draw = ImageDraw.Draw(Himage)

   cloud_cover_height = 40
   cloud_cover_font_size = math.floor(cloud_cover_height * .8)

   viewings_height = epd.height - cloud_cover_height
   viewings_width = epd.width
   current_y = 0

   viewing_row_heights = calc_row_heights(viewings_height, viewing_infos)
   print('viewing row heights', viewing_row_heights)

   font_sizes = [math.floor(row_height * 0.7) for row_height in viewing_row_heights]
   font_sizes.append(cloud_cover_font_size)
   font_sizes.append(time_font_size)
   font_sizes.append(time_desc_font_size)
   load_fonts(font_sizes)


   # viewing = viewing_infos[0]
   for viewing in viewing_infos:
      row_height = viewing_row_heights[viewing['body']['priority']]
      # box is (left x, top y, right x, bottom y)
      draw_viewing(draw, viewing, (0, current_y, viewings_width, current_y + row_height), font_sizes)
      current_y += row_height



   cloud_cover_box = (math.floor(epd.width / 2), epd.height - math.floor(cloud_cover_height / 2), epd.width, epd.height)
   draw.text(cloud_cover_box, f'Cloud Cover {cloud_cover}%', font=fonts[cloud_cover_font_size], fill=black, align='center', anchor='mm')

   cloud_cover_image = Image.new('1', (epd.width, epd.height), white)  # 255: clear the frame
   cloud_cover_draw = ImageDraw.Draw(cloud_cover_image)

   print('cloud cover', cloud_cover)
   cloud_cover_clear_width = (100 - cloud_cover) * 0.01 * epd.width
   print('cloud_cover_clear_width', cloud_cover_clear_width)
   cloud_cover_dark_box = (cloud_cover_clear_width, epd.height - cloud_cover_height, epd.width, epd.height)
   print('cloud_cover_dark_box', cloud_cover_dark_box)
   cloud_cover_draw.rectangle(cloud_cover_dark_box, fill=black)
   Himage = ImageChops.logical_xor(Himage, cloud_cover_image)
   Himage = ImageChops.invert(Himage)
   draw = ImageDraw.Draw(Himage)


   star_x = random.randint(5, 15)
   while star_x < epd.width:
      if 275 < star_x and star_x < 525:
         star_x = 525
      star_y = random.randint(epd.height-cloud_cover_height, epd.height)
      draw_star(draw, star_x, star_y)
      star_x += random.randint(1, 10)








   
   # draw_viewings(draw, (0, 0, 800, 480))




   epd.display(epd.getbuffer(Himage))
   epd.sleep()









if __name__ == "__main__":
   display_astronomy()



