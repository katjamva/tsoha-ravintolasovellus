from db import db
from sqlalchemy import text
from flask import request
from flask import Flask
from sqlalchemy import text

def remove_review(review_id):
        sql = text("DELETE FROM reviews WHERE id = ANY(:review_id)")
        db.session.execute(sql, {"review_id":review_id})
        db.session.commit()

def update_category_name(category_id, new_name):
        sql = text("""
                   UPDATE categories
                   SET category = :new_name
                   WHERE id = :category_id
        """)
        db.session.execute(sql, {"category_id": category_id, "new_name": new_name})
        db.session.commit()
    
def remove_category(category_ids):
        sql = text("""
                   DELETE FROM categories 
                   WHERE id = ANY(:category_ids)
        """)
        db.session.execute(sql,{"category_ids": category_ids})
        db.session.commit()

def search_categories(search_query): #ei käytössä vielä
    sql = text("""
               SELECT id, category 
               FROM categories
               WHERE category ILIKE :search_query
        """)
    result = db.session.execute(sql, {"search_query": f"%{search_query}%"})
    return result.fetchall()


def update_restaurant_categories(restaurant_id, selected_category_ids):
        sql = text("""
                DELETE FROM restaurant_categories
                WHERE restaurant_id = :restaurant_id
        """)
        db.session.execute(sql, {"restaurant_id": restaurant_id})

        for category_id in selected_category_ids:
                add_restaurant_category(restaurant_id, category_id)

        db.session.commit()

def get_all_categories():
        sql = text("""
                   SELECT id, category FROM categories
                   ORDER BY category
                """)
        result = db.session.execute(sql)
        return result.fetchall()

def get_restaurants_from_category(category):
        sql = text("""
                   SELECT r.id, r.name, r.description, r.address
                   FROM restaurants r
                   JOIN restaurant_categories rc ON r.id = rc.restaurant_id
                   JOIN categories c ON rc.category_id = c.id
                   WHERE c.category=:category
        """)
        result = db.session.execute(sql, {"category":category})
        return result.fetchall()

def get_categories_for_restaurant(restaurant_id):
        sql = text("""SELECT c.id, c.category
                   FROM categories c
                   JOIN restaurant_categories rc ON c.id = rc.category_id
                   WHERE rc.restaurant_id=:restaurant_id
        """)
        result = db.session.execute(sql, {"restaurant_id":restaurant_id})
        return result.fetchall()
        
def add_restaurant_category(restaurant_id, category_id):
        sql = text("""
                   INSERT INTO restaurant_categories (restaurant_id, category_id)
                   VALUES (:restaurant_id, :category_id)
        """)
        db.session.execute(sql, {"restaurant_id":restaurant_id, "category_id":category_id})
        db.session.commit()
        
def add_category(category):
        sql = text("""
                   INSERT INTO categories (category)
                   VALUES (:category)
                   RETURNING id
        """)
        result = db.session.execute(sql, {"category": category})
        db.session.commit()
        
        new_category_id = result.fetchone()[0]
        return new_category_id
        

def get_all_restaurants():
    sql = text("SELECT id, name FROM restaurants")
    result = db.session.execute(sql)
    return result.fetchall()

def get_top_10():
        sql = text("""
                SELECT r.id, r.name, ROUND(AVG(rv.stars), 2) AS average_rating
                FROM restaurants r
                LEFT JOIN reviews rv ON r.id = rv.restaurant_id
                GROUP BY r.id, r.name
                ORDER BY average_rating DESC
                LIMIT 10
        """)
        result = db.session.execute(sql)
        return result.fetchall()
       

def rating(restaurant_id):
        sql = text("""
                   SELECT ROUND(AVG(stars),2) AS rating_average 
                   FROM reviews WHERE  restaurant_id=:restaurant_id
        """)
        result = db.session.execute(sql, {"restaurant_id": restaurant_id}).fetchone()
        return result.rating_average

def edit_openinghours(restaurant_id, opening, closing, day):
        sql = text("""
                   UPDATE openinghours
                   SET opening=:opening, closing=:closing
                   WHERE restaurant_id=:restaurant_id AND day=:day
                   """)
        db.session.execute(sql, {"opening":opening, "closing":closing, "restaurant_id":restaurant_id, "day":day})
        db.session.commit()
        
def edit(id, name, description, address):
        sql = text("""
                UPDATE restaurants SET name=:name, description=:description, address=:address
                WHERE id=:id
                """)
        db.session.execute(sql, {"id": id, "name": name, "description": description, "address": address})
        db.session.commit()

def remove_restaurant(restaurant_id):
        sql = text("DELETE FROM restaurants WHERE id=:restaurant_id")
        db.session.execute(sql, {"restaurant_id":restaurant_id})
        db.session.commit()

def get_reviews(restaurant_id):
        sql = text("""
                   SELECT u.username, r.stars, r.comment FROM reviews r, users u 
                   WHERE r.user_id=u.id AND r.restaurant_id=:restaurant_id 
                   ORDER BY r.id
                """)
        return db.session.execute(sql, {"restaurant_id":restaurant_id}).fetchall()

def add_review(user_id, restaurant_id, stars, comment):
        sql = text("""
                   INSERT INTO reviews (user_id, restaurant_id, stars, comment) 
                   VALUES (:user_id, :restaurant_id, :stars, :comment)
                """)
        db.session.execute(sql, {"user_id":user_id, "restaurant_id":restaurant_id, "stars":stars, "comment":comment})
        db.session.commit()

def get_restaurant_info(restaurant_id):
        sql = text("""
                   SELECT id, name, description, address 
                   FROM restaurants WHERE id=:restaurant_id
                """)
        return db.session.execute(sql, {"restaurant_id": restaurant_id}).fetchone()

def get_opening_hours(restaurant_id):
        sql = text("""
              SELECT day, opening, closing 
              FROM openinghours
              WHERE restaurant_id=:restaurant_id
              ORDER BY day
        """
        )
        result = db.session.execute(sql, {"restaurant_id": restaurant_id}).fetchall()
        
        day_names =["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        opening_hours = {}
        for i in result:
                day, opening, closing = i
                day_name = day_names[day]
                opening_hours[day_name] = (opening, closing)
        
        return opening_hours       
        

def get_all_restaurants():
        sql = text("SELECT id, name FROM restaurants ORDER BY name") #MUISTA LISÄTÄ ORDER BY KUN REVIEWS VALMIS
        return db.session.execute(sql).fetchall()

def search(query):        
        sql = text("""
                SELECT r.id, r.name, r.description, r.address
                FROM restaurants r
                LEFT JOIN restaurant_categories rc ON r.id = rc.restaurant_id
                LEFT JOIN categories c ON rc.category_id = c.id
                WHERE r.name ILIKE :query 
                OR r.description ILIKE :query 
                OR r.address ILIKE :query 
                OR c.category ILIKE :query
                """)
        return db.session.execute(sql, {"query":"%"+query+"%"}).fetchall()
        

def name_search(query):
        sql = text("SELECT id, name FROM restaurants WHERE name ILIKE :query")
        return db.session.execute(sql, {"query":"%"+query+"%"}).fetchall()

def add_restaurant(name, description, address, openinghours):
        sql = text("""
                   INSERT INTO restaurants (name, description, address) 
                   VALUES (:name, :description, :address) 
                   RETURNING id
                """)
        restaurant_id = db.session.execute(sql, 
                {"name":name, "description":description, "address":address}).fetchone()[0]
        
        for i in range(7):
                sql = text("""
                        INSERT INTO openinghours (restaurant_id, day, opening, closing)
                        VALUES (:restaurant_id, :day, :opening, :closing) 
                        """)
                day = int(i)
                opening, closing = openinghours[i]
                db.session.execute(sql, {"restaurant_id":restaurant_id, "day":day, "opening":opening, "closing":closing})
        db.session.commit()
        return restaurant_id
