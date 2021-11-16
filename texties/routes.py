from texties.models import Texties, AuthenticationTable
from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import random
from texties import app, jwt
from texties import db, client
from texties.models import texties_schema, authentications_schema
import json 
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException
import re
import os


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



def custom_error(code, description):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    
    # replace the body with JSON
    data = json.dumps({
        "code": code,
        "description": description,
    })
    content_type = "application/json"
    return json.dumps({data}, {content_type})


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
    return json.dumps({'Error':'Nothing to look here. Move on chump!'})

#Return access token
@app.route('/token')
def token():
    access_token = create_access_token(identity="test")
    response = json.dumps({'success':True, 'access_token':access_token}), 200, {'ContentType':'application/json'}
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Save a textie along with its type
@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    body = request.values.get('Body', None)
    phone_number = request.values.get('From', None)
    phone_number = phone_check(phone_number)
    if phone_number==False:
            return custom_error(403, "Invalid phone number format")
            # return json.dumps({'success':False, 'error':'Invalid phone number format'}), 403, {'ContentType':'application/json'}
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
                data = Texties(textie, textie_type, phone_number)
                db.session.add(data)
                db.session.commit()
                resp.message("Your "+ command+" has been recorded "+positive_emojis[random_positive_emoji])
            except Exception as e:
                resp.message("Hmm, that was weird. Let me try to fix that. 🧰")
        else:
            resp.message("Hmm, textie i don't understand 😕. \n Here are the commands i understand for now (note, weight, reminder, idea)")
    except Exception as e:
        resp.message("Looks like I am having some issues textie. Let's try later 🥺")

    return str(resp)

# Add textie for web app
@app.route("/add", methods=['GET', 'POST'])
def add():
    try:
        body = str(request.args.get('textie'))
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_check(phone_number)
        if phone_number==False:
            return json.dumps({'success':False, 'error':'Invalid phone number format'}), 403, {'ContentType':'application/json'}
    except Exception as e:
        return return_error(e)
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
            try:
                textie = str(command_body)
                textie_type = command
                data = Texties(textie, textie_type, phone_number)
                db.session.add(data)
                db.session.commit()
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
            except Exception as e:
                return return_error(e)
        else:
            return return_error(e)
    except Exception as e:
        return return_error(e)



# Check phone number and send auth code
@app.route("/auth", methods=['GET', 'POST'])
def auth():
    try:
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_check(phone_number)
        if phone_number==False:
            return json.dumps({'success':False, 'error':'Invalid phone number format'}), 403, {'ContentType':'application/json'}
        auth_code = str(random.randint(1111,9999))
    except Exception as e:
        return return_error(e)
    try:
        data = AuthenticationTable(auth_code,phone_number)
        db.session.add(data)
        db.session.commit()
        try:
            auth_code = "Here is your Authentication Code: "+auth_code
            message = client.messages.create(
                              body=auth_code,
                              from_='+15126050927',
                              to=phone_number
                          )
        except Exception as e:
            return return_error(e)
    except Exception as e:
        return return_error(e)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

# Check auth code against database for phone number
@app.route("/auth_check", methods=['GET','POST'])
def auth_check():
    try:
        auth_code= str(request.args.get('auth_code'))
        auth_code = auth_code.strip()
        auth_phone_number=str(request.args.get('phone_number'))
        auth_phone_number = phone_check(auth_phone_number)
        if auth_phone_number==False:
            return json.dumps({'success':False, 'error':'Invalid phone number format'}), 403, {'ContentType':'application/json'}
    except Exception as e:
        return return_error(e)
    try:
        response = AuthenticationTable.query.filter_by(phone_number=auth_phone_number).order_by(AuthenticationTable.id.desc()).all()
        if(str(response[0].auth_code) ==  auth_code):
            access_token = create_access_token(identity="test")
            return json.dumps({'success':True, 'access_token':access_token}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False, 'Error': 'Auth Code Incorrect'}), 403, {'ContentType':'application/json'}
    except Exception as e:
        return return_error(e)

# Get a type of textie
@app.route("/get", methods=['GET', 'POST'])
def get_weight():
    try:
        type=request.args.get('type')
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_check(phone_number)
        if phone_number==False:
            return json.dumps({'success':False, 'error':'Invalid phone number format'}), 403, {'ContentType':'application/json'}
        all_texties = Texties.query.filter_by(textie_type=type, phone_number=phone_number).all()
        result = texties_schema.dump(all_texties)
        return jsonify(result)
    except Exception as e:
        return return_error(e)

@app.route("/signup",methods=['GET','POST'])
def signup():
    try:
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_check(phone_number)
        if phone_number==False:
            return json.dumps({'success':False, 'error':'Invalid phone number format'}), 403, {'ContentType':'application/json'}
        try:
            # welcome_message="hey"
            welcome_message = "Welcome to texties! \nYou can save your notes by texting me anytime. To learn more reply with --help"
            message = client.messages.create(
                                body=welcome_message,
                                from_='+15126050927',
                                to=phone_number
                            )
            samples = 'Here are some sample texts you can send me.\n\n\nnote: Return library card\n\nidea: Create a meowCoin 🐈🪙\n\nweight: 145lbs'
            message = client.messages.create(
                                body=samples,
                                from_='+15126050927',
                                to=phone_number
                            )
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        except Exception as e:
            return return_error(e)
    except Exception as e:
        return return_error(e)



# Search for a type of textie
@app.route("/search", methods=['GET', 'POST'])
def search():
    try:
        type=request.args.get('type')
        search_text=request.args.get('search_text')
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_check(phone_number)
        if phone_number==False:
            return json.dumps({'success':False, 'error':'Invalid phone number format'}), 403, {'ContentType':'application/json'}
        all_texties = Texties.query.filter(Texties.textie.contains(search_text)).filter_by(textie_type=type, phone_number=phone_number).all()
        result = texties_schema.dump(all_texties)
        return jsonify(result)
    except Exception as e:
        return return_error(e)

# Delete a textie from the database
@app.route("/delete_texties", methods=['GET','TYPE'])
def delete_texties():
    delete_key_args=request.args.get('delete_key')
    delete_key = os.environ['DELETE_KEY']
    if delete_key_args == delete_key:
        try:
            returned = Texties.query.delete()
            print(returned)
            return json.dumps({'success':True, returned:{jsonify(returned)}}), 200, {'ContentType':'application/json'}
        except Exception as e:
            return return_error(e)
    else:
        return json.dumps({'success':False, 'Error': "Incorrect Delete Key"}), 403, {'ContentType':'application/json'}

# Delete a textie from database
@app.route("/delete", methods=['GET','POST'])
def delete():
    try:
        delete_id=int(request.args.get('id'))
    except Exception as e:
        return return_error(e)
    try:
        returned = Texties.query.filter_by(id=delete_id).first()
        db.session.delete(returned)
        db.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except Exception as e:
        return return_error(e)

# Update a textie in the database
@app.route("/update", methods=['GET','POST'])
def update():
    try:
        update_id=request.args.get('id')
        update_textie=request.args.get('textie')
    except Exception as e:
        return return_error(e)
    try:
        resp = Texties.query.filter_by(id=update_id).first()
        resp.textie = update_textie
        db.session.commit()
        return json.dumps({'success':True, 'snackBar':"Textie Updated"}), 200, {'ContentType':'application/json'}
    except Exception as e:
        return return_error(e)


# Delete auth codes from the database
@app.route("/delete_authentication", methods=['GET','TYPE'])
def delete_authentication():
    delete_key_args=request.args.get('delete_key')
    delete_key = os.environ.get("DELETE_KEY")
    if delete_key_args == delete_key:
        try:
            returned = AuthenticationTable.query.delete()
            print(returned)
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        except Exception as e:
            return return_error(e)
    else:
        return json.dumps({'success':False, 'Error': "Incorrect Delete Key"}), 403, {'ContentType':'application/json'}
