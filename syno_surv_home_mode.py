#!/usr/bin/env python3

import pycurl
from io import BytesIO
import json
import pynetgear
import datetime
import logging

logging.basicConfig(filename='/tmp/synology.log',level=logging.DEBUG)
synoip = "https://192.168.1.2:5001/webapi/"
user = "cam"
password = "XXXXXXXXX"

def sendurl(url):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(pycurl.FOLLOWLOCATION, True)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    # Body is a byte string.
    # We have to know the encoding in order to print it to a text file
    # such as standard output.
    return(body.decode('iso-8859-1'))

def amihome():
    netg = pynetgear.Netgear()
    netg.password='XXXXXXXXXXX'
    homemacs=['AA:BB:CC:11:22:33','DD:EE:FF:44:55:66']
    macs = []
    for device in netg.get_attached_devices():
        macs.append(device.mac)
    if [i for i in homemacs if i in macs]:
        return("true")
    else:
        return("false")

def gettime():
    return('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))

homestate = amihome()

try:
    with open("/tmp/amihome.txt","r") as file:
        homestate_prev = file.read()
except:
    f = open("/tmp/amihome.txt","w")
    f.write("unknown")
    homestate_prev = 'unknown'
    f.close()

logging.debug(gettime()+' homestate: '+homestate)
logging.debug(gettime()+' homestate_prev: '+homestate_prev)

if homestate != homestate_prev:
    try:
        loginresponse = json.loads(sendurl("".join([synoip,"auth.cgi?api=SYNO.API.Auth&method=login&version=3&account=", user, "&passwd=", password, "&session=SurveillanceStation&format=sid"])))
    except:
        logging.error(gettime()+' login failed')
    logging.debug(gettime()+' loginresponse: '+json.dumps(loginresponse))
    if loginresponse['success']:
        hommoderesponse = json.loads(sendurl("".join([synoip, "entry.cgi?api=SYNO.SurveillanceStation.HomeMode&version=1&method=Switch&on=",homestate,"&_sid=",loginresponse['data']['sid']])))
        logging.debug(gettime()+' hommoderesponse: '+json.dumps(hommoderesponse))
        logoutresponse = json.loads(sendurl("".join([synoip, "auth.cgi?api=SYNO.API.Auth&method=logout&version=1"])))
        logging.debug(gettime()+' logoutresponse: '+json.dumps(logoutresponse))
        with open("/tmp/amihome.txt","w") as file:
            file.write(homestate)

