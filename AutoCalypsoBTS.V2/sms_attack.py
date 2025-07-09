#!/usr/bin/env python3
import telnetlib
import sys
import random
import time

imsi = 999999999999999  # IMSI for spam subscriber

def check_extension(extension):
    cmd = f"show subscriber extension {extension}\n"
    conn.write(cmd.encode('ascii'))
    res = conn.read_until(b"OpenBSC> ")

    if b"No subscriber found for extension" in res:
        print(f"Phone with extension {extension} not found ;(")
        exit(1)

def check_spam_subscriber():
    conn.write(b"show subscriber imsi %d\n" % imsi)
    res = conn.read_until(b"OpenBSC> ")

    if b"No subscriber found for imsi" in res:
        conn.write(b"subscriber create imsi %d\n" % imsi)
        print(conn.read_until(b"OpenBSC> "))

def generate_spam_number():
    prefix = random.choice(['091', '092', '093', '094'])
    return prefix + ''.join(random.choices('0123456789', k=7))

def send(extension, spam_number, message):
    print(f"Sending SMS from {spam_number}...")

    # Configure temporary subscriber
    conn.write(b"enable\n")
    conn.read_until(b"OpenBSC# ")
    cmd = f"subscriber imsi {imsi} extension {spam_number}\n"
    conn.write(cmd.encode('ascii'))
    conn.read_until(b"OpenBSC# ")
    conn.write(b"disable\n")
    conn.read_until(b"OpenBSC> ")

    # Send SMS
    cmd = f"subscriber extension {extension} sms sender extension {spam_number} send {message}\n"
    conn.write(cmd.encode('ascii'))
    res = conn.read_until(b"OpenBSC> ")

    if b"%" in res:
        print(res.decode('ascii'))
        exit(1)

if __name__ == "__main__":
    try:
        extension = sys.argv[1]
        repeats = int(sys.argv[2])
        message = " ".join(sys.argv[3:])
    except:
        print("Usage: ./sms_broadcast.py [target extension] [repeat count] [message]")
        exit(1)

    conn = telnetlib.Telnet("127.0.0.1", 4242)
    conn.read_until(b"OpenBSC> ")

    check_extension(extension)
    check_spam_subscriber()

    for _ in range(repeats):
        spam_number = generate_spam_number()
        send(extension, spam_number, message)
        time.sleep(1)
