import os
from db import db
from functools import wraps
from sqlalchemy import text
from flask import abort, request, session
from werkzeug.security import check_password_hash, generate_password_hash

def login(username, password):
    sql = text("SELECT password, id , role FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    if not check_password_hash(user[0], password):
        return False
    session["user_id"] = user[1]
    session["username"] = username 
    session["user_role"] = user[2]
    session["csrf_token"] = os.urandom(16).hex()
    return True

def register(username, password, user_role):
    hash_value = generate_password_hash(password)
    try:
        sql = text("INSERT INTO users (username, password, role) VALUES (:username, :password, :user_role)")
        db.session.execute(sql, {"username":username, "password":hash_value, "user_role":user_role})
        db.session.commit()
    except:
        return False
    return login(username, password)

def user_id():
    return session.get("user_id", 0)

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
        

def logout():
    del session["user_id"]
    del session["username"]
    
def admin_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if session.get("user_role") != "admin":
            abort(403)
        return func(*args, **kwargs)
    return wrap        

def promote_to_admin(username):
    try:
        sql = text("UPDATE users SET role = 'admin' WHERE username = :username")
        result = db.session.execute(sql, {"username": username})
        db.session.commit()
        return result.rowcount > 0 
    except Exception as e:
        print(f"Error promoting user to admin: {e}")
        return False