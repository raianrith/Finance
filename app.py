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
from twilio.rest import Client
import random




app = Flask(__name__)
app.secret_key = "supersecretkey"
#If sms is received twilio will hit this function with the message
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

account_sid = 'ACa8d0cb233f2f43304aab97b8f4e52f8e'
auth_token = '44cfcd02cd6a78664cdc215f079bc65a'
client = Client(account_sid, auth_token)


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

class AuthenticationTable(db.Model):
    __tablename__='auth_table'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(50))
    auth_code = db.Column(db.String(600))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


    def __init__(self, auth_code, phone_number):
        self.auth_code = auth_code
        self.phone_number = phone_number

class AuthenticationTableSchema(marsh.Schema):

    class Meta:
        fields = ('id','phone_number','auth_code','created_date')

authentications_schema =  AuthenticationTableSchema( many = True)
authentication_schema = AuthenticationTableSchema()
class TextiesSchema(marsh.Schema):
    class Meta:
        fields = ('id','textie_type','textie','phone_number','created_date')

texties_schema =  TextiesSchema( many = True)
textie_schema = TextiesSchema()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/authenticate')
def authenticate():
    return render_template("auth.html")


commands_list = ['weight','note','idea','reminder']
positive_emojis=['🙌','📝','🎉','🥳','👯','🎊','🤪','👌']
random_positive_emoji= random.randint(0,len(positive_emojis)-1)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
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
## Finish this auth function
# Person fills index.html form
# Redirect to auth page and send sms with code to their phone
# Collect sms code and if code matches the latest one sent to the number in database return the textie_type associated with phone number
@app.route("/auth", methods=['GET', 'POST'])
def auth():
    type=request.args.get('type')
    session["type"] = str(type)
    phone_number=str(request.args.get('phone_number'))
    phone_number = phone_number.strip()
    if(phone_number==None or len(phone_number)==4):
        phone_number = '+19206369355'
    elif(phone_number[0]=='1'):
        phone_number = "+"+phone_number
    elif(phone_number[0]!='1' and phone_number[0]!='+' and len(phone_number)!=4):
        phone_number = "+1"+phone_number
    auth_code = str(random.randint(1111,9999))
    try:
        data = AuthenticationTable(auth_code,phone_number)
        db.session.add(data)
        db.session.commit()
        try:
            message = client.messages.create(
                              body=auth_code,
                              from_='+15126050927',
                              to=phone_number
                          )
        except Exception as e:
            print("Error in sending auth code to client")
    except Exception as e:
        print(e)
        print("Error in creating auth code in Database")
    return render_template("auth.html")


##Works with data query on id but not phone number try using as an int maybe,
# once it works with phone number just route to the link unsafely
# Next step is to create a session or another secure way of loggin people in
@app.route("/auth_check", methods=['GET','POST'])
def auth_check():
    auth_code= str(request.args.get('auth_code'))
    auth_code = auth_code.strip()
    auth_phone_number=str(request.args.get('phone_number'))
    auth_phone_number = auth_phone_number.strip()
    if(auth_phone_number==None or len(auth_phone_number)==4):
        return("<h3>PLEASE ENTER A PHONE NUMBER")
    elif(auth_phone_number[0]=='1'):
        auth_phone_number = "+"+auth_phone_number
    elif(auth_phone_number[0]!='1' and auth_phone_number[0]!='+' and len(auth_phone_number)!=4):
        auth_phone_number = "+1"+auth_phone_number
    try:
        # print('phone number',auth_phone_number)
        # print('auth_code',auth_code)
        response = AuthenticationTable.query.filter_by(phone_number=auth_phone_number).order_by(AuthenticationTable.id.desc()).all()
        # print('database auth_code',response[len(response)])
        # print("I just fetched this", response)
        # print(response)
        print(response[0].auth_code)
        print(auth_code)
        if(str(response[0].auth_code) ==  auth_code):
            print("Passed auth check")
            phone_number = auth_phone_number
            session['phone_number'] = phone_number
            if "type" in session:
                pass
            else:
                session["type"] = "note"
            return redirect(url_for("get_texties"))
        else:
            print("failed Auth check")
            return render_template("fail.html")
    except Exception as e:
        print(e)
        print("error in fetching auth code from database")
    print("why am i here?")
    return "I got this far but why?"

@app.route("/get/texties", methods=['GET', 'POST'])
def get_texties():
    try:
        
        if "phone_number" in session:
            phone_number = session["phone_number"]
            type = session["type"]
        else:
            type=request.args.get('type')
            phone_number=str(request.args.get('phone_number'))
            phone_number = phone_number.strip()
            if(phone_number==None or len(phone_number)==4):
                phone_number = '+19206369355'
            elif(phone_number[0]=='1'):
                phone_number = "+"+phone_number
            elif(phone_number[0]!='1' and phone_number[0]!='+' and len(phone_number)!=4):
                phone_number = "+1"+phone_number
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