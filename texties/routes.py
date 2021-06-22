from texties.models import Texties, AuthenticationTable
from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import random
from texties import app
from texties import db, client
from texties.models import texties_schema, authentications_schema
import json 

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
            return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


##Works with data query on id but not phone number try using as an int maybe,
# once it works with phone number just route to the link unsafely
# Next step is to create a session or another secure way of login people in
@app.route("/auth_check", methods=['GET','POST'])
def auth_check():
    try:
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
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 400, {'ContentType':'application/json'}
    try:
        response = AuthenticationTable.query.filter_by(phone_number=auth_phone_number).order_by(AuthenticationTable.id.desc()).all()
        if(str(response[0].auth_code) ==  auth_code):
            phone_number = auth_phone_number
            session['phone_number'] = phone_number
            if "type" in session:
                pass
            else:
                session["type"] = "note"
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False, 'Error': 'Auth Code Incorrect'}), 403, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'success':False, 'Error': e}), 500, {'ContentType':'application/json'}


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
                redirect(url_for('index'))
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
        