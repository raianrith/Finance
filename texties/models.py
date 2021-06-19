from texties import db, marsh
import datetime

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


class TextiesSchema(marsh.Schema):
    class Meta:
        fields = ('id','textie_type','textie','phone_number','created_date')

texties_schema =  TextiesSchema( many = True)
textie_schema = TextiesSchema()
authentications_schema =  AuthenticationTableSchema( many = True)
authentication_schema = AuthenticationTableSchema()