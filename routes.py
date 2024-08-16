from flask import Flask
from app import app
#from db import db
import users
from flask import render_template, request, redirect

@app.route("/", methods=['GET','POST'])
def index():
    return render_template("index.html")

@app.route("/register", methods=["get", "post"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":
        username = request.form["username"]
        if len(username) < 3 or len(username)>20:
            return render_template("error.html", message="Your username must be 3-20 characters long")
        
        password1 = request.form["password1"]
        password2 = request.form["password2"]
    
        if password1 != password2:
            return render_template("error.html", message="Passwords don't match")
        if password1 == "":
            return render_template("error.html", message="Password empty")
        
        if not users.register(username, password1):
            return render_template("error.html", message="Registering failed")
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if users.login(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Wrong username or password")
        
@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")