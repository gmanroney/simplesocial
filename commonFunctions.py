#!/usr/bin/python3
import os
import configparser
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv

# Helper function to dump files to csv file
def dumpToCsv (mycol,mycolu,period,my_out_file):

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
            if ( record_count == 1 ): writer.writerow(["user","date","message","score"])
            writer.writerow([RemoveInvalidAscii(userIdentity),entry['msg_date'],RemoveInvalidAscii(line),vs['compound']])
    NiceMsg ('Total records exported = ' + str(record_count))

# Helper function to find a message by ID
def searchMsgById(msg_id,mycol):
    record = {}
    record = mycol.find_one({'msg_id': msg_id })
    return record

# Helper function to find username
def searchUsrById(usr_id,mycolu):
    record = {}
    record = mycolu.find_one({'id': usr_id })
    if record['first_name'] is None: record['first_name'] = "unknown"
    if record['last_name'] is None: record['last_name'] = "unknown"
    if record['username'] is None: record['username'] = "unknown"
    summary = record['first_name'] + " " + record['last_name'] + " (" + record['username'] + ")"
    return summary

def searchMsgByDate (mycol,period):
    dt = date.today()

    option = period
    end = datetime.combine(dt, datetime.max.time())
    if option == "today":
        start = datetime.combine(dt, datetime.min.time())
    elif option == "yesterday":
        start = datetime.combine(dt, datetime.min.time()) - timedelta(days=1)
        end = datetime.combine(dt, datetime.max.time()) - timedelta(days=1)
    elif option == "week":
        start = datetime.combine( dt - timedelta(days=dt.weekday()), datetime.min.time())
    elif option == "month":
        start = datetime.combine( dt - relativedelta(day=1) , datetime.min.time())
    elif option == "year":
        start = datetime.combine( dt - relativedelta(month=1,day=1) , datetime.min.time())
    elif option == "forever":
        start = datetime.combine( date(1970, 1, 1) , datetime.min.time())
    else:
        NiceMsg("Invalid option for searchMsgMain; using 'today'")
        start = datetime.combine(dt, datetime.min.time())
    mongo_query = mycol.find({"msg_date": { "$gte": start, "$lt": end}});
    record_count = 0
    result = []
    for entry in mongo_query:
        result.append(entry)
        record_count = record_count + 1
    if record_count == 0: 
        print ("No records found")
    return result

# Helper for adding timestamp to message
def NiceMsg(message): 
    f=os.popen('date').read().rstrip("\n\r")
    print("[",f,"]",message)

# Helper function to read from configuration file
def ConfigSectionMap(section,config):
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

# Helper to remove invalid ascii characters (non-ASCII ones)
def RemoveInvalidAscii(input):
    input = input.encode('ascii', 'ignore').decode('ascii')
    return input

# Helper function to send email
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

