import discord
from discord.ext import tasks
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

load_dotenv()
TOKEN = os.getenv('DC_BOT_TOKEN')
MONGO_CLIENT = os.getenv('MONGO_CLIENT')
    
"""
CUSTOM DEFS
"""

def check_author(message, client):
  if message.author == client.user:
    return False
  else:
    return True
 
def check_content(message):
  message_c = message.content
  message_c = message_c.split()
  if '!sub' in message_c[0] and 'https://www.vinted.pl' in message_c[1] and len(message_c) == 3:
    return 'sub', message_c[1], message_c[2]
  elif '!del' in message_c[0] and len(message_c) == 2:
    return 'del', message_c[1], None
  else:
    return False, None, None

async def send_response(message, response):
  return await message.channel.send(str(response))
 
async def create_subchannel(message, channel_name):
  return await message.guild.create_text_channel(channel_name)

def subchannel_to_db(collection, url, channel_name):
  pointer = len(list(collection.find()))
  post = {
    '_id': pointer,
    'channel_name': str(channel_name),
    'url': str(url)
  }
  collection.insert_one(post)
  return

def del_post(collection, channel_name):
  post = {
    'channel_name': str(channel_name),
  }
  collection.delete_one(post)
  return

async def del_subchannel(message, channel_name):
  server = message.guild
  for channel in server.channels:
    if str(channel) == channel_name:
      await channel.delete()
  return

def duplicate(url, channel_name, collection):
  duplicate = False
  for e, query in enumerate([url, channel_name]):
    if e == 0:
      post = {
        'url': url
      }
    else:
      post = {
        'channel_name': channel_name 
      }
    if len(list(collection.find(post))) != 0:
      duplicate = True
  return duplicate
"""
END
"""

client = discord.Client()
db_client = MongoClient(MONGO_CLIENT)
db = db_client['vinted']
collection = db['channel_subs']

@client.event
async def on_ready():
  print('logged as {user}'.format(user = client.user))
  slow_count.start(collection)
@client.event

async def on_message(message):
  #channel = str(message.channel.name)
  if check_author(message, client) == False:
    return
  else:
    command, url, channel_name = check_content(message)
    if command == 'sub':
      if duplicate(url, channel_name, collection) == False:
        await send_response(message, 'Vinted sub on channel {channel}'.format(channel=channel_name))
        await create_subchannel(message, channel_name)
        subchannel_to_db(collection, url, channel_name)
        return
      else:
        await send_response(message, 'Channel with this url or name already exists')
        return
    elif command == 'del':
      await del_subchannel(message, url)
      del_post(collection, url)
      return

@tasks.loop(seconds=10.0)
async def slow_count(collection):
  print(len(list(collection.find())))
  a = 'guwno'
  print('-----')

client.run(TOKEN)

