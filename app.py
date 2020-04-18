# Importing Modules
import os
from flask import (
    Flask, render_template, flash, redirect, request, url_for, session)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps


# Declaring App Name
app = Flask(__name__)


# Configure MongoDB
app.config["MONGO_DBNAME"] = 'test_forFlourish'
app.config["MONGO_URI"] = 'mongodb+srv://root:r00tUser@myfirstcluster-suguw.mongodb.net/test_forFlourish?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = '314340f218da90b32caf021224f26824'

WATERING_FREQUENCY = ("Daily", "Every other day", "Weekly", "Monthly", "Rarely")

mongo = PyMongo(app)


@app.route('/add_admin')
def add_admin():
    users = mongo.db.users
    existing_user = users.find_one({'username': 'admin'})
    if not existing_user:
        # Password
        users.insert({
            'name': 'admin',
            'email': 'admin@myself',
            'username': 'admin',
            'password': 'admin',
            'is_admin': True
        })
        flash('User account successfully registered', 'success')
        return redirect(url_for('login_user'))
    return render_template("welcome_page.html")


@app.route('/populate')
def populate():
    plants = [
       {'plant_reference': 'plant_ref1', 'plant_name': 'plant_name', 'plant_description': 'plant_description', 'plant_placement': 'plant_placement', 'plant_care': 'plant_care'},
       {'plant_reference': 'plant_ref2', 'plant_name': 'plant_name', 'plant_description': 'plant_description', 'plant_placement': 'plant_placement', 'plant_care': 'plant_care'},
       {'plant_reference': 'plant_ref3', 'plant_name': 'plant_name', 'plant_description': 'plant_description', 'plant_placement': 'plant_placement', 'plant_care': 'plant_care'},
       {'plant_reference': 'plant_ref4', 'plant_name': 'plant_name', 'plant_description': 'plant_description', 'plant_placement': 'plant_placement', 'plant_care': 'plant_care'},
       {'plant_reference': 'plant_ref5', 'plant_name': 'plant_name', 'plant_description': 'plant_description', 'plant_placement': 'plant_placement', 'plant_care': 'plant_care'},
       {'plant_reference': 'plant_ref6', 'plant_name': 'plant_name', 'plant_description': 'plant_description', 'plant_placement': 'plant_placement', 'plant_care': 'plant_care'},
       {'plant_reference': 'plant_ref7', 'plant_name': 'plant_name', 'plant_description': 'plant_description', 'plant_placement': 'plant_placement', 'plant_care': 'plant_care'},
    ]
    for plant in plants:
        plant_collection = mongo.db.plants
        plant_collection.insert({
            'plant_reference': plant['plant_reference'],
            'plant_name': request.form['plant_name'],
            'plant_description': request.form['plant_description'],
            'plant_placement': request.form['plant_placement'],
            'plant_care': request.form['plant_care']
        })
    flash('User account successfully registered', 'success')
    return redirect(url_for('login_user'))


# Welcome Page
@app.route('/')
@app.route('/welcome_page')
def welcome_page():
    return render_template("welcome_page.html")


# Register
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        users = mongo.db.users
        username = request.form['username'].lower()
        existing_user = users.find_one({'username': username})

        if not existing_user:
            # Password
            users.insert({
                'name': request.form['name'],
                'email': request.form['email'].lower(),
                'username': username,
                'password': request.form['password'],
                'is_admin': False
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
        username = request.form['username'].lower()
        user_record = users.find_one({
            'username': username
        })
        # Check username_input and user_result
        if user_record:
            if user_record['password'] == request.form['password']:
                # Start a session using username
                session['logged_in'] = True
                session['username'] = username
                session['is_admin'] = user_record['is_admin']
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


@user_logged_in
def is_admin():
    return session['is_admin']


# Log user out
@app.route('/logout')
@user_logged_in
def logout():
    session['logged_in'] = False
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('welcome_page'))


# Admin user only - account
@app.route('/admin_account', methods=["GET", "POST"])
@user_logged_in
def admin_account():
    return render_template("admin_account.html", title='Administration Account')


# Admin user only - add plant
@app.route('/admin_add', methods=["GET", "POST"])
@user_logged_in
def admin_add():
    if request.method == 'POST':
        plants = mongo.db.plants
        plants.insert({
            'plant_reference': request.form['plant_reference'],
            'plant_name': request.form['plant_name'],
            'plant_description': request.form['plant_description'],
            'plant_placement': request.form['plant_placement'],
            'plant_care': request.form['plant_care']
        })
        flash('Plant recorded successfully', 'success')
        return redirect(url_for('admin_account'))
    return render_template("admin_add.html", title="Add Plant")


# Admin user only - search existing
@app.route('/admin_search', methods=["GET", "POST"])
@user_logged_in
def admin_search():
    plants = mongo.db.plants.find()
    return render_template("admin_search.html", title='Search Plants', plants=plants)


# Admin user only - update plant
@app.route('/admin_update/<plant_id>', methods=["GET", "POST"])
@user_logged_in
def admin_update(plant_id):
    plant_collection = mongo.db.plants
    plant = plant_collection.find_one({"_id": ObjectId(plant_id)})
    if request.method == 'POST':
        plant.update({
            'plant_reference': request.form['plant_reference'],
            'plant_name': request.form['plant_name'],
            'plant_description': request.form['plant_description'],
            'plant_placement': request.form['plant_placement'],
            'plant_care': request.form['plant_care']
        })
        plant_collection.update_one({"_id": ObjectId(plant_id)}, {"$set": plant})
        flash('Plant updated successfully', 'success')
        return redirect(url_for('admin_account'))
    return render_template("admin_update.html", title='Update Plant', plant=plant)


# User Account
@app.route('/user_account', methods=["GET", "POST"])
@user_logged_in
def user_account():
    plants = mongo.db.plants.find()
    records = mongo.db.users_plant_records.find({"user": get_authenticated_user()})
    return render_template("user_account.html", title='User Account', plants=plants, records=records)


# Add Plant Record
@app.route('/add_plant_record/<plant_id>', methods=['GET', 'POST'])
@user_logged_in
def add_plant_record(plant_id):
    plant = mongo.db.plants.find_one({"_id": ObjectId(plant_id)})
    if request.method == 'POST':
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
            'date_purchased': request.form['date_purchased'],
            'water_frequency': request.form['water_frequency'].lower(),
            'notes_added': request.form['notes_added']
        })
        flash('Plant recorded successfully', 'success')
        return redirect(url_for('user_account'))
    return render_template("add_plant_record.html", title='Add Plant Record',
        plant=plant, watering_frequency=WATERING_FREQUENCY)


# Edit User Plant Record
@app.route('/edit_user_plant_record/<record_id>', methods=["GET", "POST"])
@user_logged_in
def edit_user_plant_record(record_id):
    users_plant_records = mongo.db.users_plant_records
    record = users_plant_records.find_one({"_id": ObjectId(record_id)})
    if request.method == 'POST':
        record.update({
                'water_frequency': request.form['water_frequency'].lower(),
                'notes_added': request.form['notes_added']
            })
        users_plant_records.update_one({"_id": ObjectId(record_id)}, {"$set": record})
        flash('Plant record edited successfully', 'success')
        return redirect(url_for('user_account'))
    return render_template("edit_user_plant_record.html", title='Edit Plant Record',
        record=record, watering_frequency=WATERING_FREQUENCY)


# Delete User Plant Record
@app.route('/delete_user_plant_record/<record_id>', methods=["GET", "POST"])
@user_logged_in
def delete_user_plant_record(record_id):
    mongo.db.users_plant_records.remove({"_id": ObjectId(record_id)})
    flash('Plant record successfully deleted', 'danger')
    return redirect(url_for('user_account'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
