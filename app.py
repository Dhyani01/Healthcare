from flask import Flask, render_template, redirect , url_for
from flask_bootstrap import Bootstrap
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask import request
from flask_cors import CORS,cross_origin
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import scipy.stats as stats
import sklearn
import os
import joblib


file_path = os.path.abspath(os.getcwd())+"\database.db"
app = Flask(__name__)
app.config['SECRET_KEY']='Thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
cors = CORS(app)
Bootstrap(app)
db=SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(15),unique=True)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(80))

@login_manager.user_loader

def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username=StringField('username',validators=[InputRequired(),Length(min=4,max=15)])
    password=PasswordField('password',validators=[InputRequired(),Length(min=8,max=80)])
    remember=BooleanField('rememberme')


class RegisterForm(FlaskForm):
    username=StringField('username',validators=[InputRequired(),Length(min=4,max=15)])
    email=StringField('email',validators=[InputRequired(),Email(message='Invalid Email'),Length(max=50)])
    password=PasswordField('password',validators=[InputRequired(),Length(min=8,max=80)])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login' , methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.password.data)
                return redirect(url_for('dashboard'))
        return '<h1> Invalid Username or Password </h1> '
        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html',form=form)

@app.route('/signup',methods=['GET', 'POST'])
def signup():
    form=RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data,method='sha256')
        new_user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return ' <h1> New User has been Created </h1> ' 
        # return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
    return render_template('signup.html',form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',name=current_user.username)

@app.route('/logout')
@login_required

def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/cardio' , methods=['POST'])
@cross_origin()
def cardio():
    data=request.get_json()
    
    pkl_model =joblib.load("Cardio.pkl")
    x = pd.DataFrame(data,index=[0])    
    # print(x.dtypes)
    x.astype('int')
    x = x.apply(pd.to_numeric)
    x["bmi"] = x["weight"]/((x["height"]/100)**2)
    x["bmi"].astype('float')
    print(x.head())
    a = x[x["gender"]==1]["height"].mean()
    b = x[x["gender"]==2]["height"].mean()
    if a > b:
        gender = "male"
        gender2 = "female"
    else:
        gender = "female"
        gender2 = "male"
    x["gender"] = x["gender"] % 2
    y_predict_sample = pkl_model.predict(x)
    if y_predict_sample[0]==0:
        return jsonify({'result':"You have no Cardiovascular disease as of now"})
    else:
        return jsonify({'result':"You have CardioVascular disease"})

@app.route('/kidney' , methods=['POST'])
@cross_origin()
def kidney():
    data=request.get_json()
    
    pkl_model =joblib.load("kidney_disease.pkl")
    df = pd.DataFrame(data,index=[0])
    print(df.head())
    df[['htn','dm','cad','pe','ane']] = df[['htn','dm','cad','pe','ane']].replace(to_replace={'yes':1,'no':0})
    df[['rbc','pc']] = df[['rbc','pc']].replace(to_replace={'abnormal':1,'normal':0})
    df[['pcc','ba']] = df[['pcc','ba']].replace(to_replace={'present':1,'notpresent':0})
    df[['appet']] = df[['appet']].replace(to_replace={'good':1,'poor':0,'no':np.nan})
    # Further cleaning
    df['pe'] = df['pe'].replace(to_replace='good',value=0) # Not having pedal edema is good
    df['appet'] = df['appet'].replace(to_replace='no',value=0)
    df['cad'] = df['cad'].replace(to_replace='\tno',value=0)
    print(df.dtypes)
    y_predict_sample = pkl_model.predict(df)

    if int(y_predict_sample[0])==0:
        return jsonify({'result':"You have no Kidney disease as of now"})
    else:
        return jsonify({'result':"You have Kidney disease"})



if __name__ == '__main__':
    app.run(debug=True)
