from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, SelectField, EmailField
from wtforms.validators import InputRequired, Length, Regexp, EqualTo, ValidationError
from passlib.hash import pbkdf2_sha256
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import db, users
import os

auth = Blueprint('auth', __name__)


def check_username(form, field):
    usercheck = users.query.filter_by(username=form.username.data).first()
    if usercheck:
        raise ValidationError("Username already exists. Select a different username")
    
def check_usercaps(form, field):
    if any(c.isupper() for c in field.data):
        raise ValidationError("Username cannot contain capital letters.")

def check_email(form, field):
    emailcheck = users.query.filter_by(email=form.email.data).first()
    if emailcheck:
        raise ValidationError("This email is already registered. Login or use a different email")

def login_check(form, field):
    user = users.query.filter((users.username == form.username.data) | (users.email == form.username.data)).first()
    if not user or not pbkdf2_sha256.verify(field.data, user.password):
        raise ValidationError('Username or password is incorrect')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=5, max=100)], render_kw={"placeholder": "Enter your username or email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=50), login_check], render_kw={"placeholder": "Enter your password"})
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    fullname = StringField('Full Name', validators=[InputRequired(), Length(max=100), Regexp(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", message="Full Name must contain only letters, spaces, hyphens, or apostrophes")], render_kw={"placeholder": "Enter your Full Name"})
    email = EmailField('Email', validators=[InputRequired(), Length(max=100), check_email], render_kw={"placeholder": "Enter your Email"})
    username = StringField('Username', validators=[InputRequired(), Length(min=5, max=12), Regexp('^\w+$', message="Username must contain only letters, numbers, or underscores"), check_username, check_usercaps], render_kw={"placeholder": "Create username"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=50), EqualTo('confirm', message='Passwords must match')], render_kw={"placeholder": "Create password"})
    confirm = PasswordField('Repeat Password', validators=[InputRequired(), Length(min=8, max=50)], render_kw={"placeholder": "Confirm Password"})
    dob = DateField('Date of Birth', validators=[InputRequired()], render_kw={'max': date.today() - relativedelta(years=15)})
    gender = SelectField(u'Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])


@auth.route('/login', methods=["GET", "POST"])
def login():
    logout_user()
    form = LoginForm()

    if form.validate_on_submit():
        user = users.query.filter_by(username=form.username.data).first()

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))

        if not user:
            user = users.query.filter_by(email=form.username.data).first()
            if user and pbkdf2_sha256.verify(form.password.data, user.password):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))
    
    return render_template('login.html', form=form)



@auth.route('/register', methods=["GET", "POST"])
def register():
    logout_user()
    form = RegisterForm()
    default_bio = 'No bio yet'
    
    if form.validate_on_submit():
        pw_hash = pbkdf2_sha256.hash(form.password.data)

        folderPath = current_app.config["FOLDER_PATH"]
        pfp_path = os.path.join(folderPath, 'static', 'default.png')
        with open(pfp_path, 'rb') as f:
            default_pfp = f.read()
            print(default_pfp)

        new_user = users(fullname=form.fullname.data , email=form.email.data, username=form.username.data, password=pw_hash, dob=form.dob.data, gender=form.gender.data, bio=default_bio, pfp=default_pfp)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Please set your profile picture.')
        return redirect(url_for('index'))
    
    return render_template('register.html', form=form) 



@auth.route('/uploadpfp', methods=["POST"])
@login_required
def uploadpfp():
    file = request.files['profile_picture']
    if file and allowed_file(file.filename):
        pfp_change = file.read() 
        current_user.pfp = pfp_change
        db.session.commit()
        flash('Profile picture updated successfully.')
        return redirect(url_for('index'))
    else:
        flash('Invalid file type.')
        return redirect(url_for('index'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth.route('/updatebio', methods=["POST"])
@login_required
def updatebio():
    bio = request.form.get('bio_update')
    if bio:
        current_user.bio = bio
        db.session.commit()
        flash('Profile picture updated successfully.')
        return redirect(url_for('index'))
    else:
        flash('Invalid file type.')
        return redirect(url_for('index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
