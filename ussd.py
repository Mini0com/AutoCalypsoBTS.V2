#!/usr/bin/env python3
import sqlite3
import telnetlib
import sys
import time

HLR_DATABASE = "/root/.osmocom/hlr.sqlite3"
IMSI_SENDER = "999999999999999"  # Sender's IMSI (adjust if needed)

def check_subscriber(imsi, conn):
    """Ensure the sender IMSI exists in OpenBSC."""
    conn.write(f"show subscriber imsi {imsi}\n".encode())
    res = conn.read_until(b"OpenBSC> ")
    if b"No subscriber found for imsi" in res:
        conn.write(f"subscriber create imsi {imsi}\n".encode())
        conn.read_until(b"OpenBSC> ")

def send_silent_sms(msisdn):
    """Send 2 silent SMS to a subscriber (hidden output)."""
    try:
        conn = telnetlib.Telnet("127.0.0.1", 4242)
        conn.read_until(b"OpenBSC> ")
        check_subscriber(IMSI_SENDER, conn)

        # Send two silent SMS with minimal output
        for _ in range(2):
            cmd = f"subscriber extension {msisdn} silent-sms sender imsi {IMSI_SENDER} send .SILENT\n"
            conn.write(cmd.encode())
            conn.read_until(b"OpenBSC> ")
        
        return True
    except:
        return False
    finally:
        try:
            conn.close()
        except:
            pass

def send_ussd_message(msisdn, ussd_type, message):
    """Send USSD notification with status-only output."""
    try:
        conn = telnetlib.Telnet("127.0.0.1", 4242)
        conn.read_until(b"OpenBSC> ")
        check_subscriber(IMSI_SENDER, conn)

        cmd = f'subscriber extension {msisdn} ussd-notify {ussd_type} "{message}"\n'
        conn.write(cmd.encode())
        res = conn.read_until(b"OpenBSC> ")
        
        # Simplified status check
        if b"%" in res:
            print(f"USSD failed: {msisdn}")
            return False
        else:
            print(f"USSD success: {msisdn}")
            return True
    except:
        print(f"USSD failed: {msisdn}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./send_ussd_all.py [ussd-type] [\"message\"]")
        sys.exit(1)

    ussd_type = sys.argv[1]
    message = sys.argv[2]

    # Fetch all subscribers
    db = sqlite3.connect(HLR_DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Subscriber")
    subscribers = cursor.fetchall()
    db.close()

    valid_subscribers = []
    
    # Silent SMS phase (no output)
    for sub in subscribers:
        msisdn = sub[5]
        if msisdn and str(msisdn).isdigit():
            if send_silent_sms(msisdn):
                valid_subscribers.append(msisdn)
            time.sleep(0.2)

    # System pause
    time.sleep(3)

    # USSD phase (only success/failure)
    print("\nUSSD Delivery Results:")
    for msisdn in valid_subscribers:
        send_ussd_message(msisdn, ussd_type, message)
        time.sleep(0.2)
