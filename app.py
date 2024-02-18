from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from datetime import datetime
from werkzeug.utils import secure_filename
import os
UPLOAD_FOLDER = 'static/uploads/'
app = Flask(__name__)
app.app_context().push()

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "items-database.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
Session(app)
db = SQLAlchemy(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Account(db.Model):
    username = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime('%B %d %Y'))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


class Product(db.Model):
    username = mapped_column(ForeignKey(Account.username))
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.String, nullable=False, default=datetime.utcnow().strftime('%B %d %Y'))
    picture = db.Column(db.String)
    size = db.Column(db.String, nullable=False)
    is_eco = db.Column(db.String)

    def __init__(self, username, name, gender, type, description, price, picture, size, is_eco):
        self.username = username
        self.name = name
        self.type = type
        self.description = description
        self.price = price
        self.picture = picture
        self.gender = gender
        self.size = size
        self.is_eco = is_eco

    def __repr__(self):
        return '<Product %r>' % self.username


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.form.get("name") and request.form.get("psw") and request.form.get("psw_repeat"):
            existing_user = Account.query.filter_by(username=request.form.get("name")).first()
            if not existing_user:
                if request.form.get("psw") == request.form.get("psw_repeat"):
                    user = Account(username=request.form.get("name"), password=request.form.get("psw"))
                    db.session.add(user)
                    db.session.commit()
                    return redirect("/")
                else:
                    print("Passwords don't match")
                    return redirect("#register")
            else:
                print("User already exists")
                return redirect("#register")
        else:
            print("You left some windows empty")
            return redirect("#register")
    return redirect("/")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if request.form.get("name") and request.form.get("psw"):
            existing_user = Account.query.filter_by(username=request.form.get("name")).first()
            if existing_user:
                if request.form.get("psw") == existing_user.password:
                    session["name"] = request.form.get("name")
                else:
                    print("Password doesnt match")
                    return redirect("#login")
            else:
                print("user doesn't exist")
                return redirect("#login")
        else:
            print("You left some windows empty")
            return redirect("#login")
    return redirect("/")


@app.route("/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        session["name"] = None
    return redirect("/")


def is_bio(text):
    text = text.lower()
    materials_bio = ["bawelna", "bawełna", "biodegra", "konop"]
    start_index = text.find("materia")
    if start_index == -1:
        return False  # Jeśli nie ma słowa "materia" w tekście, zwracamy False
    start_index += 9  # Przesunięcie indeksu o 8, aby zacząć od materiałów
    end_index = len(text)
    result_text = text[start_index:end_index].split()
    procent_sum = 0
    bio_limit = 50

    if len(result_text) % 2 == 1:
        result_text = result_text[:-1]

    for i in range(0, len(result_text), 2):
        i_1 = result_text[i]
        i_2 = result_text[i + 1]

        procent = 0
        for material in materials_bio:
            if material in i_1:
                procent_str = i_2.strip('%,')
                if procent_str.isdigit():
                    procent = int(procent_str)
                else:
                    procent = 0
            if material in i_2:
                procent_str = i_1.strip('%,')
                if procent_str.isdigit():
                    procent = int(procent_str)
                else:
                    procent = 0

        procent_sum += procent

    if procent_sum >= bio_limit:
        return True
    return False


@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        if request.form.get("name") and request.form.get("description") and request.form.get("type") and request.form.get("price") and request.form.get("size"):
            image = request.files.get("picture", None)
            print(image.filename)
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                if is_bio(request.form.get("description")):
                    product = Product(username=session["name"], name=request.form.get("name"),
                                      description=request.form.get("description"),
                                      type=request.form.get("type"), price=request.form.get("price"),
                                      picture=filename, gender=request.form.get("gender"), size=request.form.get("size"), is_eco="True")
                else:
                    product = Product(username=session["name"], name=request.form.get("name"),
                                      description=request.form.get("description"),
                                      type=request.form.get("type"), price=request.form.get("price"),
                                      picture=filename, gender=request.form.get("gender"), size=request.form.get("size"), is_eco=None)
                db.session.add(product)
                db.session.commit()
            else:
                return redirect('#create')
        else:
            print("You left some windows empty")
            return redirect("#create")
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    if request.method == "POST":
        for name in request.form.getlist('checked_delete[]'):
            item = Product.query.filter_by(username=session["name"], name=name).first()
            db.session.delete(item)
            db.session.commit()
    return redirect("/user")


@app.route("/user", methods=["POST", "GET"])
def user():
    products = Product.query.filter_by(username=session["name"])
    return render_template("userpage.html", products=products)


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        products = Product.query.filter(Product.name.contains(request.form.get("search")))
        return render_template("index.html", products=products)
    else:
        return redirect("/")


@app.route("/product_page", methods=["GET", "POST"])
def product_page():
    if request.form:
        id = request.form.get('id')
        product = Product.query.filter_by(id=id)
        return render_template("product_template.html", products=product)


@app.route("/", methods=["GET", "POST"])
def home():
    products = Product.query.all()
    return render_template("index.html", products=products)


if __name__ == "__main__":
    app.run(debug=True)