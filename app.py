# -*- coding: utf-8 -*-
from typing import Text
from twilio.rest import Client
from flask import Flask, Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from flask_sqlalchemy import SQLAlchemy
import datetime
import random
from dotenv import load_dotenv
import os
from os.path import join, dirname
from flask_marshmallow import Marshmallow

app = Flask(__name__)
#If sms is received twilio will hit this function with the message
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DEV_DATABASE_URL")
else:
    app.debug=False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://egvyaqyigaujuu:0f852e4602daf4f86ceb0919aa6510631585c97b4ecf2cf7ef9fae02516f6a38@ec2-54-158-232-223.compute-1.amazonaws.com:5432/d8k8274ljhv05'
db = SQLAlchemy(app)
marsh = Marshmallow(app)
class Texties(db.Model):
    __tablename__='texties_table'
    id = db.Column(db.Integer, primary_key=True)
    textie_type = db.Column(db.String(50))
    textie = db.Column(db.String(600))
    phone_number = db.Column(db.String(15))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


    def __init__(self, textie, textie_type, phone_number):
        self.textie = textie
        self.textie_type = textie_type
        self.phone_number = phone_number

class TextiesSchema(marsh.Schema):
    class Meta:
        fields = ('id','textie_type','textie','phone_number','created_date')

texties_schema =  TextiesSchema( many = True)
textie_schema = TextiesSchema()

@app.route('/')
def index():
    return render_template("index.html")


commands_list = ['weight','note','idea','reminder']
positive_emojis=['🙌','📝','🎉','🥳','👯','🎊','🤪','👌']
random_positive_emoji= random.randint(0,len(positive_emojis)-1)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    print(random_positive_emoji)
    body = request.values.get('Body', None)
    phone_number = request.values.get('From', None)
    resp = MessagingResponse()
    try:
        body_split = body.split(':')
        if(len(body_split)<2):
            command = "none"
        else:
            command = body_split[0]
            command = command.strip()
            command = command.lower()
            command_body = body_split[1]
        if command in commands_list:
            #save weight
            try:
                textie = str(command_body)
                textie_type = command
                data = Texties(textie, textie_type, phone_number)
                db.session.add(data)
                db.session.commit()
                resp.message("Your "+ command+" has been recorded "+positive_emojis[random_positive_emoji])
            except Exception as e:
                print(e)
                resp.message("Hmm, that was weird. Let me try to fix that. 🧰")
        else:
            resp.message("Hmm, textie i don't understand 😕. \n Here are the commands i understand for now (note, weight, reminder, idea)")
    except Exception as e:
        resp.message("Looks like I am having some issues textie. Let's try later 🥺")

    return str(resp)


@app.route("/get/texties", methods=['GET', 'POST'])
def get_texties():
    try:
        type=request.args.get('type')
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_number.strip()
        if(phone_number==None or len(phone_number)==4):
            phone_number = '+19206369355'
        elif(phone_number[0]=='1'):
            phone_number = "+"+phone_number
        elif(phone_number[0]!='1' and phone_number[0]!='+' and len(phone_number)!=4):
            phone_number = "+1"+phone_number
        print('phone number =',phone_number)
        all_texties = Texties.query.filter_by(textie_type=type,phone_number=phone_number).all()
        result = texties_schema.dump(all_texties)
        return jsonify(result)
    except Exception as e:
        print(e)
        return ("error fetching",type)

@app.route("/get/weight", methods=['GET', 'POST'])
def get_weight():
    try:
        all_texties = Texties.query.filter_by(textie_type='weight').all()
        result = texties_schema.dump(all_texties)
        return jsonify(result)
    except Exception as e:
        print(e)
        return "error fetching weights"
    
@app.route("/get/notes", methods=['GET', 'POST'])
def get_notes():
    try:
        all_texties = Texties.query.filter_by(textie_type='note').all()
        result = texties_schema.dump(all_texties)
        return jsonify(result)
    except Exception as e:
        print(e)
        return "error fetching notes"

@app.route("/get/ideas", methods=['GET', 'POST'])
def get_ideas():
    try:
        all_texties = Texties.query.filter_by(textie_type='idea').all()
        result = texties_schema.dump(all_texties)
        return jsonify(result)
    except Exception as e:
        print(e)
        return "error fetching ideas"
        

if __name__ == "__main__":
    app.run()