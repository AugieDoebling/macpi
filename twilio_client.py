# Download the helper library from https://www.twilio.com/docs/python/install
import os
import json
from pytz import timezone
from twilio.rest import Client

cache_filename = './lastmessage.json'
time_format = "%m/%d %H:%M"

def retreive_last_twilio_message():
    account_sid = ""
    auth_token = ""
    client = Client(account_sid, auth_token)

    messages = client.messages.list(limit=20, to='+18456134979')
    return serialize_message(messages[0])

def load_last_message():
    try:
        f = open(cache_filename, 'r')
        last_message = json.loads(f.read())
        return last_message
    except Exception as e:
        print('error loading message', e)
        return None

def serialize_message(message):
    return {
        'sid': message.sid,
        'body': message.body,
        'from': message.from_,
        'date_sent': message.date_sent.astimezone(timezone('America/Los_Angeles')).strftime(time_format),
    }

def save_last_message(message):
    try:
        f = open(cache_filename, 'w+')
        json.dump(message, f)
        f.close()
    except Exception as e:
        print('error saving message', e)

def get_latest_message():
    message = retreive_last_twilio_message()
    cached = load_last_message()
    is_new = cached == None or message['sid'] != cached['sid']
    if is_new:
        save_last_message(message)

    return (is_new, message)
