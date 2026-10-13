import os
import sys
import types
import random
import contextlib

# Shared bits for the test_*_screenshots.py files. The astronomy and text message
# views draw straight to the e-ink display, so they get a fake display that just
# keeps the image, and fake versions of the modules that need the Pi or the network.

repo_dir = os.path.dirname(os.path.abspath(__file__))

class FakeEPD:
   width = 800
   height = 480
   last_image = None

   def init(self):
      pass

   def Clear(self):
      pass

   def getbuffer(self, image):
      return image

   def display(self, image):
      FakeEPD.last_image = image

   def sleep(self):
      pass

def install_fake_module(name, **attributes):
   module = types.ModuleType(name)
   for key, value in attributes.items():
      setattr(module, key, value)
   sys.modules[name] = module
   return module

def install_fake_display():
   # fonts are loaded relative to the working directory
   os.chdir(repo_dir)
   install_fake_module('epd7in5_V2', EPD=FakeEPD)

def capture_display(display_func):
   # runs a view's display function and returns what it sent to the display (None if it never drew)
   FakeEPD.last_image = None
   random.seed(0) # keeps anything randomly placed (stars) the same between runs
   with open(os.devnull, 'w') as devnull, contextlib.redirect_stdout(devnull):
      display_func()
   return FakeEPD.last_image

def write_screenshots(view_name, scenarios, render):
   # scenarios is {name: data}, render(data) returns the image for that scenario
   output_dir = os.path.join(repo_dir, 'screenshots', view_name)
   os.makedirs(output_dir, exist_ok=True)
   failed = []
   for name, data in scenarios.items():
      path = os.path.join(output_dir, f'{name}.png')
      try:
         image = render(data)
         if image is None:
            raise Exception('nothing was sent to the display')
         image.save(path)
         print('wrote', os.path.relpath(path, repo_dir))
      except Exception as e:
         failed.append(name)
         print('FAILED', name, '-', repr(e))
   if failed:
      sys.exit(f'{len(failed)} scenario(s) failed: ' + ', '.join(failed))
