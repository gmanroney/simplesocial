#!/usr/bin/python3

from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

pos_count = 0
pos_correct = 0

import pymongo
import re
import configparser
import smtplib

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

# Helper function to send email

#def DailyReport
#def WeeklyReport
#def EventReport 
#    SendEmail

def SendEmailByGmail (g_user, g_pass, e_user, e_subject, e_body):
    sent_from = g_user  
    sent_to = e_user
    subject = 'OMG Super Important Message'  
    body = 'Hey, what\'s up?\n\n- You'
    email_text = """\  
From: %s  
To: %s  
Subject: %s

%s
""" % (sent_from, ", ".join(sent_to), subject, body)
    try:  
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(g_user, g_pass)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()
        print ('Email sent!')
    except:  
        print ('Something went wrong...')

# Read From Config File
config = configparser.ConfigParser()
config.read('./analyseSocial.ini')
mongo_db = ConfigSectionMap("mongo")['mongo_db']
mongo_collection = ConfigSectionMap("mongo")['mongo_collection']
mongo_users = ConfigSectionMap("mongo")['mongo_users']
mongo_analytics = ConfigSectionMap("mongo")['mongo_analytics']
gmail_user = ConfigSectionMap("email")['gmail_user']
gmail_password = ConfigSectionMap("email")['gmail_password']
end_user = ConfigSectionMap("email")['end_user']

# Define Mongo connection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient[mongo_db]
mycol = mydb[mongo_collection]
mycolu = mydb[mongo_users]
mycola = mydb[mongo_analytics]

# Check for iohk
print ('\n----------------- iohk ------------')
for xxx in mycol.find({'msg_message': { '$regex': 'iohk', '$options': 'i' }}):
    line=xxx['msg_message']
    vs = analyzer.polarity_scores(line)
    if vs['compound'] < 0:
        print (xxx['msg_date'],line,vs['compound'])
# Check for emurgo
print ('\n----------------- emurgo ------------')
for xxx in mycol.find({'msg_message': { '$regex': 'emurgo', '$options': 'i' }}):
    line=xxx['msg_message']
    vs = analyzer.polarity_scores(line)
    if vs['compound'] < 0:
        print (xxx['msg_date'],line,vs['compound'])
# Check for rust
print ('\n------------------ rust ------------')
cursor1 = mycol.find({'msg_message': { '$regex': ' rust', '$options': 'i' }})
for xxx in cursor1:
    line = re.sub(r'[\x00-\x1F]+', '', xxx['msg_message'])
    vs = analyzer.polarity_scores(line)
    if vs['compound'] < 0:
        print (xxx['msg_date'],line,vs['compound'])

# Close connection
#client.disconnect()
