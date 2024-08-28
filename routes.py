from flask import Flask
from app import app
import users 
import restaurants
from users import admin_required, promote_to_admin
from flask import render_template, request, redirect, url_for



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
    
    reviews = restaurants.get_reviews(restaurant_id)
    
    return render_template("restaurant.html", id=restaurant_id, name=info[1], cuisine=info[2], description=info[3], location=info[4], opening_hours=info[5], reviews=reviews)
    
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

@app.route("/remove_review", methods=["POST"])
@users.admin_required
def remove_review():
    if request.method == "POST":
        users.check_csrf()
        # Retrieve the list of selected review IDs
        selected_reviews = request.form.getlist("review_ids")
        print("Selected review IDs:", selected_reviews)  # Debug print

        for review_id in selected_reviews:
            try:
                restaurants.remove_review(review_id)
            except ValueError:
                print(f"Invalid review ID: {review_id}")

        return redirect("/")
    return render_template("restaurant.html")


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
        return render_template("add.html")
    
    if request.method == "POST":
        users.check_csrf()
        
    name = request.form["name"]
    if len(name) < 1 or len(name) > 20:
        return render_template("error.html", message="Name must be 1-20 characters")
    
    cuisine = request.form["cuisine"]
    if len(cuisine) < 3 or len(cuisine) > 200:
        return render_template("error.html", message="Cuisine can't be less than 5 or more than 200 characters")
    
    
    description = request.form["description"]
    if len(description)>1500:
        return render_template("error.html", message="Description too long, max 1500 characters") 
    
    location = request.form["location"]
    if len(location) < 5 or len(location) > 200:
        return render_template("error.html", message="Location can't be less than 5 or more than 200 characters")
    
    opening_hours = request.form["opening_hours"]
    if len(opening_hours) < 10 or len(opening_hours) > 100:
        return render_template("error.html", message="Opening hours can't be less than 10 or more than 100 characters long")
    

    restaurant_id = restaurants.add_restaurant(name, cuisine, description, opening_hours, location) 
    return redirect("/")#+str(restaurant_id))

@app.route("/", methods=['GET','POST'])
def index():
    return render_template("index.html", restaurants=restaurants.get_all_restaurants())

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
        
        