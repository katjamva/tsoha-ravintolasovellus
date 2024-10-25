from flask import Flask
from app import app
import users 
import restaurants
from users import admin_required, promote_to_admin
from flask import render_template, request, redirect, url_for
from sqlalchemy.sql import text
from flask import render_template


@app.route("/remove_review", methods=["POST"])
@users.admin_required
def remove_review():
    if request.method == "POST":
        users.check_csrf()
        selected_reviews = request.form.getlist("review_id")
        print("Selected review IDs:", selected_reviews)  

        for review_id in selected_reviews:
            try:
                restaurants.remove_review(review_id)
            except ValueError:
                print(f"Invalid review ID: {review_id}")

        return redirect("/")
    return render_template("restaurant.html")


@app.route("/categoryedit", methods=["GET", "POST"])
def edit_categories():
    users.admin_required("admin") 

    if request.method == "GET":
        categories = restaurants.get_all_categories()
        return render_template("categoryedit.html", categories=categories)

    if request.method == "POST":
        users.check_csrf()
        action = request.form.get("action")

        if action == "Update":
            for category in restaurants.get_all_categories():
                new_name = request.form.get(f"new_name_{category.id}")
                if new_name and new_name != category.category:
                    restaurants.update_category_name(category.id, new_name)
            return redirect("/categoryedit")

        elif action == "Delete Selected":
            delete_ids = request.form.getlist("delete_ids")
            if delete_ids:
                delete_ids = list(map(int, delete_ids))  
                restaurants.remove_category(delete_ids)
            return redirect("/categoryedit")

    return render_template("error.html", message="Unknown action")


@app.route("/edit/<int:restaurant_id>", methods=["GET", "POST"])
def edit(restaurant_id):
    users.admin_required("admin")
    
    if request.method == "GET":
        restaurant = restaurants.get_restaurant_info(restaurant_id)
        opening_hours = restaurants.get_opening_hours(restaurant_id)
        categories = restaurants.get_all_categories()  
        selected_categories = restaurants.get_categories_for_restaurant(restaurant_id)
        selected_category_ids = [category[0] for category in selected_categories]
        
        return render_template("edit.html", 
                               restaurant=restaurant, 
                               opening_hours=opening_hours, 
                               categories=categories, 
                               selected_category_ids=selected_category_ids)

    if request.method == "POST":
        users.check_csrf()
        
        name = request.form["name"]
        if len(name) < 1 or len(name) > 20:
            return render_template("error.html", message="Name must be 1-20 characters", restaurant_id=restaurant_id)
        
        description = request.form["description"]
        if len(description) > 1500:
            return render_template("error.html", message="Description too long, max 1500 characters", restaurant_id=restaurant_id)

        address = request.form["address"]
        if len(address) < 5 or len(address) > 200:
            return render_template("error.html", message="Address must be between 5 and 200 characters", restaurant_id=restaurant_id)

        opening_hours = []
        for i in range(7):
            opening = request.form.get(f"opening_{i}")
            closing = request.form.get(f"closing_{i}")
            if not opening and not closing:
                opening_hours.append((None, None))
            elif not opening or not closing:
                return render_template("error.html", message="You can't leave one of the times empty.", restaurant_id=restaurant_id)
            else:
                opening_hours.append((opening, closing))

        restaurants.edit(restaurant_id, name, description, address)
        
        selected_categories = request.form.getlist("categories")
        restaurants.update_restaurant_categories(restaurant_id, selected_categories)
        
        new_category = request.form.get("new_category")
        add_new_category = request.form.get("add_new_category")
        if new_category and add_new_category == "yes":
            new_category_id = restaurants.add_category(new_category)
            if new_category_id:
                restaurants.add_restaurant_category(restaurant_id, new_category_id)
            else:
                return render_template("error.html", message="Failed to add the new category.", restaurant_id=restaurant_id)
    
        for i in range(7):
            opening, closing = opening_hours[i]
            restaurants.edit_openinghours(restaurant_id, opening, closing, i)
        
        return redirect("/restaurant/" + str(restaurant_id))


@app.route("/review", methods=["POST"])
def review():
    users.check_csrf
    
    restaurant_id = request.form["restaurant_id"]
    stars = int(request.form["stars"])
    if stars < 1 or stars > 5:
        return render_template("error.html", message="False amount of stars")

    comment = request.form["comment"]
    if len(comment) > 1000:
        return render_template("error.html", message="Comment too long")
    if comment == "":
        comment ="-"
        
    restaurants.add_review(users.user_id(), restaurant_id, stars, comment)
    
    return redirect("/restaurant/"+str(restaurant_id))
        
@app.route("/restaurant/<int:restaurant_id>")
def show_restaurant(restaurant_id):
    info = restaurants.get_restaurant_info(restaurant_id)
    
    opening_hours = restaurants.get_opening_hours(restaurant_id)
    
    reviews = restaurants.get_reviews(restaurant_id)
    
    average_rating = restaurants.rating(restaurant_id)
    
    categories = restaurants.get_categories_for_restaurant(restaurant_id)
    
    
    return render_template("restaurant.html", id=restaurant_id, 
                           name=info[1], categories=categories,
                           description=info[2], address=info[3], 
                           opening_hours=opening_hours, reviews=reviews, 
                           average_rating=average_rating)
    
@app.route("/name_search", methods=["GET", "POST"])
@users.admin_required
def name_search():
    query = request.form.get("query")
    results = restaurants.name_search(query)
    return render_template("remove.html", restaurants=results, query=query)
    

@app.route("/search", methods=["GET"])
def search():
    query = request.args["query"]
    results = restaurants.search(query)
    return render_template("search_results.html", restaurants=results, query=query)



@app.route("/remove", methods=["GET", "POST"])
@users.admin_required
def remove_restaurant():
    if request.method == "POST":
        users.check_csrf()
        selected_restaurants = request.form["restaurant"]
        for restaurant_id in selected_restaurants:
            restaurants.remove_restaurant(restaurant_id)
        return redirect("/")
    return render_template("remove.html")


@app.route("/add", methods=["GET", "POST"])
def add_restaurant():
    users.admin_required("admin")
    
    if request.method == "GET":
        categories = restaurants.get_all_categories()  
        return render_template("add.html", categories=categories)
    
    if request.method == "POST":
        users.check_csrf()
        
        name = request.form["name"]
        if len(name) < 1 or len(name) > 20:
            return render_template("error.html", message="Name must be 1-20 characters")
        
        description = request.form["description"]
        if len(description)>1500:
            return render_template("error.html", message="Description too long, max 1500 characters") 
        
        address = request.form["address"]
        if len(address) < 5 or len(address) > 200:
            return render_template("error.html", message="Address can't be less than 5 or more than 200 characters")        
        #https://www.geeksforgeeks.org/retrieving-html-from-data-using-flask/
        opening_hours = []

        for i in range(7):
            opening = request.form.get(f"opening_{i}")
            closing = request.form.get(f"closing_{i}")
            print(f"Day {i}: Opening: {opening}, Closing: {closing}")
            
            if not opening and not closing:
                opening_hours.append((None, None))  
            elif not opening or not closing:
                return render_template("error.html", message="You can't have either of the times empty")
            else:
                opening_hours.append((opening, closing))

        restaurant_id = restaurants.add_restaurant(name, description, address, opening_hours)
        
        selected_categories = request.form.getlist("categories")
        for category_id in selected_categories:
            restaurants.add_restaurant_category(restaurant_id, category_id)
            
        new_category = request.form.get("new_category")
        if new_category:
            restaurants.add_category(new_category)
            
        return redirect("/")#+str(restaurant_id))

@app.route("/", methods=["GET","POST"])
def index():
    result = restaurants.get_top_10()
    return render_template("index.html", restaurants=result)


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
        
        if not users.register(username, password1, "user"):  
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

#@app.route("/admin/rights/<username>")
#users.admin_required
#def grant_admin_rights(username):
#    users.promote_to_admin(username)
 #   return f"User {username} has been promoted to admin."
        
        