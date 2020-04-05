# Importing Modules
import os
import logging
from flask import (
    Flask, render_template, flash, redirect, request, url_for, session)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from wtforms import (
    Form, StringField, DateTimeField, TextAreaField, PasswordField, validators)
from functools import wraps


# Declaring App Name
app = Flask(__name__)


# Configure MongoDB
app.config["MONGO_DBNAME"] = 'test_forFlourish'
app.config["MONGO_URI"] = 'mongodb+srv://root:r00tUser@myfirstcluster-suguw.mongodb.net/test_forFlourish?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = 'florish123'

mongo = PyMongo(app)


# Welcome Page
@app.route('/')
@app.route('/welcome_page')
def welcome_page():
    return render_template("welcome_page.html")


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# Register
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm(request.form)
    users = mongo.db.users
    if request.method == 'POST' and form.validate():
        # Insert input fields into MongoDB users collection
        users.insert({
            'name': request.form['name'].lower(),
            'email': request.form['email'].lower(),
            'username': request.form['username'].lower(),
            'password': request.form['password'].lower()
        })
        # Message to acknowledge registration needed
        flash('Registration complete. Please log in.', 'success')

        return redirect(url_for('login_user'))
    return render_template('register_user.html', form=form)


# Login
@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        users = mongo.db.users
        # Get username from input field
        username_input = request.form['username']
        # password_input = request.form['password']
        # import pdb
        # pdb.set_trace()

        # Check username exists in user database
        current_user = users.find_one({
            'username': request.form['username'].lower()
        })
        # Check username_input and user_result
        if current_user:
            if current_user['password'] == request.form['password']:
                logging.info('Usernames matched')
                # Start a session using username
                session['logged_in'] = True
                session['username'] = username_input

                # Message to acknowledge registration successful
                flash('Log in complete', 'success')

                return redirect(url_for('user_account'))

        logging.info('No user registered under that username')
        # End session
        session.clear('username', None)
        return render_template('login_user.html')
    return render_template('login_user.html')


# Check user is logged in - decorator
def user_logged_in(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorised access. Please login', 'danger')
            return redirect(url_for('login_user'))
    return decorator


# Log user out
@app.route('/logout')
@user_logged_in
def logout():
    # Start a session using username
    session['logged_in'] = False
    # Remove username from the session
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('welcome_page'))


# User Account
@app.route('/user_account')
@user_logged_in
def user_account():
    return render_template("user_account.html", plants=mongo.db.plants.find())


# Add Plant Record Form Class
class AddPlantRecord(Form):
    date_purchased = DateTimeField('Date Purchased', format='%d/%m/%y')
    water_frequency = TextAreaField('Water Frequency')
    notes_added = TextAreaField('Notes')

# Add Plant Record
@app.route('/add_plant_record', methods=['GET', 'POST'])
@user_logged_in
def add_plant_record():
    plants = mongo.db.plants.find({"_id": ['id']})
    form = AddPlantRecord(request.form)
    users_plant_records = mongo.db.users_plant_records
    if request.method == 'POST':
        users_plant_records.insert({
            'date_purchased': request.form['date_purchased'].lower(),
            'water_frequency': request.form['water_frequency'].lower(),
            'notes_added': request.form['notes_added'].lower()
        })
        return redirect(url_for('user_account'))
    return render_template("add_plant_record.html", form=form, plants=plants)


# Edit User Plant Record
@app.route('/edit_user_plant_record')
@user_logged_in
def edit_user_plant_record():
    return render_template("edit_user_plant_record.html")


# Delete User Plant Record


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
