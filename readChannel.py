#!/usr/bin/python3

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
import pymongo
import re

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = xxx
api_hash = 'xxx'
client = TelegramClient('session_name', api_id, api_hash)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["telegram"]
mycol = mydb["cardanodevelopersofficial"]

client.start()
client.connect()

#print(client.get_me().stringify())

print ("Starting execution")

channel_username='CardanoDevelopersOfficial' # your channel
channel_entity=client.get_entity(channel_username)


posts = client(GetHistoryRequest(
        peer=channel_entity,
        limit=1000000,
        offset_date=0,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0))

for message in reversed(posts.messages): 
    cursor = mycol.find({"msg_id": message.id})
    if cursor.count() == 0:
        if len(message.message) > 0:
            print (cursor.count())
            pattern = re.compile('[^A-Za-z0-9 -]')
            new_msg = pattern.sub('',message.message)
            print(message.date,"---",message.from_id,"---",new_msg,"---",message.id)
            mydict = { "msg_date": message.date,"msg_from_id": message.from_id,"msg_body": new_msg,"msg_id": message.id }
            x = mycol.insert_one(mydict)
    
client.disconnect()
