from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, current_user
from blueprints.models import db, users, followers, posts, likes, saved, comments
from blueprints.auth import auth as auth_blueprint 
from blueprints.myprofile import myprofile as myprofile_blueprint
from blueprints.search import search as search_blueprint
from blueprints.posts import posting as posts_blueprint
from blueprints.messages import dmessage as messages_blueprint
from blueprints.settings import settings as settings_blueprint
from blueprints.notifications import mynotifications as notification_blueprint
import os, base64
from datetime import datetime
import humanize
import random




app = Flask(__name__)
folderPath = os.path.dirname(os.path.abspath(__file__))
app.config["FOLDER_PATH"] = folderPath
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + folderPath + "/master.db"
app.config["SECRET_KEY"] = 'zR11b652Ue6tMD8SavPNvxk9EFJ5i7jZ'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True





Bootstrap(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

@app.template_filter('b64encode')
def b64encode_filter(s):
    return base64.b64encode(s).decode('utf-8')

@app.template_filter('to_datetime')
def to_datetime(date_string, format):
    return datetime.strptime(date_string, format)

@app.template_filter('relative_time')
def relative_time(date):
    now = datetime.now()
    return humanize.naturaltime(now - date)

@app.template_filter('strftime')
def strftime_format(date, format):
    return date.strftime(format)

@app.route('/')
@login_required
def index(): 
    followedUsers = followers.query.filter_by(follower_id=current_user.id).all()
    followed_userID = [user.user_id for user in followedUsers]


    user_likes = likes.query.filter_by(userID=current_user.id).all()
    liked_posts = [like.postID for like in user_likes]
    print(liked_posts)

    user_saved = saved.query.filter_by(userID=current_user.id).all()
    saved_posts = [save.postID for save in user_saved]
    print(saved_posts)

    user_comments = comments.query.filter_by(userID=current_user.id).all()
    commented_posts = [comment.postID for comment in user_comments]
    print(commented_posts)

    my_posts_query = posts.query.filter_by(userID=current_user.id).all()
    my_posts = [post.postID for post in my_posts_query]
    print(my_posts)

    followed_posts = []
    if followed_userID:
        followed_posts = posts.query.filter(posts.userID.in_(followed_userID)).all()
        followed_postIDs = [post.postID for post in followed_posts]
        print(followed_postIDs)
    else:
        followed_postIDs = []
    
    interacted_id = list(set(liked_posts + saved_posts + commented_posts + followed_postIDs + my_posts))
    print('Final',interacted_id)
    uninteracted_posts = posts.query.filter(posts.postID.notin_(interacted_id)).all()
    random.shuffle(uninteracted_posts)
    print(uninteracted_posts)

    sorted_following = []
    if followed_posts:
        sorted_following = sorted(followed_posts, key=lambda fposts: fposts.date, reverse=True)


    return render_template('index.html', followed_posts=sorted_following, user_likes=liked_posts, user_saved=saved_posts, uninteracted_posts=uninteracted_posts)


@app.route('/switchFeed')
def switch_feed():
    tab = request.args.get('tab')

    followedUsers = followers.query.filter_by(follower_id=current_user.id).all()
    followed_userID = [user.user_id for user in followedUsers]

    user_likes = likes.query.filter_by(userID=current_user.id).all()
    liked_posts = [like.postID for like in user_likes]
    print(f"liked{liked_posts}")

    user_saved = saved.query.filter_by(userID=current_user.id).all()
    saved_posts = [save.postID for save in user_saved]

    user_comments = comments.query.filter_by(userID=current_user.id).all()
    commented_posts = [comment.postID for comment in user_comments]

    my_posts_query = posts.query.filter_by(userID=current_user.id).all()
    my_posts = [post.postID for post in my_posts_query]

    followed_posts = []
    followed_postIDs = []
    if followed_userID:
        followed_posts = posts.query.filter(posts.userID.in_(followed_userID)).all()
        followed_postIDs = [post.postID for post in followed_posts]
    
    interacted_id = list(set(liked_posts + saved_posts + commented_posts + followed_postIDs + my_posts))


    if tab == 'fyp':
        uninteracted_posts = posts.query.filter(posts.postID.notin_(interacted_id)).all()
        random.shuffle(uninteracted_posts)
        content = render_template('fyp_posts.html', uninteracted_posts=uninteracted_posts, user_likes=liked_posts, user_saved=saved_posts)
    else:
        if not followed_userID:
            content = render_template('no_following.html')
        else:
            sorted_following = sorted(followed_posts, key=lambda fposts: fposts.date, reverse=True)
            content = render_template('following_posts.html', followed_posts=sorted_following, user_likes=liked_posts, user_saved=saved_posts)
    return content


app.register_blueprint(auth_blueprint)
app.register_blueprint(myprofile_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(posts_blueprint)
app.register_blueprint(messages_blueprint)
app.register_blueprint(settings_blueprint)
app.register_blueprint(notification_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
