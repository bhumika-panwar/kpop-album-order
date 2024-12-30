from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db , User, Order
from flask_sqlalchemy import SQLAlchemy
import pandas as pd 

app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#read menu form csv using read_csv functin of pandas
df=pd.read_csv('dishes.csv')
shop=df.to_dict('records')#Converts Dataframe to list of dictionary

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shop") #root for showing menu item
def shop_page():
    return render_template("shop.html", shop=shop)

@app.route("/add_to_cart/<int:item_id>")
def add_to_cart(item_id):
    item=next((dish for dish in shop if dish["id"] == item_id), None)
    if item:
        cart = session.get("cart", [] )
        cart.append(item)
        session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/remove_from_cart/<int:item_id>")
def remove_from_cart(item_id):
    cart = session.get("cart", [])
    cart = [item for item in cart if item["id"] != item_id]
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/checkout",methods=["POST"])
def checkout():
    if "user_id" not in session:
        flash("Please log in to place an order.", "warning")
        return redirect(url_for("login"))
    
    cart = session.get("cart",[])
    total = sum(item["price"]for item in cart)
    new_order = Order(user_id=session["user_id"], items=str(cart), total=total)
    db.session.add(new_order)
    db.session.commit()
    session.pop("cart", None)
    return render_template("order_success.html")

@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    total = sum(item["price"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password,method="pbkdf2:sha256")
        new_user = User(username=username,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successfull. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])       
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login Successfull.", "success")
            return redirect(url_for("shop_page"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@app.route("/order_history")
def order_history():
    if "user_id" not in session:
        flash("Please log in to view your order history.", "warning")
        return redirect(url_for("login"))
    orders = Order.query.filter_by(user_id=session["user_id"]).all()
    return render_template("order_history.html", orders=orders)

@app.route("/payment", methods=["GET", "POST"])
def payment():
    if "user_id" not in session:
        flash("Please log in to proceed with payment.", "warning")
        return redirect(url_for("login"))

    cart = session.get("cart", [])
    if not cart:
        flash("Your cart is empty. Please add items to proceed.", "warning")
        return redirect(url_for("cart"))

    total = sum(item["price"] for item in cart)

    if request.method == "POST":
        # Save the order in the database
        new_order = Order(user_id=session["user_id"], items=str(cart), total=total)
        db.session.add(new_order)
        db.session.commit()

        # Clear the cart
        session.pop("cart", None)
        return render_template("order_success.html")

    return render_template("payment.html", total=total)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
