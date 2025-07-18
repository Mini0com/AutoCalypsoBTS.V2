#!/usr/bin/env python3
import telnetlib
import sqlite3
import sys

imsi = 606059999999999
HLR_DATABASE = "hlr.sqlite3"

def check_extension(extension):
    conn.write(bytes("show subscriber extension %s\n" % extension, 'utf-8'))
    res = conn.read_until(bytes("OpenBSC> ", 'utf-8'))

    if bytes("No subscriber found for extension", 'utf-8') in res:
        create_subscriber(extension)

def create_subscriber(extension):
    print("No user with excension %s found. Creating new..." % extension)
    print("Extension: %s, IMSI: %d" % (extension, imsi))

    conn.write(bytes("show subscriber imsi %d\n" % imsi, 'utf-8'))
    res = conn.read_until(bytes("OpenBSC> ", 'utf-8'))

    if bytes("No subscriber found for imsi", 'utf-8') in res:
        conn.write(bytes("subscriber create imsi %d\n" % imsi, 'utf-8'))
        conn.read_until(bytes("OpenBSC> ", 'utf-8'))

    conn.write(bytes("enable\n", 'utf-8'))
    conn.read_until(bytes("OpenBSC# ", 'utf-8'))
    conn.write(bytes("subscriber imsi %d extension %s\n" % (imsi, extension), 'utf-8'))
    conn.read_until(bytes("OpenBSC# ", 'utf-8'))
    conn.write(bytes("disable\n", 'utf-8'))
    conn.read_until(bytes("OpenBSC> ", 'utf-8'))

def get_users():
    # returns user id list generator

    db = sqlite3.connect(HLR_DATABASE)
    c = db.cursor()
    c.execute("SELECT * FROM Subscriber")

    for subscriber in c.fetchall():
        yield subscriber[0]

def send_sms(id, extension, message):
    conn.write(bytes("subscriber id %d sms sender extension %s send %s\n" % (id, extension, message), 'utf-8'))
    res = conn.read_until(bytes("OpenBSC> ", 'utf-8'))
    if bytes("%", 'utf-8') in res:
        print(res)
        exit(1)

if __name__ == "__main__":
    try:
        extension = sys.argv[1]
        message = " ".join(sys.argv[2:])
    except:
        print("usage: ./sms_broadcast.py extension message")
        print("This script sends a message from the specified extension (number) to all devices connected to this base station")
        exit(1)

    conn = telnetlib.Telnet("127.0.0.1", 4242)
    conn.read_until(bytes("OpenBSC> ", 'utf-8'))

    check_extension(extension)

    for id in get_users():
        send_sms(id, extension, message)
