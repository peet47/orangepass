#!/usr/bin/python

#################
#
#                                                                                                             
#                                                               ,-.----.                                      
#                                                               \    /  \                                     
#                                                               |   :    \                                    
#   ,---.    __  ,-.                 ,---,                      |   |  .\ :                                   
#  '   ,'\ ,' ,'/ /|             ,-+-. /  |  ,----._,.          .   :  |: |             .--.--.    .--.--.    
# /   /   |'  | |' | ,--.--.    ,--.'|'   | /   /  ' /   ,---.  |   |   \ : ,--.--.    /  /    '  /  /    '   
#.   ; ,. :|  |   ,'/       \  |   |  ,"' ||   :     |  /     \ |   : .   //       \  |  :  /`./ |  :  /`./   
#'   | |: :'  :  / .--.  .-. | |   | /  | ||   | .\  . /    /  |;   | |`-'.--.  .-. | |  :  ;_   |  :  ;_     
#'   | .; :|  | '   \__\/: . . |   | |  | |.   ; ';  |.    ' / ||   | ;    \__\/: . .  \  \    `. \  \    `.  
#|   :    |;  : |   ," .--.; | |   | |  |/ '   .   . |'   ;   /|:   ' |    ," .--.; |   `----.   \ `----.   \ 
# \   \  / |  , ;  /  /  ,.  | |   | |--'   `---`-'| |'   |  / |:   : :   /  /  ,.  |  /  /`--'  //  /`--'  / 
#  `----'   ---'  ;  :   .'   \|   |/       .'__/\_: ||   :    ||   | :  ;  :   .'   \'--'.     /'--'.     /  
#                 |  ,     .-./'---'        |   :    : \   \  / `---'.|  |  ,     .-./  `--'---'   `--'---'   
#                  `--`---'                  \   \  /   `----'    `---`   `--`---'                            
#                                             `--`-'                                                          
# orangePass
#  just an observer
#
#   Peter Massini
#
#################


import logging
import logging.handlers
import datetime
import certstream
import os, sys
import httplib, urllib
import smtplib

#switches
active_mail = "false"
active_pushy = "false"

#config
mail_to = "MAILTO"
ALERT_TRIGGER = "SEARCH NAME TO TRIGGER"

SEARCHS = ['co.nz', 'google.com'] # OR anything you like to search

#LOGGING 
LOG_FILENAME = '/var/log/orangePass.log'
# Set up a specific logger with our desired output level
my_logger = logging.getLogger('orangePass')
my_logger.setLevel(logging.INFO)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=10240000, backupCount=5)

my_logger.addHandler(handler)

def send_mail(message):
    server = smtplib.SMTP('SMTPADRESS', 587)
    server.starttls()
    #Next, log in to the server
    server.login("USERNAME", "PASSWORD")
    mail_message = """From: USERNAME
To: TEAM """  + """<""" + mail_to + """>""" + """ 
Subject: orangePass

""" + message + """
"""

    #Send the mail
    server.sendmail("USERNAME", mail_to , mail_message)
    server.close()


def pushy(message):
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.urlencode({
        "token": "TOKEN",
        "user": "USER",
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def print_callback(message, context):
    my_logger.debug("Message -> {}".format(message))

    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

        if len(all_domains) == 0:
            domain = "NULL"
        else:
            domain = all_domains[0]

        for SEARCH in SEARCHS:
            if SEARCH in str(all_domains):
                my_logger.info("FOUND!!!!")
                if SEARCH == ALERT_TRIGGER:
                    lable == "IMPORTANT"
                report_message == (u"[{}] FOUND!!! {} {} (SAN: {})\n".format(datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'), lable, domain, ", ".join(message['data']['leaf_cert']['all_domains'][1:])))
                if active_pushy == "true":
                    pushy(report_message)
                if active_mail == "true" or SEARCH == ALERT_TRIGGER:
                    send_mail(report_message)
                #sys.stdout.write("FOUND!!!!")
                my_logger.info(report_message) 

        my_logger.info(u"[{}] {} (SAN: {})\n".format(datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'), domain, ", ".join(message['data']['leaf_cert']['all_domains'][1:])))
        #sys.stdout.write(u"[{}] {} (SAN: {})\n".format(datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'), domain, ", ".join(message['data']['leaf_cert']['all_domains'][1:])))
        #sys.stdout.flush()

logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.INFO)

certstream.listen_for_events(print_callback)
