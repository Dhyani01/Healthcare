from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY']='Thisissecret'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////mnt/c/Users/Anurag/Desktop/Major_Project/Healthcare/database.db'
Bootstrap(app)
db=SQLAlchemy(app)

class LoginForm(FlaskForm):
    username=StringField('username',validators=[InputRequired(),Length(min=4,max=15)])
    password=PasswordField('password',validators=[InputRequired(),Length(min=4,max=80)])
    remember=BooleanField('rememberme')


class RegisterForm(FlaskForm):
    username=StringField('username',validators=[InputRequired(),Length(min=4,max=15)])
    email=StringField('email',validators=[InputRequired(),Email(message='Invalid Email'),Length(max=50)])
    password=PasswordField('password',validators=[InputRequired(),Length(min=4,max=80)])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login' , methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return render_template('login.html',form=form)

@app.route('/signup',methods=['GET', 'POST'])
def signup():
    form=RegisterForm()
    if form.validate_on_submit():
        return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
    return render_template('signup.html',form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)