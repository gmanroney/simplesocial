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

def dumpToCsv (my_out_file):
    record_count = 0
    outfile=my_out_file
    Path(outfile).touch()
    os.remove(outfile)
    NiceMsg ('++++++++++ CSV DUMP ++++++++++++++++')
    for entry in mycol.find():
        line=entry['msg_message']
        userIdentity = searchUsrById(entry['msg_from_id'])
        vs = analyzer.polarity_scores(line)
        record_count = record_count + 1
        with open(outfile, 'a') as writeFile: 
            writer = csv.writer(writeFile,quoting=csv.QUOTE_ALL,lineterminator=os.linesep)
            if ( record_count == 1 ): writer.writerow(["user","date","message","score"])
            if ( record_count % 50 == 0 ): print ('writing record :',record_count)
            writer.writerow([RemoveInvalidAscii(userIdentity),entry['msg_date'],RemoveInvalidAscii(line),vs['compound']])

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
out_file = ConfigSectionMap("export",config)['out_file']

# Define Mongo connection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient[mongo_db]
mycol = mydb[mongo_collection]
mycolu = mydb[mongo_users]
mycola = mydb[mongo_analytics]

# Full dump to CSV file
dumpToCsv(out_file)

# End program
sys.exit()
