#!/usr/bin/python3

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
import pymongo
import re
import configparser

# Helper function to read from configuration file
def ConfigSectionMap(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1
                                                                                                                
# Read From Config File
config = configparser.ConfigParser()
config.read('./readChannel.ini')
api_id = ConfigSectionMap("telegram")['api_id']
api_hash = ConfigSectionMap("telegram")['api_hash']
channel_name = ConfigSectionMap("telegram")['channel_name']
mongo_db = ConfigSectionMap("mongo")['mongo_db']
mongo_collection = ConfigSectionMap("mongo")['mongo_collection']

# Define Telegram client connection
client = TelegramClient('readChannel', api_id, api_hash)

# Define Mongo connection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient[mongo_db]
mycol = mydb[mongo_collection]

# Connect to telegram
client.start()
client.connect()

# Connect to channel and get posts
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

# Initalise counter for records added
records_added = 0

# Loop through messages and add if not already present
for message in reversed(posts.messages): 
    cursor = mycol.find({"msg_id": message.id})
    if cursor.count() == 0:
        if message.message is not None:
            records_added = records_added + 1
            pattern = re.compile('[^A-Za-z0-9 -]')
            new_msg = pattern.sub('',message.message)
            print (message)
            mydict = {  "msg_id": message.id,
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
            x = mycol.insert_one(mydict)

# Report records added
print("Records added = ", records_added)

# Close connection
client.disconnect()
