from screenshot_helpers import install_fake_display, install_fake_module, capture_display, write_screenshots

# Renders the text message view for a handful of fake messages and writes them to
# screenshots/macpi/ so layout changes show up as image diffs.
#
#   python test_macpi_screenshots.py
#
# No display, twilio or friends.py needed.

fake_friends = {
   '8055550101': 'Augie',
   '8055550102': 'Bartholomew',
}

def get_friend_name(number):
   # same formatting as friends.py, with made up numbers
   no_area_code = number.replace('+1', '')
   if no_area_code in fake_friends:
      return fake_friends[no_area_code]
   return '('+no_area_code[:3]+')'+no_area_code[3:6]+'-'+no_area_code[6:]

install_fake_display()
install_fake_module('twilio_client', get_latest_message=None)
install_fake_module('friends', get_friend_name=get_friend_name)

import run_macpi

def scenario(body, sender='+18055550101', date_sent='01/21 14:22'):
   return {'sid': 'SM123', 'body': body, 'from': sender, 'date_sent': date_sent}

scenarios = {
   'one_word': scenario('Hi'),
   'short': scenario('Enjoy your life'),
   'two_lines': scenario('does harold asdf sdkfa?'),
   'medium': scenario('Ok so what are we all doing for dinner tonight, tacos?'),
   'long': scenario('Please, Wallace...call me "Toddy" (a British slang term for an attractive, high society dame)'),
   'very_long': scenario('This is a much longer message than the display was really designed for, the kind of thing someone sends when they find out the number works and want to see how far it can be pushed before it breaks'),
   'no_spaces': scenario('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),
   'long_first_word': scenario('Supercalifragilisticexpialidocious is a word'),
   'punctuation_and_accents': scenario('¿Qué tal? It\'s 72° & sunny — "perfect" café weather!'),
   'unknown_sender': scenario('Who is this?', sender='+18055550199'),
   'long_sender_name': scenario('Hello from a long name', sender='+18055550102', date_sent='12/31 23:59'),
}

def render(message):
   run_macpi.get_latest_message = lambda: (True, message)
   return capture_display(run_macpi.update_message)

if __name__ == "__main__":
   write_screenshots('macpi', scenarios, render)
