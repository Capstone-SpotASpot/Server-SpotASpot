#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------STANDARD DEPENDENCIES-----------------------------#

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_user, current_user, login_required, logout_user


#--------------------------------Project Includes--------------------------------#
from flask_helpers import flash_print, is_form
from userManager import UserManager
from user import User
from registrationForm import RegistrationForm
from loginForm import LoginForm
from forgotPasswordForm import ForgotPwdForm

class UserRoutes():
    """An object responsible for all the flask/website interactions involving user"""
    def __init__(self, app: Flask, user_manager: UserManager):
        """Initialize the UserRoutes class that works with the flask app

        Args:
            app (Flask): An existing flask app to extend
        """
        self.app = app
        self.user_manager = user_manager
        self.createUserPages()

    def createUserPages(self):
        # https://flask-login.readthedocs.io/en/latest/#login-example
        @self.app.route("/user/login", methods=["GET", "POST"], defaults={'username': None, 'password': None, 'rememberMe': None})
        @self.app.route("/user/login?username=<username>&password=<password>&rememberMe=<rememberMe>", methods=["GET", "POST"])
        def login(username: str, password: str, rememberMe: bool):
            # dont login if already logged in
            if current_user.is_authenticated: return redirect(url_for('index'))

            is_form = len(request.form) > 0
            form = LoginForm(self.app, self.user_manager)

            def login_fail(msg=""):
                flash_print(f'Invalid Username or Password!', "is-danger")
                # print(msg)
                return redirect(url_for('login'))

            username = None
            password = None
            rememberMe = None
            if request.method == "GET":
                return render_template("login.html", title="SpotASpot Login", form=form)
            elif request.method == "POST":
                # print("Login Form Params: username = {0}, password = {1}, rememberMe={2}".format(
                #     form.username.data, form.password.data, form.rememberMe.data
                # ))

                if is_form and form.validate_on_submit():
                    username = form.username.data
                    password = form.password.data
                    rememberMe = form.rememberMe.data
                elif is_form:
                    # unsuccessful login
                    return login_fail(msg="Failed to validate")
                else:
                    # make sure posting with normal method (not via form) still works
                    args = request.args
                    username = args.get("username")
                    password = args.get("password")
                    rememberMe = args.get("rememberMe")
                    print("Login Params: username = {0}, password = {1}, rememberMe={2}".format(
                        username, password, rememberMe
                    ))

                    # verify valid login
                    if(not self.user_manager.check_password(username, password)):
                        # unsuccessful login
                        return login_fail()

            # username & pwd must be right at this point, so login
            # https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader
            # call loadUser() / @user_loader in userManager.py
            user_id = self.user_manager.get_user_id(username)
            user = User(user_id)
            login_user(user, remember=rememberMe)

            # flash messages for login
            flash_print("Login Successful!", "is-success")
            flash_print(f"user id: {user_id}", "is-info") # format str safe bc not user input

            # route to original destination
            next = flask.request.args.get('next')
            isNextUrlBad = next == None or not is_safe_url(next, self._urls)
            if isNextUrlBad:
                return redirect(url_for('index'))
            else:
                return redirect(next)

            # on error, keep trying to login until correct
            return redirect(url_for("login"))

        @self.app.route("/user/get_id", methods=["GET"])
        @login_required
        def get_user_id():
            return {'user_id': current_user.id}


        @self.app.route("/user/signup", methods=["GET", "POST"],
                         defaults={'fname': None, 'lname': None, 'username': None, 'password': None, 'password2': None})
        @self.app.route("/user/signup?fname=<fname>&lname=<lname>&username=<username>&password=<password>&password2=<password2>", methods=["GET", "POST"])
        def signup(fname:str, lname:str, username:str, password:str, password2: str):
            if current_user.is_authenticated: return redirect(url_for('index'))

            is_form = len(request.form) > 0
            form = RegistrationForm(self.app, user_manager=self.user_manager)

            def signup_fail(msg=""):
                flash_print(f'Signup Failed! {msg}', "is-danger")
                # try again
                return redirect(url_for("signup"))
            def signup_succ(username, msg=""):
                # since validated, always return to login
                flash_print(f"Signup successful for {username}! {msg}", "is-success")
                return redirect(url_for("login"))

            if request.method == "POST":
                if is_form and form.validate_on_submit():
                    fname = form.fname.data
                    lname = form.lname.data
                    username = form.username.data
                    pwd = form.password.data
                elif is_form:
                    return signup_fail()
                else:
                    # make sure posting with normal method (not via form) still works
                    args = request.args
                    fname = args.get("fname")
                    lname = args.get("lname")
                    username = args.get("username")
                    pwd = args.get("password")
                    pwd2 = args.get("password2")

                add_res = self.user_manager.add_user(fname, lname, username, pwd)
                if(add_res != -1):
                    return signup_succ(username)
                else:
                    return signup_fail(msg="failed to add user to db")

            elif request.method == "POST":
                print("Signup Validation Failed")

            # on GET or failure, reload
            return render_template('signup.html', title="SpotASpot Signup", form=form)


        @self.app.route("/user/forgot_password", methods=["GET", "POST"], defaults={'uname': None, 'new_pwd': None})
        @self.app.route("/user/forgot_password?uname=<uname>&new_pwd=<new_pwd>", methods=["GET", "POST"])
        def forgotPassword(uname: str, new_pwd: str):
            is_form = len(request.form) > 0
            form = ForgotPwdForm(self.app, user_manager=self.user_manager)
            update_res = True

            if request.method == "POST":
                if is_form and form.validate_on_submit():
                    uname = form.username.data
                    new_pwd = form.new_password.data
                elif is_form:
                    # flash_print(f"Password Reset Fail! Bad form", "is-warning")
                    uname = new_pwd = None
                else:
                    # make sure posting with normal method (not via form) still works
                    args = request.args
                    uname = args.get("uname")
                    new_pwd = args.get("new_pwd")

                if uname != None and new_pwd != None:
                    update_res = self.user_manager.update_pwd(uname, new_pwd)

                    if update_res == 1:
                        flash_print("Password Reset Successful", "is-success")
                        return redirect(url_for('index'))
                print(f"Password Reset Failed: {uname} w/ {new_pwd}")
                flash("Password Reset Failed", "is-danger")

            # on GET or failure, reload
            return render_template("forgot_password.html", title="SpotASpot Reset Password", form=form)

        @self.app.route("/user/logout", methods=["GET", "POST"])
        @login_required
        def logout():
            logout_user()
            flash("Successfully logged out!", "is-success")
            return redirect(url_for("login"))
