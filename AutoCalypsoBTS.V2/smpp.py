#!/usr/bin/env python3
# -*- encoding: UTF-8 -*-
import sqlite3
import logging
import sys
import smpplib.gsm
import smpplib.client
import smpplib.consts

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s %(filename)s:%(lineno)d %(message)s')

HLR_DATABASE = "/root/.osmocom/hlr.sqlite3"

def send_message(client, source, dest, message):
    """Send SMS message using SMPP client"""
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)
    coding = encoding_flag  # Use encoding determined by make_parts

    logging.info(f'Sending SMS "{message}" to {dest}')
    for part in parts:
        pdu = client.send_message(
            msg_type=smpplib.consts.SMPP_MSGTYPE_USERACK,
            source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
            source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            source_addr=source,
            dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
            dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            destination_addr=dest,
            short_message=part,
            data_coding=coding,
            esm_class=msg_type_flag,
            registered_delivery=True,
        )
        logging.debug(f'Sent part: {pdu.sequence}')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./send_bulk_sms.py [FROM] [\"MESSAGE\"]")
        print("Example: ./send_bulk_sms.py MyCompany \"Hello subscribers!\"")
        sys.exit(1)

    source = sys.argv[1]
    message = sys.argv[2]

    # Setup SMPP client
    client = smpplib.client.Client('127.0.0.1', 2775)
    client.set_message_sent_handler(
        lambda pdu: logging.info(f'Sent PDU {pdu.sequence} (ID: {pdu.message_id})'))
    client.set_message_received_handler(
        lambda pdu: logging.info(f'Delivered message {pdu.receipted_message_id}'))

    try:
        client.connect()
        client.bind_transceiver(system_id='OSMO-SMPP', password='1234')
    except Exception as e:
        logging.error(f"Connection failed: {e}")
        sys.exit(1)

    # Fetch subscribers from database
    try:
        db = sqlite3.connect(HLR_DATABASE)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Subscriber")
        subscribers = cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        sys.exit(1)
    finally:
        db.close()

    # Process subscribers and send messages
    for sub in subscribers:
        if not sub[5]:  # MSISDN is in position 5
            logging.warning(f"Subscriber {sub[0]} has no MSISDN")
            continue
            
        msisdn = str(sub[5]).lstrip('+')  # Remove leading '+' if present
        try:
            logging.info(f"Processing subscriber: IMSI={sub[3]}, MSISDN={msisdn}")
            send_message(client, source, msisdn, message)
        except Exception as e:
            logging.error(f"Failed to send to {msisdn}: {e}")

    # Cleanup SMPP connection
    try:
        client.unbind()
        client.disconnect()
    except Exception as e:
        logging.warning(f"Error disconnecting: {e}")

    logging.info("Message sending completed")
