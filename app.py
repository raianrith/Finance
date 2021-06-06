# -*- coding: utf-8 -*-
import os
import sqlite3
from twilio.rest import Client
from flask import Flask, Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)
#If sms is received twilio will hit this function with the message

DATABASE = './data.db'




@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    body = request.values.get('Body', None)
    # phone_number = request.values.get('from', None)
    resp = MessagingResponse()
    try:
        body_split = body.split(':')
        if(len(body_split)<2):
            command = "none"
        else:
            command = body_split[0]
            command = command.strip()
            command_body = body_split[1]
        if command == "weight" or command == "Weight":
            #save weight
            try:
                
                conn = get_db()
                cur = conn.cursor()
                weight_in_lbs = command_body
                weight_in_lbs = 100
                phone_number = 200
                cur.execute('INSERT INTO weights (id, weight) VALUES(?,?)',(phone_number, weight_in_lbs))
                conn.commit()
                resp.message("Your weight has been recorded 🙌")
                
            except Exception as e:
                print(e)
                resp.message("Hmm, that was weird. Let me try to fix that. 🧰")
        elif command == "note" or command == "Note":
            #save note
            try:
                conn = get_db()
                cur = conn.cursor()
                note = command_body
                phone_number = 3125090234
                cur.execute('INSERT INTO notes (id, note) VALUES(?,?)',(phone_number, note))
                conn.commit()
                resp.message("Your note has been saved 📝")
            except Exception as e:
                print(e)
                resp.message("Hmm, that was weird. Let me try to fix that. 🧰")
        else:
            resp.message("Hmm, textie i don't understand 😕")
    except Exception as e:
        resp.message("Looks like I am having some issues textie. Let's try later 🥺")

    return str(resp)

@app.route("/get/weight", methods=['GET', 'POST'])
def get_weight():
    cur = get_db().cursor()
    cur.execute('SELECT * from weights')
    rows = cur.fetchall()
    weights = ""
    for row in rows:
        weights = weights + "Phone number = "+str(row[1])+" weight = "+str(row[2]) + "\n"
    print(weights)
    return weights
        


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
# def process_weight(command_body):
#     print(command_body)
#     reponse = "not set"
#     try:
#         response = "Your weight has been recorded 🙌"
#     except Exception as e:
#         response = "Looks like I am having issues recording your weight.\nI'm sorry textie 😞"
#     return reponse

