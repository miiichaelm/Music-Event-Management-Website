from main import app
from flask import request, render_template, flash, redirect, url_for, session
from db.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm

from db.models import db


# @app.route('/login/', methods=['GET', 'POST'])
# def login():
#     # redirect if user already logged in
#     if session.get('logged_in'):
#         return redirect("/")

#     # Creating Login form object
#     form = LoginForm(request.form)
#     # verifying that method is post and form is valid
#     if request.method == 'POST' and form.validate():
#         # checking that user exists or not
#         user = User.query.filter_by(email=form.email.data).first()

#         if user:
#             print("Here")
#             # if user exist in database than we will compare our database hashed password
#             # and password come from login form
#             if check_password_hash(user.password, form.password.data):
#                 # if password is matched, allow user to access and save email and username inside the session
#                 flash('You have successfully logged in.', "success")

#                 session['logged_in'] = True

#                 session['email'] = user.email

#                 session['username'] = user.username

#                 session['user_id'] = user.id
#                 print(session['username'])
#                 # After successful login, redirecting to home page
#                 return redirect('/')

#             else:

#                 # if password is in correct , redirect to login page
#                 flash('Username or Password Incorrect', "Danger")
#                 print("Invalid username or password")
#                 return redirect('/login/')

#     # rendering login page
#     return render_template('login.html', form=form)


# @app.route('/register/', methods=['GET', 'POST'])
# def register():
#     # redirect if user already logged in
#     if session.get('logged_in'):
#         return redirect("/")

#     # Creating RegistrationForm class object
#     form = RegisterForm(request.form)

#     # Checking that method is post and form is valid or not.
#     if request.method == 'POST' and form.validate():

#         # if all is fine, generate hashed password
#         hashed_password = generate_password_hash(form.password.data, method='sha256')

#         # create new user model object
#         new_user = User(

#             name=form.name.data,

#             username=form.username.data,

#             email=form.email.data,

#             password=hashed_password)

#         # saving user object into data base with hashed password
#         db.session.add(new_user)

#         db.session.commit()

#         flash('You have successfully registered', 'success')

#         # if registration successful, then redirecting to login Api
#         return redirect(url_for('login'))

#     else:

#         # if method is Get, than render registration form
#         return render_template('register.html', form=form)


# @app.route('/logout/')
# def logout():
#     # Removing data from session by setting logged_flag to False.
#     session['logged_in'] = False
#     session['username'] = None
#     session['email'] = None
#     # redirecting to home page
#     return redirect(url_for('index'))
