#!/usr/bin/python3

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
import pymongo
import re

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = 297114
records_added = 0
api_hash = '45692fe05242e19d33fd512e1893d737'
client = TelegramClient('session_name', api_id, api_hash)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["telegram"]
mycol = mydb["cardanodevelopersofficial"]

client.start()
client.connect()

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
                        "msg_fwd_from": message.fwd_from,
                        "msg_via_bot_id": message.via_bot_id,
                        "msg_reply_to_msg_id": message.reply_to_msg_id,
                        "msg_reply_markup": message.reply_markup,
                        "msg_views": message.views,
                        "msg_edit_date": message.edit_date,
                        "msg_post_author": message.post_author,
                        "msg_grouped_id": message.grouped_id }
            x = mycol.insert_one(mydict)

print("Records added = ", records_added)
client.disconnect()
