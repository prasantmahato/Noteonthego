from cProfile import Profile
from distutils.log import info
import profile
from app import app, db
from flask import request, redirect, render_template, url_for, flash
from app.model import Todo, User
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from werkzeug.urls import url_parse

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index(): 
    if(request.method == 'POST'):
        task_content = request.form['content']
        if len(task_content) > 2:
            new_task = Todo(content=task_content, user_id = current_user.get_id())
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                return "There was an issue adding your task"
        else:
            flash('Include atleast 3 characters', category='danger')
            return redirect(url_for('index'))
    else:
        # tasks = Todo.query.order_by(Todo.date_created).all() # alt:  .first 
        tasks = Todo.query.filter_by(
                user_id=current_user.get_id()).order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        flash('Note deleted', category='danger')
        return redirect('/')
    
    except:
        return "There was a problem deleting that task."


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        
        try:
            db.session.commit()
            flash('Note updated', category='success')
            return redirect('/')
        except:
            return "There was an issue in update"
    else:
        return render_template("update.html", task=task, title="Update")



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', category='danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


# Method to logout
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', category='warning')
    return redirect(url_for('index'))

# Method to register users 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Insert registered user to database
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.lower(),first_name=form.first_name.data, 
                    last_name=form.last_name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign Up', form=form)


# User profile view function
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


# Edit profile view function
@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # form.profile_images.choices = []
    if form.validate_on_submit():
        current_user.username = form.username.data.lower()
        current_user.about_me = form.about_me.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('Profile updated successfully.', category='success')
        return redirect('user/'+current_user.username)
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    
    return render_template('edit_profile.html', title='Edit Profile', form=form, user=user)