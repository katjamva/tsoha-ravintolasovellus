from db import db
from sqlalchemy import text
from flask import request

def get_reviews(restaurant_id):
        sql = text("SELECT u.username, r.stars, r.comment FROM reviews r, users u WHERE r.user_id=u.id AND r.restaurant_id=:restaurant_id ORDER BY r.id")
        return db.session.execute(sql, {"restaurant_id":restaurant_id}).fetchall()

def add_review(user_id, restaurant_id, stars, comment):
        sql = text("INSERT INTO reviews (user_id, restaurant_id, stars, comment) VALUES (:user_id, :restaurant_id, :stars, :comment)")
        db.session.execute(sql, {"user_id":user_id, "restaurant_id":restaurant_id, "stars":stars, "comment":comment})
        db.session.commit()

def get_restaurant_info(restaurant_id):
        sql = text("SELECT id, name, cuisine, description, location, opening_hours FROM restaurants WHERE id=:restaurant_id")
        return db.session.execute(sql, {"restaurant_id": restaurant_id}).fetchone()

def get_all_restaurants():
        sql = text("SELECT id, name FROM restaurants ORDER BY name") #MUISTA LISÄTÄ ORDER BY KUN REVIEWS VALMIS
        return db.session.execute(sql).fetchall()

def search(query):
        sql = text("SELECT id, name, description, location, cuisine FROM restaurants WHERE name ILIKE :query OR description ILIKE :query OR location ILIKE :query OR cuisine ILIKE :query")
        return db.session.execute(sql, {"query":"%"+query+"%"}).fetchall()
        

def search_by_name(query):
        sql = text("SELECT id, name FROM restaurants WHERE name LIKE :query")
        result = db.session.execute(sql, {"query":"%"+query+"%"})
        searches = result.fetchall()
        return searches

def add_restaurant(name, cuisine, description, opening_hours, location,):
        sql = text("INSERT INTO restaurants (name, cuisine, description, opening_hours, location) VALUES (:name, :cuisine, :description, :opening_hours, :location) RETURNING id")
        restaurant_id = db.session.execute(sql, {"name":name, "cuisine":cuisine, "description":description, "opening_hours":opening_hours, "location":location}).fetchone()[0]
        db.session.commit()
        return restaurant_id
