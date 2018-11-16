#!/usr/bin/python3

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from commonFunctions import NiceMsg
from commonFunctions import ConfigSectionMap

import pymongo
import re
import sys
import os
import configparser

# Read From Config File
config = configparser.ConfigParser()
config.read('/home/germoroney/simplesocial/simpleSocial.ini')
api_id = ConfigSectionMap("telegram",config)['api_id']
api_hash = ConfigSectionMap("telegram",config)['api_hash']
channel_name = ConfigSectionMap("telegram",config)['channel_name']
mongo_db = ConfigSectionMap("mongo",config)['mongo_db']
mongo_collection = ConfigSectionMap("mongo",config)['mongo_collection']
mongo_users = ConfigSectionMap("mongo",config)['mongo_users']

# Define Telegram client connection
client = TelegramClient('readChannel', api_id, api_hash)

# Define Mongo connection
try:
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
except:
    NiceMsg("Could not connect to mongodb")

mydb = myclient[mongo_db]
mycol = mydb[mongo_collection]
mycolu = mydb[mongo_users]

# Connect to telegram
try:
    client.start()
    client.connect()
except:
    NiceMsg("Could not connect to telegram")

# Connect to channel and get posts
try:
    channel_entity=client.get_entity(channel_name)
    posts = client(GetHistoryRequest(
        peer=channel_entity,
        limit=1000000,
        offset_date=0,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0))
except:
    NiceMsg("Could not connect to channel ", channel_name)

NiceMsg("Read messages from chanel " + channel_name)

# Initalise counter for records added
message_added = 0
user_added = 0

NiceMsg("Processing messages")
# Loop through messages and add if not already present
for message in reversed(posts.messages): 

    # Check if user and message is in database or not
    cursor = mycol.find({"msg_id": message.id})
    cursoru = mycolu.find({"id": message.from_id})

    # If no user record add it
    if cursoru.count() == 0:
        user_added = user_added + 1
        user = client.get_entity(PeerUser(message.from_id))
        print (user)
        myuser = { "id": user.id,
                   "access_hash": user.access_hash,
                   "first_name": user.first_name,
                   "last_name": user.last_name,
                   "username": user.username }
        x = mycolu.insert_one(myuser)

    # If no message record add it
    if cursor.count() == 0:
        if message.message is not None:
            message_added = message_added + 1
            pattern = re.compile('[^A-Za-z0-9 -]')
            new_msg = pattern.sub('',message.message)
            print (message)
            mymessage = {  "msg_id": message.id,
                        "msg_date": message.date,
                        "msg_message": message.message,
                        "msg_out": message.out,
                        "msg_mentioned": message.mentioned,
                        "msg_silent": message.silent,
                        "msg_post": message.post,
                        "msg_from_id": message.from_id,
                        "msg_via_bot_id": message.via_bot_id,
                        "msg_reply_to_msg_id": message.reply_to_msg_id,
                        "msg_reply_markup": message.reply_markup,
                        "msg_views": message.views,
                        "msg_edit_date": message.edit_date,
                        "msg_post_author": message.post_author,
                        "msg_grouped_id": message.grouped_id }
            x = mycol.insert_one(mymessage)

# Report records added
f=os.popen('date').read().rstrip("\n\r")
NiceMsg("Messages added = " + str(message_added))
NiceMsg("Users added = " + str(user_added))

# Close connection
client.disconnect()

# End program
sys.exit()
