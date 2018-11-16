#!/usr/bin/python3

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from prettytable import PrettyTable
from pathlib import Path
from datetime import datetime, timedelta, date
from isoweek import Week
from commonFunctions import NiceMsg,ConfigSectionMap,RemoveInvalidAscii

analyzer = SentimentIntensityAnalyzer()

pos_count = 0
pos_correct = 0

import pymongo
import re
import configparser
import smtplib
import csv
import os
import sys

# Helper function to find username
def searchUsrById(usr_id):
    record = {}
    record = mycolu.find_one({'id': usr_id })
    if record['first_name'] is None: record['first_name'] = "unknown"
    if record['last_name'] is None: record['last_name'] = "unknown"
    if record['username'] is None: record['username'] = "unknown"
    summary = record['first_name'] + " " + record['last_name'] + " (" + record['username'] + ")"
    return summary

# Helper function to find a message by ID
def searchMsgById(msg_id):
    record = {}
    record = mycol.find_one({'msg_id': msg_id })
    return record

def searchMsgMain ():
    record_added = 0
    record_updated = 0

    for entry in mycol.find():
        line=entry['msg_message'].replace('\n', ' ').replace('\r', '')
        vs = analyzer.polarity_scores(line)
        mymessage = {  "msg_id": entry['msg_id'],
                       "msg_vader_sentiment": vs }
        cursor = mycola.find({"msg_id": entry['msg_id']})
        if cursor.count() == 0:
            x = mycola.insert_one(mymessage)
            record_added = record_added + 1
        else:
            x = mycola.update({"msg_id": entry['msg_id']},{ "$set": { "msg_vader_sentiment": vs }})
            record_updated = record_updated + 1

    print ("Record added = ", record_added, "Record updated = ", record_updated )

# Read From Config File
config = configparser.ConfigParser()
config.read('./simpleSocial.ini')
mongo_db = ConfigSectionMap("mongo",config)['mongo_db']
mongo_collection = ConfigSectionMap("mongo",config)['mongo_collection']
mongo_users = ConfigSectionMap("mongo",config)['mongo_users']
mongo_analytics = ConfigSectionMap("mongo",config)['mongo_analytics']
gmail_user = ConfigSectionMap("email",config)['gmail_user']
gmail_password = ConfigSectionMap("email",config)['gmail_password']
end_user = ConfigSectionMap("email",config)['end_user']

# Define Mongo connection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient[mongo_db]
mycol = mydb[mongo_collection]
mycolu = mydb[mongo_users]
mycola = mydb[mongo_analytics]

# Run searches based on configuration
searchMsgMain ()

# End program
sys.exit()
