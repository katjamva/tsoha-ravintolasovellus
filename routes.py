from flask import Flask
from app import app
from db import db
#import users
from flask import render_template

@app.route("/", methods=['GET','POST'])
def index():
    return render_template("index.html")


