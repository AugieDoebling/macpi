#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
# picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
# libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
# if os.path.exists(libdir):
#     sys.path.append(libdir)

import logging
# from lib/waveshare_epd import epd7in5_V2
import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from datetime import datetime
from twilio_client import get_latest_message
from friends import get_friend_name

logging.basicConfig(level=logging.DEBUG)

white = 255
black = 0

font_sizes = [96, 64, 48, 24, 18]

fonts = {}
characters_per_line_for_font = {
    96 : 14,
    64 : 22,
    48 : 32,
    24 : 14,
    18 : 14,
}

def load_fonts():
    for size in font_sizes:
        fonts[size] = ImageFont.truetype(os.path.join('fonts', 'default.ttc'), size)

def break_message(message, font=0):
    font_size = font_sizes[font]
    max_length = characters_per_line_for_font[font_size]
    broken = ''
    lines = 0
    index = 0
    if ' ' not in message:
        return (message, font_size)
    while index < len(message) - max_length:
        next_index = message.rindex(' ', index, index+max_length)
        if index == next_index:
            next_index = message.index(' ', index+max_length)
        line = message[index:next_index].strip()
        broken += (line+'\n')
        lines += 1
        index = next_index
        if 3 < lines:
            return break_message(message, font+1)
    broken += message[index:]
    return (broken, font_size)

def update_message():
    try:
        is_new, message = get_latest_message()
        # if no new message, dont write display
        if not is_new:
            return

        body, body_font_size = break_message(message['body'])
        sender = get_friend_name(message['from'])

        logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        
        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        load_fonts()

        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)

        # main message
        draw.multiline_text((400, 230), body, font=fonts[body_font_size], fill=black, anchor='mm', align='center')

        # header - number to text
        draw.rectangle((150, 0, 650, 30), fill=black)
        draw.text((400, 15), 'Text Your Message to: (845) 613-4979', font=fonts[18], fill='white', anchor='mm')

        # footer
        draw.line((0, 430, 800, 430), fill=black, width=2)
        draw.line((400, 430, 400, 480), fill=black, width=2)
        # from
        draw.text((600, 455), 'From: '+sender, font=fonts[24], fill=black, anchor='mm')
        draw.text((200, 455), 'At: '+message['date_sent'], font=fonts[24], fill=black, anchor='mm')
        
        epd.display(epd.getbuffer(Himage))

        logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
   update_message()

