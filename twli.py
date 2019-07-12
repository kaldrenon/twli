'''
DO A REPL
'''
import json
import psycopg2
import signal
import sys
import twitter

from prompt_toolkit import prompt



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
# Implementations of all Commands
#
def send_tweet():
  tweet_text = clint.textui.prompt.query('--> ')
  api.PostUpdate(tweet_text)

def get_timeline():
  current_tl = api.GetHomeTimeline()
  for tweet in current_tl:
    print(f"{tweet.user.screen_name}:\n  {tweet.text}\n")

def get_my_timeline():
  current_tl = api.GetUserTimeline(screen_name='kaldrenon')
  for tweet in current_tl:
    print(f'{tweet.user.screen_name}: {tweet.text}')

def create_list():
  actor = db.cursor()

  list_name = clint.textui.prompt.query('List name -> ')

  try:
    actor.execute(f'INSERT INTO lists (title) VALUES ({list_name});')
    db.commit()
  except:
    print('goof\'d')

def add_to_list():
  actor = db.cursor()
  username = clint.textui.prompt.query('Username -> ')

  try:
    SQL = "SELECT * FROM users WHERE username LIKE %s"
    actor.execute(SQL, (username, ))
    if len(actor.fetchall()) > 0:
      print('user known')
    else:
      print('user not recorded - will insert')
      SQL = "INSERT INTO users (username) VALUES (%s);"
      actor.execute(SQL, (username, ))

    # list_name = clint.textui.prompt.query('List name -> ')
    #
    # list_id = 1
    # user_id = 1
    #
    # SQL = "INSERT INTO mtm_users_lists (user_id, list_id) VALUES (%s, %s);"
    # actor.execute(SQL, (user_id, list_id))
    #
    # db.commit()
  except Exception as err:
    print('did a bad')
    print(err)

def print_lists():
    pass

commands = {
  'la': add_to_list,
  'l': print_lists,
  'lc': create_list,
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

if __name__ == '__main__':
  while True:
    user_input = prompt('-> ')

    if parse_command(user_input):
      continue
    else:
      break

