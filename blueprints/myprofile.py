from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .models import db, users
from jinja2.exceptions import TemplateNotFound
from .models import db, users, followers, posts, likes, saved, notifications
import os
from datetime import datetime


myprofile = Blueprint('myprofile', __name__)

@myprofile.route('/myprofile')
@login_required
def userprofile(): 
    user_posts = posts.query.filter_by(userID=current_user.id).all()
    followerNumber = followers.query.filter_by(user_id=current_user.id).count()
    followingNumber = followers.query.filter_by(follower_id=current_user.id).count()
    postNumber = posts.query.filter_by(userID=current_user.id).count()

    for post in user_posts:
        post.date = datetime.strptime(post.date, '%Y-%m-%d_%H-%M-%S')

    sorted_posts = sorted(user_posts, key=lambda post: post.date, reverse=True)

    for post in sorted_posts:
        post.date = post.date.strftime('%Y-%m-%d_%H-%M-%S')

    liked_posts = []
    user_likes = likes.query.filter_by(userID=current_user.id).all()
    for like in user_likes:
        liked_posts.append(like.postID)

    saved_posts = []
    user_saved = saved.query.filter_by(userID=current_user.id).all()
    for save in user_saved:
        saved_posts.append(save.postID)

    saved_obj =  posts.query.filter(posts.postID.in_(saved_posts)).all()
    print(saved_obj)
    
    return render_template('myprofile.html', followers=followerNumber, following=followingNumber, posts=postNumber, user_posts=sorted_posts, user_likes=liked_posts, user_saved=saved_posts, saved_obj=saved_obj)


@myprofile.route('/myprofile/saved')
@login_required
def mysaved(): 
    user_posts = posts.query.filter_by(userID=current_user.id).all()
    followerNumber = followers.query.filter_by(user_id=current_user.id).count()
    followingNumber = followers.query.filter_by(follower_id=current_user.id).count()
    postNumber = posts.query.filter_by(userID=current_user.id).count()

    for post in user_posts:
        post.date = datetime.strptime(post.date, '%Y-%m-%d_%H-%M-%S')

    sorted_posts = sorted(user_posts, key=lambda post: post.date, reverse=True)

    for post in sorted_posts:
        post.date = post.date.strftime('%Y-%m-%d_%H-%M-%S')

    liked_posts = []
    user_likes = likes.query.filter_by(userID=current_user.id).all()
    for like in user_likes:
        liked_posts.append(like.postID)

    saved_posts = []
    user_saved = saved.query.filter_by(userID=current_user.id).all()
    for save in user_saved:
        saved_posts.append(save.postID)

    saved_obj =  posts.query.filter(posts.postID.in_(saved_posts)).all()
    for saves in saved_obj:
        sorted_saves = sorted(saved_obj, key=lambda saves: saves.date, reverse=True)
    
    return render_template('saved.html', followers=followerNumber, following=followingNumber, posts=postNumber, user_posts=sorted_posts, user_likes=liked_posts, user_saved=saved_posts, saved_obj=sorted_saves)



@myprofile.route('/profiles/<username>', methods=['GET','POST'])
@login_required
def profile(username):
    profilefolder = 'templates/profiles'
    if not os.path.exists(profilefolder):
        os.mkdir(profilefolder)

    userprofile = users.query.filter_by(username=username).first()
    if userprofile:
        user_posts = posts.query.filter_by(userID=userprofile.id).all()
        followerNumber = followers.query.filter_by(user_id=userprofile.id).count()
        followingNumber = followers.query.filter_by(follower_id=userprofile.id).count()
        check_following = followers.query.filter_by(user_id=userprofile.id, follower_id=current_user.id).first() is not None
        postNumber = posts.query.filter_by(userID=userprofile.id).count()

        for post in user_posts:
           post.date = datetime.strptime(post.date, '%Y-%m-%d_%H-%M-%S')

        sorted_posts = sorted(user_posts, key=lambda post: post.date, reverse=True)

        for post in sorted_posts:
            post.date = post.date.strftime('%Y-%m-%d_%H-%M-%S')

        liked_posts = []
        user_likes = likes.query.filter_by(userID=current_user.id).all()
        for like in user_likes:
           liked_posts.append(like.postID)

        saved_posts = []
        user_saved = saved.query.filter_by(userID=current_user.id).all()
        for save in user_saved:
           saved_posts.append(save.postID)

        if current_user.username == username:
            return redirect(url_for('myprofile.userprofile'))
        try:
            return render_template(f"{username}.html", userprofile=userprofile, followers=followerNumber, following=followingNumber, followCheck=check_following, posts=postNumber, user_posts=sorted_posts, user_likes=liked_posts, user_saved=saved_posts)
        except TemplateNotFound:
            htmlcont = render_template('profiletemp.html', userprofile=userprofile, followers=followerNumber, following=followingNumber, followCheck=check_following, posts=postNumber, user_posts=sorted_posts, user_likes=liked_posts, user_saved=saved_posts)
            with open(f'templates/profiles/{username}.html', 'w') as profile_page:
                profile_page.write(htmlcont)
            return render_template(f'profiles/{username}.html')
        

@myprofile.route('/followUpdate', methods=['GET','POST'])
@login_required
def follow():
    if request.method == 'POST':
        followerID = request.json.get('user_id')        
        check_follow = followers.query.filter_by(user_id=followerID, follower_id=current_user.id).first()
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if not check_follow:
            new_follow = followers(user_id=followerID, follower_id=current_user.id)
            follow_content = f"{current_user.username} has started following you" 
            follow_notification = notifications(userID=followerID, notifyingUser=current_user.id, content=follow_content, date=current_time, type="follow" )
            db.session.add(follow_notification)
            db.session.add(new_follow)
            db.session.commit()
            return jsonify({'is_following':True})
        else:
            unfollow_content = f"{current_user.username} has unfolowed you" 
            unfollow_notification = notifications(userID=followerID, notifyingUser=current_user.id, content=unfollow_content, date=current_time, type="follow" )
            db.session.add(unfollow_notification)
            db.session.delete(check_follow)
            db.session.commit()
            return jsonify({'is_following':False})
        

@myprofile.route('/updatepfp', methods=["POST"])
@login_required
def updatepfp():
    file = request.files['profile_picture']
    if file and allowed_files(file.filename):
        pfp_change = file.read() 
        current_user.pfp = pfp_change
        db.session.commit()
        flash('Profile picture updated successfully.')
        return redirect(url_for('myprofile.userprofile'))
    else:
        flash('Invalid file type.')
        return redirect(url_for('myprofile.userprofile'))
    

@myprofile.route('/editProfile', methods=['GET','POST'])
@login_required
def editProfile():
    bio = request.form.get('bioContent')
    print(bio)
    if bio:
        if 'edit_profile_picture' in request.files and request.files['edit_profile_picture']:
            print("good")
            file = request.files['edit_profile_picture']
            if file and allowed_files(file.filename):
                pfp_change = file.read() 
                current_user.pfp = pfp_change
                current_user.bio = bio
                db.session.commit()
        else:
            current_user.bio = bio
            db.session.commit()

    return redirect(url_for('myprofile.userprofile'))


def allowed_files(filename):
    ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS