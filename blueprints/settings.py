from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length, Regexp, EqualTo, ValidationError
from passlib.hash import pbkdf2_sha256
from .models import db, users, followers, posts, likes, comments, saved, conversation, message


settings = Blueprint('settings', __name__)

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
    
def oldpword(pform,field):
   usernamecheck = users.query.filter_by(username=current_user.username).first()
   if not pbkdf2_sha256.verify(field.data, usernamecheck.password):
      raise ValidationError('Password entered is incorrect please enter correct current password')


class infoForm(FlaskForm):
    fullname = StringField('Full Name', validators=[InputRequired(), Length(max=100), Regexp(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", message="Full Name must contain only letters, spaces, hyphens, or apostrophes")], render_kw={"placeholder": "Enter your Full Name"})
    dob = DateField('Date of Birth', render_kw={'disabled':''})
    gender = SelectField(u'Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])


class passwordform(FlaskForm):
    oldpassword = PasswordField('Old Password', validators=[InputRequired(),Length(min=8,max=50),oldpword], render_kw={"placeholder": "Old Password"})
    newpassword = PasswordField('New Password', validators=[InputRequired(),Length(min=8,max=50),EqualTo('confirm', message='New Passwords Must Match')], render_kw={"placeholder": "Create New Password"})
    confirm  = PasswordField('Repeat Password', validators=[InputRequired(),Length(min=8,max=50)], render_kw={"placeholder": "Confirm New Password"})

class userForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=5, max=12), Regexp('^\w+$', message="Username must contain only letters, numbers, or underscores"), check_username, check_usercaps], render_kw={"placeholder": "Create username"})

class deleteform(FlaskForm):
    delpassword = PasswordField('Password', validators=[InputRequired(),Length(min=8,max=50),oldpword], render_kw={"placeholder": "Enter Your Password"})
    deleteaccount = SubmitField('Delete Account')


@settings.route('/settings', methods=['GET','POST'])
@login_required
def settings_page():
    form = infoForm()
    user_form = userForm()
    pform = passwordform()
    delform = deleteform()  

    if request.method == 'POST':
        if 'save_info' in request.form and form.validate_on_submit():
            user_update = users.query.filter_by(id=current_user.id).first()
            user_update.fullname = form.fullname.data
            user_update.dob = form.dob.data
            user_update.gender = form.gender.data
            db.session.commit()

        elif 'save_username' in request.form and user_form.validate_on_submit():
            user_update = users.query.filter_by(id=current_user.id).first()
            user_update.username = user_form.username.data
            db.session.commit()

        elif 'save_password' in request.form and pform.validate_on_submit():
            user = users.query.get(current_user.id)
            if user:
                pw_hash = pbkdf2_sha256.hash(pform.newpassword.data)
                user.password = pw_hash
                db.session.commit()
                flash('Password changed successfully!')

        elif 'delete_account' in request.form and delform.validate_on_submit():
            user_id = current_user.id

            db.session.query(followers).filter((followers.user_id == user_id) | (followers.follower_id == user_id)).delete()
            db.session.query(posts).filter_by(userID=user_id).delete()
            db.session.query(likes).filter_by(userID=user_id).delete()
            db.session.query(comments).filter_by(userID=user_id).delete()
            db.session.query(saved).filter_by(userID=user_id).delete()

            conversations = db.session.query(conversation).filter((conversation.userID1 == user_id) | (conversation.userID2 == user_id)).all()
            for conv in conversations:
                db.session.query(message).filter_by(conversationID=conv.conversationID).delete()
                db.session.delete(conv)
            user_to_delete = db.session.query(users).filter_by(id=user_id).first()
            if user_to_delete:
                db.session.delete(user_to_delete)

            db.session.commit()
            flash('Your account has been deleted successfully!')
            logout_user()
            return redirect(url_for('index'))  

    return render_template('settings.html', form=form, userForm=user_form, pform=pform, delform=delform)

