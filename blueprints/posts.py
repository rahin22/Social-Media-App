from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from .models import db, posts, likes, comments, saved, notifications
import os
from datetime import datetime
import uuid
from jinja2.exceptions import TemplateNotFound

posting = Blueprint('posting', __name__)


@posting.route('/create', methods=['GET','POST'])
@login_required
def create():
    description = request.form.get('postContent')
    print(description)
    if description:
        if 'post-image' in request.files and request.files['post-image']:
            print("good")
            file = request.files['post-image']
            if file and allowed_files(file.filename):
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                unique_filename = f"{current_time}_{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
                print(unique_filename)

                postfolder = 'static/posts'
                if not os.path.exists(postfolder):
                    os.mkdir(postfolder)

                file_path = os.path.join(postfolder, unique_filename)
                file.save(file_path)
                print(f"Saving file to: {file_path}")
                new_post = posts(userID=current_user.id , desc=description, img=unique_filename, date=current_time)
                db.session.add(new_post)
                db.session.commit()
        else:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            new_post = posts(userID=current_user.id , desc=description, date=current_time)
            db.session.add(new_post)
            db.session.commit()


    return redirect(url_for('myprofile.userprofile'))

def allowed_files(filename):
    ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@posting.route('/deletepost/<post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    find_post = posts.query.filter_by(postID=post_id, userID=current_user.id).first()
    if find_post:
        db.session.query(likes).filter_by(postID=post_id).delete()
        db.session.query(comments).filter_by(postID=post_id).delete()
        db.session.query(saved).filter_by(postID=post_id).delete()

        if find_post.img:
            filepath = os.path.join('static/posts', find_post.img)
            if os.path.exists(filepath):
                os.remove(filepath)

        db.session.delete(find_post)
        db.session.commit()

    return redirect(url_for('myprofile.userprofile'))





@posting.route('/editpost/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    find_post = posts.query.filter_by(postID=post_id, userID=current_user.id).first()
    if find_post:
        description = request.form.get('postEditDesc')
        find_post.desc = description
        db.session.commit()
    return redirect(url_for('myprofile.userprofile'))


@posting.route('/likeUpdate', methods=['GET','POST'])
@login_required
def like():
    if request.method == 'POST':
        postID = request.json.get('postID')        
        check_like = likes.query.filter_by(userID=current_user.id, postID=postID).first()
        find_user = posts.query.filter_by(postID=postID).first()
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if not check_like:
            new_like = likes(userID=current_user.id, postID=postID)
            like_content = f"{current_user.username} has liked your post" 
            like_notification = notifications(userID=find_user.user.id, notifyingUser=current_user.id, content=like_content, date=current_time, type=postID)
            db.session.add(like_notification)
            db.session.add(new_like)
            db.session.commit()
            return jsonify({'is_liked':True})
        else:
            db.session.delete(check_like)
            db.session.commit()
            return jsonify({'is_liked':False})
        

@posting.route('/comment/<postID>', methods=['GET', 'POST'])
@login_required
def comment(postID):
    if request.method == 'POST':
        postID = request.json.get('postID')
        print(postID)

    commentfolder = 'templates/comments'
    if not os.path.exists(commentfolder):
        os.mkdir(commentfolder)

    post = posts.query.filter_by(postID=postID).first()
    likeNumber = likes.query.filter_by(postID=postID).count()
    saveNumber = saved.query.filter_by(postID=postID).count()
    if post:
        liked_posts = []
        userprofile = post.user
        user_likes = likes.query.filter_by(userID=current_user.id).all()
        user_comments = comments.query.filter_by(postID=postID).all()

        for like in user_likes:
            liked_posts.append(like.postID)

        saved_posts = []
        user_saved = saved.query.filter_by(userID=current_user.id).all()

        for save in user_saved:
            saved_posts.append(save.postID)

        sorted_comments = sorted(user_comments, key=lambda comment: comment.date, reverse=True)
        
        try:
            return render_template(f"{postID}.html", post=post, user_likes=liked_posts, likeNumber=likeNumber, userprofile=userprofile, user_comments=sorted_comments, user_saved=saved_posts, saveNumber=saveNumber )
        except TemplateNotFound:
            htmlcont = render_template('comment.html', post=post, user_likes=liked_posts, likeNumber=likeNumber, userprofile=userprofile, user_comments=sorted_comments, user_saved=saved_posts, saveNumber=saveNumber)
            with open(f'templates/comments/{postID}.html', 'w') as post_page:
                post_page.write(htmlcont)
            return render_template(f'comments/{postID}.html')

        
@posting.route('/postComment', methods=['GET','POST'])
@login_required
def postComment():
    if request.method == 'POST':
        postID = request.form.get('postID')        
        comment = request.form.get('comments')
        if postID and comment:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            find_user = posts.query.filter_by(postID=postID).first()
            new_comment = comments(userID=current_user.id, postID=postID, comment=comment, date=current_time)
            comment_content = f"{current_user.username} left a comment on your post '{comment}'" 
            comment_notification = notifications(userID=find_user.user.id, notifyingUser=current_user.id, content=comment_content, date=current_time, type=postID)
            db.session.add(comment_notification)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('posting.comment', postID=postID))
        

@posting.route('/deletecomment/<comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    find_comment = comments.query.filter_by(commentID=comment_id, userID=current_user.id).first()
    if find_comment: 
        db.session.delete(find_comment)
        db.session.commit()
    return redirect(url_for('posting.comment', postID=find_comment.postID))


@posting.route('/editcomment/<comment_id>', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    find_comment = comments.query.filter_by(commentID=comment_id, userID=current_user.id).first()
    if find_comment:
        description = request.form.get('commentEditDesc')
        find_comment.comment = description
        db.session.commit()
    return redirect(url_for('posting.comment', postID=find_comment.postID))


@posting.route('/savePost', methods=['GET','POST'])
@login_required
def save():
    if request.method == 'POST':
        postID = request.json.get('postID')        
        check_save = saved.query.filter_by(userID=current_user.id, postID=postID).first()
        if not check_save:
            new_save = saved(userID=current_user.id, postID=postID)
            db.session.add(new_save)
            db.session.commit()
            return jsonify({'is_saved':True})
        else:
            db.session.delete(check_save)
            db.session.commit()
            return jsonify({'is_saved':False})