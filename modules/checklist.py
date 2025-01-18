# Checkin Checkout database module for the bot
# K7MHI Kelly Keeton 2024

import sqlite3
from modules.log import *

trap_list_bbs = ("checkin", "checkout", "checklist", "purgein", "purgeout")

def initialize_checklist_database():
    # create the database
    conn = sqlite3.connect('data/checklist.db')
    c = conn.cursor()
    # Check if the checkin table exists, and create it if it doesn't
    c.execute('''CREATE TABLE IF NOT EXISTS checkin
                 (checkin_id INTEGER PRIMARY KEY, checkin_name TEXT, checkin_date TEXT, checkin_time TEXT, checkin_notes TEXT)''')
    # Check if the checkout table exists, and create it if it doesn't
    c.execute('''CREATE TABLE IF NOT EXISTS checkout
                 (checkout_id INTEGER PRIMARY KEY, checkout_name TEXT, checkout_date TEXT, checkout_time TEXT, checkout_notes TEXT)''')
    conn.commit()
    conn.close()
    logger.debug("System: Ensured data/checklist.db exists with required tables")

def checkin(name, date, time, notes):
    # checkin a user
    conn = sqlite3.connect('data/checklist.db')
    c = conn.cursor()
    c.execute("INSERT INTO checkin (checkin_name, checkin_date, checkin_time, checkin_notes) VALUES (?, ?, ?, ?)", (name, date, time, notes))
    conn.commit()
    conn.close()
    return "Checked in: " + name

def delete_checkin(checkin_id):
    # delete a checkin
    conn = sqlite3.connect('data/checklist.db')
    c = conn.cursor()
    c.execute("DELETE FROM checkin WHERE checkin_id = ?", (checkin_id,))
    conn.commit()
    conn.close()
    return "Checkin deleted."

def checkout(name, date, time, notes):
    # checkout a user
    conn = sqlite3.connect('data/checklist.db')
    c = conn.cursor()
    c.execute("INSERT INTO checkout (checkout_name, checkout_date, checkout_time, checkout_notes) VALUES (?, ?, ?, ?)", (name, date, time, notes))
    conn.commit()
    conn.close()
    return "Checked out: " + name

def delete_checkout(checkout_id):
    # delete a checkout
    conn = sqlite3.connect('data/checklist.db')
    c = conn.cursor()
    c.execute("DELETE FROM checkout WHERE checkout_id = ?", (checkout_id,))
    conn.commit()
    conn.close()
    return "Checkout deleted."

def list_checkin():
    # list checkins
    conn = sqlite3.connect('data/checklist.db')
    c = conn.cursor()
    c.execute("""
        SELECT * FROM checkin
        WHERE checkin_id NOT IN (
            SELECT checkin_id FROM checkout
            WHERE checkout_date > checkin_date OR (checkout_date = checkin_date AND checkout_time > checkin_time)
        )
    """)
    rows = c.fetchall()
    conn.close()
    checkin_list = ""
    for row in rows:
        checkin_list += "Checkin ID: " + str(row[0]) + " Name: " + row[1] + " Date: " + row[2] + " Time: " + row[3] + " Notes: " + row[4] + "\n"
    return checkin_list

def handle_checklist(nodeID, message):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")
    # handle checklist commands
    if message[0].lower() == "checkin":
        return checkin(nodeID, date, time, message[1])
    elif message[0].lower() == "checkout":
        return checkout(nodeID, date, time, message[1])
    elif message[0].lower() == "purgein":
        return delete_checkin(nodeID)
    elif message[0].lower() == "purgeout":
        return delete_checkout(nodeID)
    elif message[0].lower() == "checklist":
        return list_checkin()
    else:
        return "Invalid command."