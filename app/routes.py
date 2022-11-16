from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template

from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Mendy'}
    posts = [
        {
            'author': {'username': 'David'},
            'body': 'I work with THINK ETERNITY as a consultant'
        },
        {
            'author': {'username': 'Favour'},
            'body': 'I am Software Engineer'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login form
    """
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for {}, remember me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title="Sign In", form=form)
