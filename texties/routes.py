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
import os


@app.route('/')
def index():
    return json.dumps({'Error':'Nothing to look here. Move on chump!'})

@app.route('/token')
def token():
    access_token = create_access_token(identity="test")
    response = json.dumps({'success':True, 'access_token':access_token}), 200, {'ContentType':'application/json'}
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response



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
                print(e)
                resp.message("Hmm, that was weird. Let me try to fix that. 🧰")
        else:
            resp.message("Hmm, textie i don't understand 😕. \n Here are the commands i understand for now (note, weight, reminder, idea)")
    except Exception as e:
        resp.message("Looks like I am having some issues textie. Let's try later 🥺")

    return str(resp)


@app.route("/add", methods=['GET', 'POST'])
def add():
    try:
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_number.strip()
        if(phone_number==None or len(phone_number)==4):
            redirect(url_for('index'))
        elif(phone_number[0]=='1'):
            phone_number = "+"+phone_number
        elif(phone_number[0]!='1' and phone_number[0]!='+' and len(phone_number)!=4):
            phone_number = "+1"+phone_number
        body = str(request.args.get('textie'))
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 400, {'ContentType':'application/json'}
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
                print(e)
                return json.dumps({'success':False}), 500, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False, 'error':'Command not found'}), 403, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'success':False, 'error':'Something went wrong' }), 403, {'ContentType':'application/json'}




@app.route("/auth", methods=['GET', 'POST'])
def auth():
    try:
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_number.strip()
        if(phone_number==None or len(phone_number)==4):
            redirect(url_for('index'))
        elif(phone_number[0]=='1'):
            phone_number = "+"+phone_number
        elif(phone_number[0]!='1' and phone_number[0]!='+' and len(phone_number)!=4):
            phone_number = "+1"+phone_number
        auth_code = str(random.randint(1111,9999))
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 400, {'ContentType':'application/json'}
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
            return json.dumps({'success':False, 'Error': e+" Error in sending message", }), 500, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'success':False, 'Error': e+" Error in adding auth code to database"}), 500, {'ContentType':'application/json'}
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/auth_check", methods=['GET','POST'])
def auth_check():
    try:
        auth_code= str(request.args.get('auth_code'))
        auth_code = auth_code.strip()
        auth_phone_number=str(request.args.get('phone_number'))
        auth_phone_number = auth_phone_number.strip()
        if(auth_phone_number==None or len(auth_phone_number)==4):
            return json.dumps({'success':False, 'Error': "Phone number not entered"}), 400, {'ContentType':'application/json'}
        elif(auth_phone_number[0]=='1'):
            auth_phone_number = "+"+auth_phone_number
        elif(auth_phone_number[0]!='1' and auth_phone_number[0]!='+' and len(auth_phone_number)!=4):
            auth_phone_number = "+1"+auth_phone_number
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 400, {'ContentType':'application/json'}
    try:
        response = AuthenticationTable.query.filter_by(phone_number=auth_phone_number).order_by(AuthenticationTable.id.desc()).all()
        if(str(response[0].auth_code) ==  auth_code):
            access_token = create_access_token(identity="test")
            return json.dumps({'success':True, 'access_token':access_token}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False, 'Error': 'Auth Code Incorrect'}), 403, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}


@app.route("/get", methods=['GET', 'POST'])
def get_weight():
    try:
        type=request.args.get('type')
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_number.strip()
        if(phone_number==None or len(phone_number)==4):
            redirect(url_for('index'))
        elif(phone_number[0]=='1'):
            phone_number = "+"+phone_number
        elif(phone_number[0]!='1' and phone_number[0]!='+' and len(phone_number)!=4):
            phone_number = "+1"+phone_number
        all_texties = Texties.query.filter_by(textie_type=type, phone_number=phone_number).all()
        result = texties_schema.dump(all_texties)
        return jsonify(result)
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}

@app.route("/search", methods=['GET', 'POST'])
def search():
    try:
        type=request.args.get('type')
        search_text=request.args.get('search_text')
        phone_number=str(request.args.get('phone_number'))
        phone_number = phone_number.strip()
        if(phone_number==None or len(phone_number)==4):
            redirect(url_for('index'))
        elif(phone_number[0]=='1'):
            phone_number = "+"+phone_number
        elif(phone_number[0]!='1' and phone_number[0]!='+' and len(phone_number)!=4):
            phone_number = "+1"+phone_number

        all_texties = Texties.query.filter(Texties.textie.contains(search_text)).filter_by(textie_type=type, phone_number=phone_number).all()
        result = texties_schema.dump(all_texties)
        return jsonify(result)
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}

@app.route("/delete_texties", methods=['GET','TYPE'])
def delete_texties():
    delete_key_args=request.args.get('delete_key')
    delete_key = os.environ.get("DELETE_KEY")
    if delete_key_args == delete_key:
        try:
            returned = Texties.query.delete()
            print(returned)
            return json.dumps({'success':True, returned:{jsonify(returned)}}), 200, {'ContentType':'application/json'}
        except Exception as e:
            print(e)
            return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False, 'Error': "Incorrect Delete Key"}), 403, {'ContentType':'application/json'}

@app.route("/delete", methods=['GET','POST'])
def delete():
    try:
        delete_id=int(request.args.get('id'))
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 403, {'ContentType':'application/json'}
    try:
        returned = Texties.query.filter_by(id=delete_id).first()
        db.session.delete(returned)
        db.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}


@app.route("/update", methods=['GET','POST'])
def update():
    try:
        update_id=request.args.get('id')
        update_textie=request.args.get('textie')
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 403, {'ContentType':'application/json'}
    try:
        resp = Texties.query.filter_by(id=update_id).first()
        resp.textie = update_textie
        db.session.commit()
        return json.dumps({'success':True, 'snackBar':"Textie Updated"}), 200, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}



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
            print(e)
            return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':False, 'Error': "Incorrect Delete Key"}), 403, {'ContentType':'application/json'}
