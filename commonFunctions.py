#!/usr/bin/python3
import os
import configparser

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

