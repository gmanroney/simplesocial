#!/usr/bin/python3
import os
import re
import configparser
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import pdb
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
            if ( record_count == 1 ): writer.writerow(["User","Date","Message","Score"])
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
def SendEmailByGmailo (g_user, g_pass, e_user, e_subject, e_body ):

    gmail_user = g_user
    gmail_password = g_pass
    sent_from = gmail_user
    to=e_user
    print(sent_from,to,gmail_user,gmail_password)

    subject = e_subject
    #f = open(e_body)
    #body = f.readlines().append('\n')`
    #f.close()
    with open(e_body) as f:
        body = f.read()
        print (body)

    #body = 'sssssssssss'
    #f = open(e_body)
    #body = MIMEText(''.join(f.readlines()))
    #f.close()

    print(body)

    email_text = """From: %s  
To: %s  
Subject: %s
<html>
  <head></head>
  <body>
%s
  </body>
</html>
""" % (sent_from, to, subject, body)

    print (email_text)

    try:  
       server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
       server.ehlo()
       server.login(gmail_user, gmail_password)
       server.sendmail(sent_from, to, email_text)
       server.close()
       print ('Email sent!')
    except:  
       print ('Something went wrong...')

#Helper function to send email
def SendEmailByGmail (g_user, g_pass, e_user, e_subject, e_body ):

    gmail_user = g_user
    gmail_password = g_pass
    sent_from = gmail_user
    to=e_user
    subject = e_subject

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = e_subject
    msg['From'] = gmail_user
    msg['To'] = e_user

    with open(e_body) as f:
        body = f.read()

    email_text = """From: %s  
To: %s  
Subject: %s
%s
""" % (sent_from, to, subject, body)
    email_text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org"


    table = ''
    with open(e_body, encoding="utf8") as csvFile:
        reader = csv.DictReader(csvFile, delimiter=',')
        table = '<table id="customers" style="width: 100%" > <colgroup> <col span="1" style="width: 15%;"><col span="1" style="width: 10%;"> <col span="1" style="width: 65%;"> <col span="1" style="width: 5%;"> </colgroup>'
        table += '<tr>{}</tr>'.format(''.join(['<td><b>{}</b></td>'.format(header) for header in reader.fieldnames]))
        for row in reader:
            table_row = '<tr>'
            index = 0
            for fn in reader.fieldnames:
                if index == 3:
                    score = float(row[fn].strip(' "'))
                    if score < 0:
                        table_row += '<td><mark>{}</mark></td>'.format(row[fn])
                    else:
                        table_row += '<td>{}</td>'.format(row[fn])
                else:
                    table_row += '<td>{}</td>'.format(row[fn])

                index +=1
            table_row += '</tr>'
            table += table_row
        table +='</table>'

    email_html = """\
<html>
  <head>
    <style>
      #customers {
        font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
        border-collapse: collapse;
      }
      #customers td, #customers th {
        border: 1px solid #ddd;
        padding: 8px;
      }
      #customers tr:nth-child(even){background-color: #f2f2f2;}
      #customers tr:hover {background-color: #ddd;}
      #customers th {
        padding-top: 12px;
        padding-bottom: 12px;
        text-align: left;
        background-color: #4CAF50;
        color: white;
      }
    </style>
  </head>
  <body>
    <p>Hi!<br><br>
Report for time period specified in e-mail subject displayed in table below.<br><br>
Those items marked yellow have potential negative sentiment and should be investigated further.<br><br>
Since the algorithm for calculating the sentiment is not precise it is also advisable that a manual audit of all records be performed.<br><br>
Regards,<br><br>
Gerard
    </p>
    %s
  </body>
</html>
""" % ( table )

    msg.attach(MIMEText(email_html, 'html'))

    try:  
       server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
       server.ehlo()
       server.login(gmail_user, gmail_password)
       #server.sendmail(sent_from, to, email_text)
       server.sendmail(sent_from, to, msg.as_string())
       server.close()
       print ('Email sent!')
    except:  
       print ('Something went wrong...')
