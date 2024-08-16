from os import getenv

from flask import Flask


app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///user"
app.secret_key = getenv("SECRET_KEY")

import routes
