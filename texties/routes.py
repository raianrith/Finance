
from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import random
from texties import app
from texties import db, client
import json 
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException
import re
import os
from texties import collection


commands_list = ['weight','note','idea','reminder']
positive_emojis=['🙌','📝','🎉','🥳','👯','🎊','🤪','👌']
random_positive_emoji= random.randint(0,len(positive_emojis)-1)
phone_num_regex=re.compile(r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))')


#General Error handler
@app.errorhandler(HTTPException)
def return_error(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


#Check phone number validity and change it to E.164 format
def phone_check(number):
    number=number.strip()
    number=(re.sub('[^A-Za-z0-9]+','',number))
    if(number[0]=='1'and len(number)==11):
        number = number[1:]
    if phone_num_regex.match(number) and len(number)==10:
        return "+1"+number
    else:
        return False


@app.route('/')
def index():
    collection.insert_one({'ss':'Nothing to look here. Move on chump!'})
    return json.dumps({'Error':'Nothing to look here. Move on chump!'})

@app.route('/twilio_test')
def index():
    collection.insert_one({'twilio':'Nothing to look here. Move on chump!'})
    return json.dumps({'Error':'Nothing to look here. Move on chump!'})


# Save a textie along with its type
@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    body = request.values.get('Body', None)
    phone_number = request.values.get('From', None)
    phone_number = phone_check(phone_number)
    if phone_number==False:
            return json.dumps({'success':False, 'error':'Invalid phone number format'}), 403, {'ContentType':'application/json'}
    resp = MessagingResponse()
    try:
        body_split = body.split(':')
        if(len(body_split)<2):
            command = "note"
            command_body = body
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
                resp.message("Your "+ command+" has been recorded "+positive_emojis[random_positive_emoji])
            except Exception as e:
                resp.message("Hmm, that was weird. Let me try to fix that. 🧰")
        else:
            resp.message("Hmm, textie i don't understand 😕. \n Here are the commands i understand for now (note, weight, reminder, idea)")
    except Exception as e:
        resp.message("Looks like I am having some issues textie. Let's try later 🥺")

    return str(resp)



# Get a type of textie
@app.route("/get", methods=['GET', 'POST'])
def get_weight():
    try:
        type=request.args.get('type')
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_check(phone_number)
        if phone_number==False:
            return json.dumps({'success':False, 'error':'Invalid phone number format'}), 403, {'ContentType':'application/json'}
        return jsonify(result)
    except Exception as e:
        return return_error(e)
