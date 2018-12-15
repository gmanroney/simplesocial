#!/usr/bin/python3

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from prettytable import PrettyTable
from pathlib import Path
from datetime import datetime, timedelta, date
from isoweek import Week
from commonFunctions import NiceMsg,ConfigSectionMap,RemoveInvalidAscii,searchUsrById,searchMsgByDate,SendEmailByGmail

pos_count = 0
pos_correct = 0

import pymongo
import re
import configparser
import smtplib
import csv
import os
import sys

def dumpToCsv (period,my_out_file):

    record_count = 0
    outfile=my_out_file
    Path(outfile).touch()
    os.remove(outfile)

    NiceMsg ('++++++++++ CSV DUMP ++++++++++++++++')
    results = []
    results = searchMsgByDate(mycol,period)
    analyzer = SentimentIntensityAnalyzer()

    for entry in results:
        line=entry['msg_message']
        userIdentity = searchUsrById(entry['msg_from_id'],mycolu)
        vs = analyzer.polarity_scores(line)
        record_count = record_count + 1
        with open(outfile, 'a') as writeFile: 
            writer = csv.writer(writeFile,quoting=csv.QUOTE_ALL,lineterminator=os.linesep)
            if ( record_count == 1 ): writer.writerow(["User","Date","Message","Score"])
            writer.writerow([RemoveInvalidAscii(userIdentity),entry['msg_date'],RemoveInvalidAscii(line),vs['compound']])
    
    NiceMsg ('Total records exported = ' + str(record_count))

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

# Read option; if blank then set default 'forever'
#period=sys.argv[1]
if len(sys.argv) < 2:
    period='forever'
else:
    period=sys.argv[1]

print (period)
# Full dump to CSV file
dumpToCsv(period,out_file)
SendEmailByGmail (gmail_user, gmail_password, end_user, "Social Report For Period: " + period, out_file)

# End program
sys.exit()
