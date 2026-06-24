from flask import Flask, render_template, request, redirect, session, send_from_directory
from models import db, Product, Admin, Wishlist, GoldPrice
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
from flask import jsonify, request
from models import Wishlist

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.secret_key = "MENNA_SECRET_KEY_2026"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///goldshop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# CSS
@app.route('/css/<path:filename>')
def css_files(filename):
    return send_from_directory('css', filename)


# JS
@app.route('/js/<path:filename>')
def js_files(filename):
    return send_from_directory('js', filename)


# IMAGES
@app.route('/images/<path:filename>')
def image_files(filename):
    return send_from_directory('images', filename)


# UPLOADS
@app.route('/uploads/<path:filename>')
def upload_files(filename):
    return send_from_directory('uploads', filename)


# HOME
@app.route("/")
def home():

    prices = GoldPrice.query.first()

    if not prices:

        prices = GoldPrice()

        db.session.add(prices)

        db.session.commit()

    return render_template(
        "index.html",
        prices=prices
    )

@app.route("/test-gold")
def test_gold():

    prices = GoldPrice.query.first()

    if not prices:

        prices = GoldPrice()

        db.session.add(prices)

        db.session.commit()

    return f"""
    24 = {prices.gold24}<br>
    21 = {prices.gold21}<br>
    18 = {prices.gold18}<br>
    pound = {prices.pound}
    """
@app.route("/favorite/<int:product_id>", methods=["POST"])
def favorite(product_id):

    ip = request.remote_addr

    exists = Wishlist.query.filter_by(
        product_id=product_id,
        ip_address=ip
    ).first()

    if exists:
        db.session.delete(exists)
        db.session.commit()
        return jsonify({"status": "removed"})

    fav = Wishlist(
        product_id=product_id,
        ip_address=ip
    )

    db.session.add(fav)
    db.session.commit()

    return jsonify({"status": "added"})

@app.route("/favorites/count/<int:product_id>")
def fav_count(product_id):

    count = Wishlist.query.filter_by(
        product_id=product_id
    ).count()

    return jsonify({"count": count})

# ADMIN
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():

    if "admin" not in session:
        return redirect("/login")

    # إنشاء سجل أسعار الذهب لو مش موجود
    prices = GoldPrice.query.first()

    if not prices:
        prices = GoldPrice()
        db.session.add(prices)
        db.session.commit()

    # إضافة منتج جديد
    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        category = request.form["category"]
        image = request.files["image"]

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        product = Product(
            name=name,
            description=description,
            category=category,
            image=f"uploads/{filename}"
        )

        db.session.add(product)
        db.session.commit()

        return redirect("/admin")

    return render_template(
        "admin.html",
        prices=prices
    )

@app.route("/update-gold", methods=["POST"])
def update_gold():

    if "admin" not in session:
        return redirect("/login")

    prices = GoldPrice.query.first()

    if not prices:
        prices = GoldPrice()
        db.session.add(prices)

    prices.gold24 = float(request.form["gold24"])
    prices.gold21 = float(request.form["gold21"])
    prices.gold18 = float(request.form["gold18"])
    prices.pound = float(request.form["pound"])

    db.session.commit()

    return redirect("/admin")

# PRODUCTS
@app.route("/products")
def products():

    products = Product.query.order_by(Product.id.desc()).all()

    return render_template("products.html", products=products)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/booking")
def booking():
    return render_template("booking.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):

            session["admin"] = admin.id
            return redirect("/admin")

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
   
