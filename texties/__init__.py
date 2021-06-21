# -*- coding: utf-8 -*-
from typing import Text
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from os.path import join, dirname
from flask_marshmallow import Marshmallow
from twilio.rest import Client
from flask_cors import CORS




app = Flask(__name__)
CORS(app)
app.secret_key = "supersecshrlweifjhgaslihgfsghas35465454654sd6gf54s6f5g4s6f5gretkey"
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

from texties import routes