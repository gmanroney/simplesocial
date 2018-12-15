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
    record_count = 0
    dt = date.today()

    option = "forever"
    if option == "today":
        start = datetime.combine(dt, datetime.min.time())
        end = datetime.combine(dt, datetime.max.time())
    elif option == "yesterday":
        start = datetime.combine(dt, datetime.min.time()) - timedelta(days=1)
        end = datetime.combine(dt, datetime.max.time()) - timedelta(days=1)
    elif option == "week":
        week = dt.isocalendar()[1]
        dow = dt.weekday()
        start = datetime.combine(dt, datetime.min.time()) - timedelta(dow)
        end = datetime.combine(dt, datetime.max.time()) + timedelta(days=6 - dow)
    elif option == "month":
        start = datetime.combine(dt, datetime.min.time())
        end = datetime.combine(dt, datetime.max.time())
    elif option == "month":
        start = datetime.combine(dt, datetime.min.time())
        end = datetime.combine(dt, datetime.max.time())
    elif option == "forever":
        start = ""
        end = ""
    else:
        NiceMsg("Invalid option for searchMsgMain; exiting")


    print (start)
    print (end)
    result = mycol.find({"msg_date": { "$gte": start, "$lt": end}});

    for entry in result:
        print(entry)
        record_count = record_count + 1
    if record_count > 0: 
        print ("Records found =", record_count)
    else:
        print ("No records found")

def searchMsgMain2 (m_term,m_type):
    record_count = 0
    myPrettyTable = PrettyTable (["User","Date","Message","Score"])
    myPrettyTable.align["User"]="l"
    myPrettyTable.align["Message"]="l"
    myPrettyTable.align["Score"]="l"

    # Title of report
    if ( m_type > 0 ): 
        m_type_desc = "neutral to +ve"
    elif ( m_type < 0 ): 
        m_type_desc = "neutral to -ve"
    else:
        m_type_desc = "all regardless of sentiment"

    print ("Sentiment: ",m_type_desc)

    for entry in mycol.find({'msg_message': { '$regex': m_term, '$options': 'i' }}):
        line=entry['msg_message'].replace('\n', ' ').replace('\r', '')
        userIdentity = searchUsrById(entry['msg_from_id'])
        vs = analyzer.polarity_scores(line)
        mymessage = {  "msg_id": entry['msg_id'],
                       "msg_vader_sentiment": vs }
        cursor = mycola.find({"msg_id": entry['msg_id']})
        print (cursor)
        if cursor.count() == 0:
            x = mycola.insert_one(mymessage)
        else:
            x = mycola.update({"msg_id": entry['msg_id']},{ "$set": { "msg_vader_sentiment": vs }})

        if ( float(vs['compound']) * m_type ) >= 0  :
           myPrettyTable.add_row([RemoveInvalidAscii(userIdentity),entry['msg_date'],RemoveInvalidAscii(line[:120]),vs['compound']])
           record_count = record_count + 1
    if record_count > 0: 
        print (myPrettyTable)
    else:
        print ("No records found")

# Read From Config File
config = configparser.ConfigParser()
config.read('./analyseSocial.ini')
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

#searchMsgMain()

# Run searches based on configuration
for key, value in config.items('report'):
    searchTerm,searchType,searchRange=value.split(":")
    f=os.popen('date').read().rstrip("\n\r")
    print("[",f, "] Executing search :",searchTerm,searchType)
    searchMsgMain2 (searchTerm,int(searchType))

# End program
sys.exit()
