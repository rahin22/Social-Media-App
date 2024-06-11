from flask import Blueprint, render_template
from flask_login import current_user
from .models import posts, notifications


mynotifications = Blueprint('mynotifications', __name__)

@mynotifications.route('/notifications')
def notification_page():
    user_notifications = notifications.query.filter_by(userID=current_user.id).all()

    notification_check = []
    for notification in user_notifications:
        if notification.type.isdigit():  
            post = posts.query.filter_by(postID=int(notification.type)).first()
            if post:
                notification.post = post
        notification_check.append(notification)
        print(notification_check)

    sorted_notifications = sorted(notification_check, key=lambda notification: notification.date, reverse=True)
    print(user_notifications)

    if not sorted_notifications:
        return render_template('no_notifications.html')
    else:
        return render_template('notifications.html', user_notifications=sorted_notifications)

