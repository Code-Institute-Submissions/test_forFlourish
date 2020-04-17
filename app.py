# Importing Modules
import os
import logging
from flask import (
    Flask, render_template, flash, redirect, request, url_for, session)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from wtforms import (
    Form, StringField, DateField, TextAreaField, PasswordField, SelectField)
from wtforms.validators import DataRequired, Length, EqualTo, Email
from functools import wraps


# Declaring App Name
app = Flask(__name__)


# Configure MongoDB
app.config["MONGO_DBNAME"] = 'test_forFlourish'
app.config["MONGO_URI"] = 'mongodb+srv://root:r00tUser@myfirstcluster-suguw.mongodb.net/test_forFlourish?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = '314340f218da90b32caf021224f26824'

mongo = PyMongo(app)


# Welcome Page
@app.route('/')
@app.route('/welcome_page')
def welcome_page():
    return render_template("welcome_page.html")


# # Register Form Class
# class RegisterForm(Form):
#     name = StringField('Name', [
#         DataRequired(), Length(min=1, max=50)])
#     email = StringField('Email', [
#         Email(message='Not a valid email address.'), DataRequired()])
#     username = StringField('Username', [
#         DataRequired(), Length(min=4, max=25)])
#     password = PasswordField('Password', [
#         DataRequired(message='Please enter a password')
#     ])
#     confirm = PasswordField('Confirm Password', [
#         EqualTo('password', message='Passwords must match')
#     ])


# Register
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    users = mongo.db.users
    if request.method == 'POST':
        existing_user = users.find_one({'username': request.form['username'].lower()})

        if not existing_user:
            # Insert input fields into users collection
            users.insert({
                'name': request.form['name'].lower(),
                'email': request.form['email'].lower(),
                'username': request.form['username'].lower(),
                'password': request.form['password'].lower()
            })
            flash('User account successfully registered', 'success')
            return redirect(url_for('login_user'))

        flash('Username already exists. Please try a different username', 'danger')
        return render_template('register_user.html', title='Register')

    return render_template('register_user.html', title='Register')


# Login
@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        users = mongo.db.users
        username_input = request.form['username']
        # password_input = request.form['password']
        
        current_user = users.find_one({
            'username': request.form['username'].lower()
        })
        # Check username_input and user_result
        if current_user:
            if current_user['password'] == request.form['password']:
                # Start a session using username
                session['logged_in'] = True
                session['username'] = username_input
                flash('Log in complete', 'success')
                return redirect(url_for('user_account'))
        else:
            # End session
            session.clear()
            flash('No user registered under that username', 'danger')

    return render_template('login_user.html', title='Login')


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

# Authenticate user
@user_logged_in
def get_authenticated_user():
    return session['username']


# Log user out
@app.route('/logout')
@user_logged_in
def logout():
    session['logged_in'] = False
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('welcome_page'))


# User Account
@app.route('/user_account', methods=["GET", "POST"])
@user_logged_in
def user_account():
    plants = mongo.db.plants.find()
    records = mongo.db.users_plant_records.find({"user": session['username']})
    return render_template("user_account.html", title='User Account', plants=plants, records=records)


# Add Plant Record Form Class
class AddPlantRecord(Form):
    date_purchased = DateField('Date Purchased', format='%d/%m/%Y')
    water_frequency = SelectField('Water Frequency', choices=[
            ('Blank', ''),
            ('Daily', 'Daily'),
            ('Weekly', 'Weekly'),
            ('Fortnightly', 'Fortnightly'),
            ('Monthly', 'Monthly')])
    notes_added = TextAreaField('Notes')

# Add Plant Record
@app.route('/add_plant_record/<plant_id>', methods=['GET', 'POST'])
@user_logged_in
def add_plant_record(plant_id):
    plant = mongo.db.plants.find_one({"_id": ObjectId(plant_id)})
    # import pdb
    # pdb.set_trace()
    if request.method == 'POST'():
        users_plant_records = mongo.db.users_plant_records
        users_plant_records.insert({
            'user': get_authenticated_user(),
            'plant': {
                '_id': plant['_id'],
                'plant_reference': plant['plant_reference'],
                'plant_name': plant['plant_name'],
                'plant_description': plant['plant_description'],
                'plant_placement': plant['plant_placement'],
                'plant_care': plant['plant_care']
            },
            'date_purchased': request.form['date_purchased'].lower(),
            'water_frequency': request.form['water_frequency'].lower(),
            'notes_added': request.form['notes_added'].lower()
        })
        flash('Plant recorded successfully', 'success')
        return redirect(url_for('user_account'))
    else:
        form = AddPlantRecord(request.form)
    return render_template("add_plant_record.html", title='Add Plant Record', plant=plant, form=form)


# Edit User Plant Record
@app.route('/edit_user_plant_record/<record_id>', methods=["GET", "POST"])
@user_logged_in
def edit_user_plant_record(record_id):
    form = AddPlantRecord(request.form)
    record = mongo.db.users_plant_records.find_one({"_id": ObjectId(record_id)})
    # Populate form fields
    if request.method == 'POST' and form.validate():
        record.update({
            # 'user': get_authenticated_user(),
            # 'plant': {
            #     '_id': record['_id'],
            #     'plant_reference': record['plant_reference'],
            #     'plant_name': record['plant_name'],
            #     'plant_description': record['plant_description'],
            #     'plant_placement': record['plant_placement'],
            #     'plant_care': record['plant_care'],
            #     'date_purchased': record['date_purchased']
            # },
            'water_frequency': request.form['water_frequency'].lower(),
            'notes_added': request.form['notes_added'].lower()
        })
        flash('Plant record edited successfully', 'success')
        return redirect(url_for('user_account'))
    return render_template("edit_user_plant_record.html", title='Edit Plant Record', record=record,
        form=form)


# Delete User Plant Record
@app.route('/delete_user_plant_record/<record_id>', methods=["GET", "POST"])
@user_logged_in
def delete_user_plant_record(record_id):
    mongo.db.users_plant_records.remove({"_id": ObjectId(record_id)})
    return redirect(url_for('user_account'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
