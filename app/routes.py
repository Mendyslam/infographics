from datetime import datetime
from flask import flash
from flask import url_for
from flask import request
from flask import redirect
from flask import render_template
from flask_login import login_user
from flask_login import current_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse

from app import app
from app import db
from app.models import User, Post
from app.forms import LoginForm, RegistrationForm, EditProfileForm, FollowForm, PostForm


@app.before_request
def before_request():
    """
    Invoke before a request. Updates current_user user last seen
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Handles post creation and displays post associated with logged in user
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('You have just created a new post!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    prev_page = url_for('index', page=posts.prev_num) if posts.has_prev else None
    next_page = url_for('index', page=posts.next_num) if posts.has_next else None
    return render_template('index.html', title='Home Page',
        posts=posts.items, form=form, prev_page=prev_page, next_page=next_page)

@app.route('/explore')
@login_required
def explore():
    """
    Get access to all users
    """
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    prev_page = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    next_page = url_for('explore', page=posts.next_num) if posts.has_next else None
    return render_template('index.html', title="Explore",
        posts=posts.items, prev_page=prev_page, next_page=next_page)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user
    """
    if current_user.is_authenticated:
        redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you have successfully registered')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login form
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title="Sign In", form=form)

@app.route('/logout')
def logout():
    """
    Logout route
    """
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    """
    User profile endpoint
    """
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    prev_page = url_for('user',
        username=user.username, page=posts.prev_num) if posts.has_prev else None
    next_page = url_for('user',
        username=user.username, page=posts.next_num) if posts.has_next else None
    form = FollowForm()
    return render_template('user.html', user=user,
        posts=posts.items, form=form, prev_page=prev_page, next_page=next_page)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit user profile
    """
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been successfully edited')
        redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>/', methods=['POST'])
@login_required
def follow(username):
    """
    Follow logic
    """
    form = FollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You can not follow you')
            return redirect(url_for('user', username))
        current_user.follow(user)
        db.session.commit()
        flash('You now follow {}'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>/', methods=['POST'])
@login_required
def unfollow(username):
    """
    Unfollow logic
    """
    form = FollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You can not unfollow you')
            return redirect(url_for('user', username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You just unfollowed {}'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
