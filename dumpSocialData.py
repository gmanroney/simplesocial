#!/usr/bin/python3

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from prettytable import PrettyTable
from datetime import datetime, timedelta, date
from isoweek import Week
from commonFunctions import NiceMsg,ConfigSectionMap,RemoveInvalidAscii,searchUsrById,searchMsgByDate,dumpToCsv
import pymongo
import re
import configparser
import smtplib
import os
import sys

pos_count = 0
pos_correct = 0

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

# Full dump to CSV file
dumpToCsv(mycol,mycolu,period,out_file)

# End program
sys.exit()
