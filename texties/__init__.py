# -*- coding: utf-8 -*-
# from typing import Text
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from os.path import join, dirname
from flask_marshmallow import Marshmallow
from twilio.rest import Client
from flask_cors import CORS
from pymongo import MongoClient




app = Flask(__name__)


client = MongoClient('mongodb+srv://raianrith83:hXj5iWEI4NOnq0HF@cluster0.2hkhltm.mongodb.net/?retryWrites=true&w=majority')

db = client.Finance_App
collection = db.Finance_App_Data

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
#jwt = JWTManager(app)

CORS(app)
app.secret_key = os.environ['APP_SECRET_KEY']

#If sms is received twilio will hit this function with the message
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Load the Twilio configuration from the environment variables
account_sid = os.environ['ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

# Load DEV/PROD configuration from the environment variables
ENV = os.environ['APP_ENV']
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DEV_DATABASE_URL")
else:
    app.debug=False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
#db = SQLAlchemy(app)
#marsh = Marshmallow(app)

from texties import routes

