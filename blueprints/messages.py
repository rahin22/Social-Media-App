from flask import Blueprint, render_template, redirect, url_for, request
from sqlalchemy import or_
from flask_login import login_required, current_user
from .models import db, conversation, message
from datetime import datetime

dmessage = Blueprint('dmessage', __name__)
@dmessage.route('/messages')
@login_required
def message_page():
    user_conversation = conversation.query.filter(or_(conversation.userID1 == current_user.id, conversation.userID2 == current_user.id)).all()
    print(user_conversation)
    return render_template('messaging.html', user_conversation=user_conversation)



@dmessage.route('/create_conversation', methods=['GET','POST'])
@login_required  
def create_conversation():
    other_user_id = request.form.get('user_id')
    
    existing_conversation = conversation.query.filter(or_((conversation.userID1 == current_user.id) & (conversation.userID2 == other_user_id), (conversation.userID1 == other_user_id) & (conversation.userID2 == current_user.id))).first()


    if existing_conversation:
        conversation_id = existing_conversation.conversationID
    else:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(current_time)
        new_conversation = conversation(userID1=current_user.id,userID2=other_user_id,dateCreated=current_time,lastUpdated=current_time)
        db.session.add(new_conversation)
        db.session.commit()
        conversation_id = new_conversation.conversationID

    return redirect(url_for('dmessage.message_page', conversation_id=conversation_id))


@dmessage.route('/load_messages', methods=['GET','POST'])
def load_messages():
    conversation_id = request.json.get('conversationID')
    print(conversation_id)
    conversation_messages = message.query.filter_by(conversationID=conversation_id).all()
    print(conversation_messages)
    content = render_template('show_message.html', selected_conversation=conversation_messages, conversation_id=conversation_id)


    return content

@dmessage.route('/send_message', methods=['GET','POST'])
def send_message():
    conversation_id = request.form.get('conversation_id')
    message_content = request.form.get('message')
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    new_message = message(conversationID=conversation_id, senderID=current_user.id, content=message_content, date=current_time)
    db.session.add(new_message)
    conversation_update = conversation.query.get(conversation_id)
    conversation_update.lastUpdated = current_time
    db.session.commit()

    updated_messages = message.query.filter_by(conversationID=conversation_id).all()

    updated_content = render_template('show_message.html', selected_conversation=updated_messages, conversation_id=conversation_id)
    return updated_content 