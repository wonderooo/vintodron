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

def contains_newest_filter(message):
    message_c = message.content
    if '&order=newest_first' in message_c:
        return True
    else:
        return False
"""
END
"""

client = discord.Client()
db_client = MongoClient(MONGO_CLIENT)
db = db_client['vinted']
collection = db['channel_subs']
collection_offers = db['offers']
collection_keeper = db['keeper']

@client.event
async def on_ready():
  print('logged as {user}'.format(user = client.user))
  db_logger.start(collection_offers, collection_keeper, client)
@client.event

async def on_message(message):
  #channel = str(message.channel.name)
  if check_author(message, client) == False:
    return
  else:
    command, url, channel_name = check_content(message)
    if command == 'sub':
      if duplicate(url, channel_name, collection) == False:
        if contains_newest_filter(message) == True:
            await send_response(message, 'Vinted sub on channel {channel}'.format(channel=channel_name))
            await create_subchannel(message, channel_name)
            subchannel_to_db(collection, url, channel_name)
            return
        else:
            await send_response(message, 'url must contain newest first filter!')
            return
      else:
        await send_response(message, 'Channel with this url or name already exists')
        return
    elif command == 'del':
      await del_subchannel(message, url)
      del_post(collection, url)
      return

@tasks.loop(seconds=0.1)
async def db_logger(collection_offers, collection_keeper, client):
    offers_query = list(collection_offers.find({}))
    for offer in offers_query:
        if offer['posted'] == 'False':
            current_channel = offer['channel_name']
            for c in client.get_all_channels():
                if str(current_channel) == str(c):
                    _id = offer['_id']
                    make = offer['make']
                    description = offer['description']
                    price = offer['price']
                    reference = offer['reference']
                    image_path = offer['image_path']
                    image_path = '/data/common/{path}.png'.format(path = image_path)
                    print(image_path)
                    payload = '{make}\n{description}\n{price}\n{reference}\n'.format(make=make, description=description, price=price, reference=reference, image_path = image_path)
                    await c.send(payload, file = discord.File(image_path))
                    os.remove(image_path)
                    #file = discord.File('images/{image_path}'.format(image_path=image_path))
                    collection_offers.update_one({'_id': _id}, {'$set': {'posted': 'True'}})
                    return



    #channel_query = collection_offers.find({}, {'channel_name': 1, '_id': 0})
    #reference_query = collection_offers.find({}, {'reference': 1, '_id': 0})
    #keeper_value = collection_keeper.find({}, {'keeper': 1, '_id':0})
    #keeper_value = list(keeper_value)[0]['keeper']
    #if int(keeper_value) != len(list(collection_offers.find())):
        #current_offer = list(collection_offers.find({'_id': int(keeper_value)}))[0]
        #current_channel = current_offer['channel_name']
        #for c in client.get_all_channels():
            #if str(current_channel) == str(c):
                #make = current_offer['make']
                #description = current_offer['description']
                #price = current_offer['price']
                #reference = current_offer['reference']
                #image_path = current_offer['image_path']
                #payload = '{make}\n{description}\n{price}\n{reference}\n'.format(make=make, description=description, price=price, reference=reference, image_path = image_path)
                #print(payload)
                #await c.send(payload, file = discord.File('images/{image_path}'.format(image_path=image_path)))
                #collection_keeper.update_one({'_id':0}, {'$set': {'keeper': int(keeper_value) + 1}})
                #return
client.run(TOKEN)










