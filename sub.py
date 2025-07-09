#!/usr/bin/env python3
import os
import sys
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HLR_DATABASE = os.path.join(BASE_DIR, "hlr.sqlite3")

# IMSI prefix to country/network lookup
IMSI_PREFIXES = {
    "60600": ("Libya", "Libyana"),
    "60601": ("Libya", "Almadar"),
    "310260": ("USA", "T-Mobile"),
    "310410": ("USA", "AT&T"),
    "23430": ("UK", "T-Mobile UK"),
    "23415": ("UK", "Vodafone UK"),
    "26201": ("Germany", "Telekom"),
    "26202": ("Germany", "Vodafone DE"),
    "20801": ("France", "Orange"),
    "20810": ("France", "SFR"),
    "60603": ("Libya",  "LibyaPhone"),
    # Extend as needed
}

def detect_country_network(imsi):
    if not imsi:
        return "Unknown", "Unknown"
    for prefix in sorted(IMSI_PREFIXES.keys(), key=len, reverse=True):
        if str(imsi).startswith(prefix):
            return IMSI_PREFIXES[prefix]
    return "Unknown", "Unknown"

def main():
    if not os.path.isfile(HLR_DATABASE):
        sys.stderr.write(f"ERROR: database file not found at {HLR_DATABASE}\n")
        sys.exit(1)

    try:
        db = sqlite3.connect(HLR_DATABASE)
    except sqlite3.OperationalError as e:
        sys.stderr.write(f"ERROR: could not open database: {e}\n")
        sys.exit(1)

    c = db.cursor()

    c.execute("""
        SELECT
            s.id,
            s.imsi,
            s.extension AS msisdn,
            e.imei,
            s.tmsi,
            s.created
        FROM Subscriber AS s
        LEFT JOIN Equipment AS e ON s.id = e.id
        ORDER BY s.id
    """)

    rows = c.fetchall()
    if not rows:
        print("No subscribers found.")
    else:
        # Aligned header
        print(
            f"{'ID':<4}{'IMSI':<18}{'MSISDN':<15}{'IMEI':<18}"
            f"{'TMSI':<12}{'Timestamp':<22}{'Country':<10}{'Network':<15}"
        )
        print("-" * 114)

        for sid, imsi, msisdn, imei, tmsi, created in rows:
            country, network = detect_country_network(imsi)
            print(
                f"{str(sid):<4}{str(imsi or ''):<18}{str(msisdn or ''):<15}{str(imei or ''):<18}"
                f"{str(tmsi or ''):<12}{str(created or 'N/A'):<22}{country:<10}{network:<15}"
            )

    db.close()

if __name__ == "__main__":
    main()