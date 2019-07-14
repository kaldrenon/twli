'''
DO A REPL
'''
from __future__ import unicode_literals, print_function

import ipdb
import json
import psycopg2
import signal
import sys
import twitter
import urllib.parse

from datetime import datetime
from dateutil import parser
from orator import Model, SoftDeletes
from prompt_toolkit import prompt
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style

from lib.database import User, List, ListUser

#
# CONFIG SETUP
#
config = {}

with open('./config.json', 'r') as json_data_file:
    config = json.load(json_data_file)

# Brought over from tw.py

api = twitter.Api(consumer_key = config['twitter']['consumer_key'],
                  consumer_secret= config['twitter']['consumer_secret'],
                  access_token_key= config['twitter']['access_token_key'],
                  access_token_secret= config['twitter']['access_token_secret'])

db = psycopg2.connect(f"dbname={config['postgres']['database']}")

# Signal Handler enables Ctrl-C to quit
def signal_handler(sig, frame):
  print('\nDone.')
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#
# Helpers
#
def sp(text):
  style = Style.from_dict({
    'user': '#609db5',
    'tweet': '#b5a360',
    'timestamp': '#386577'
    })

  print_formatted_text(HTML(text), style=style)

#
# Implementations of all Commands
#
def send_tweet():
  tweet_text = prompt('--> ')
  api.PostUpdate(tweet_text)

def get_timeline():
  current_tl = api.GetHomeTimeline()
  for tweet in current_tl:
    sp(f"<timestamp>{tweet.created_at}</timestamp><user>{tweet.user.screen_name}</user>\n  <tweet>{tweet.text}</tweet>\n")

def get_my_timeline():
  current_tl = api.GetUserTimeline(screen_name='kaldrenon')
  for tweet in current_tl:
    print(f'{tweet.user.screen_name}: {tweet.text}')

def create_list():
  list_name = prompt('List name -> ')

  try:
    new_list = List()
    new_list.name = list_name
    new_list.save()
  except Exception as err:
    print('error: ')
    print(err)

def add_to_list():
  actor = db.cursor()
  username = prompt('Username -> ')

  try:
    user = User.where('username', 'like', username).first()
    if user:
      print('user known')
    else:
      print(f'{username} added to user database')
      user = User()
      user.username = username
      user.save()

    list_name = prompt('List name -> ')
    list_id = List.where('name', 'like', list_name).first().id
    user_id = user.id

    association = ListUser()
    association.user_id = user_id
    association.list_id = list_id
    association.save()

  except Exception as err:
    print('did a bad')
    print(err)

def read_list():
  list_name = prompt('List name -> ')

  sel_list = List.where('name', 'like', list_name).first()
  users = list(map(lambda user: user.username, sel_list.users))

  middle = ", OR from:"
  query = f"(from:{middle.join(users)})"
  print(query)
  query = urllib.parse.quote(query)
  query = f"q={query}"
  print(query)
  tweets = api.GetSearch(raw_query=query)
  for tweet in tweets:
    dt = parser.parse(tweet.created_at)
    timestamp = dt.strftime('%Y-%M-%d %H:%m')
    sp(f"<timestamp>[{timestamp}]</timestamp> <user>{tweet.user.screen_name}</user>\n  <tweet>{tweet.text}</tweet>\n")

def print_lists():
  for tw_list in List.all():
    print(tw_list.name)

commands = {
  'la': add_to_list,
  'l': print_lists,
  'lc': create_list,
  'lr': read_list,
  'tweet': send_tweet,
  'tl': get_timeline,
  'tlm': get_my_timeline
}

def parse_command(command):
  if command == 'exit' or command == 'x':
    return False
  elif command in commands.keys():
    commands[command]()
    return True
  else:
    print('unknown command - enter \'help\' for command list')
    return True

#
# Main function loop
#
if __name__ == '__main__':
  try:
    while True:
      user_input = prompt('-> ')

      if parse_command(user_input):
        continue
      else:
        break
  except KeyboardInterrupt:
    print('Done.')
    sys.exit(0)
