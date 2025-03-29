import base64
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from database import *
import bcrypt

app = Flask(__name__)

app.config["SESSION_TYPE"] = 'filesystem'  
app.config['SESSION_PERMANENT'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

Session(app)


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="052005"
)

cursor = conn.cursor()
cursor.execute("use carDB")

@app.route('/')
def index():
    # session = {}
    catalogues = select_all(cursor, "Catalogue")
    catalogues_with_images = []
    for cat in catalogues:
        image_data = base64.b64encode(cat[9]).decode('utf-8')
        image_src = f"data:image/png;base64,{image_data}"
        catalogues_with_images.append((*cat[:9], image_src))
    # print(len(catalogues_with_images))
    return render_template('index.html', catalogues=catalogues_with_images)


@app.route("/filter", methods=["GET"])
def filter():
    order = request.args.get('price_filter')
    catalogues = select_all(cursor, "Catalogue", "price", order)
    catalogues_with_images = []
    for cat in catalogues:
        image_data = base64.b64encode(cat[9]).decode('utf-8')
        image_src = f"data:image/png;base64,{image_data}"
        catalogues_with_images.append((*cat[:9], image_src))
    # print(len(catalogues_with_images))
    return render_template('index.html', session=session, catalogues=catalogues_with_images)
    

@app.route('/login', methods=["POST", "GET"])
def login():
    
    session.clear()

    if request.method == "GET":
        return render_template('login.html')
    usn = request.form.get("username")
    pwd = request.form.get("password")
    user = verify_login(cursor, usn, pwd) # checking if the usn and pwd correct atau nggak
    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect("/")
    return render_template("login.html")


@app.route('/signup', methods=["POST", "GET"])
def signup():
    session.clear()
    if request.method == "GET":
        return render_template('signup.html')
    usn = request.form.get("username")
    pwd = request.form.get("password")
    con_pwd = request.form.get("con_password")
    user = verify_signup(cursor, usn, pwd, con_pwd)
    # print("user:", user)

    if user:
        insert_user(cursor, usn, pwd)
        conn.commit()
        session["user_id"] = cursor.lastrowid
        session["username"] = usn
        return redirect("/")
    return render_template("signup.html", error="Signup failed. Try again.")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/permintaan")
def permintaan():
    if "user_id" not in session or session["username"] != "admin":
        return redirect('/')
    
    requestss = select_all_join(cursor, "Renting", "Catalogue", "Catalogue.id = Renting.catalogue_id")
    return render_template("permintaan.html", requests=requestss)


@app.route("/tambah", methods=["GET", "POST"])
def tambah():
    if request.method == "GET":
        if "user_id" not in session or session["username"] != "admin":
            return redirect("/")
        return render_template("tambah.html")
    brand = request.form.get("brand")
    model = request.form.get("model")
    warna = request.form.get("warna")
    nomor_kendaraan = request.form.get("nomor_kendaraan")
    tahun = request.form.get("tahun")
    kursi = request.form.get("kursi")
    harga = request.form.get("harga")
    availability = request.form.get("availability")
    foto = request.files['foto']

    insert_catalogue(cursor, brand, model, warna, nomor_kendaraan, tahun, kursi, harga, availability, foto.read())
    conn.commit()
    return redirect('/')

@app.route("/edit/<catalogue_id>", methods=["GET", "POST"])
def edit(catalogue_id):
    if "user_id" not in session or session["username"] != "admin":
        return redirect("/")

    if request.method == "GET":
        cursor.execute("SELECT * FROM Catalogue WHERE id = %s", (catalogue_id,))
        catalogue = cursor.fetchone()
        return render_template("edit.html", catalogue=catalogue)

    # Jika metode POST, update data katalog
    brand = request.form.get("brand")
    model = request.form.get("model")
    color = request.form.get("color")
    plate = request.form.get("plate")
    year = request.form.get("year")
    seats = request.form.get("seats")
    price = request.form.get("price")
    availability = request.form.get("availability")

    update_columns(cursor, catalogue_id, ["brand", "model", "color", "plate", "year", "seats", "price", "availability"],
                   [brand, model, color, plate, year, seats, price, availability])
    conn.commit()
    
    return redirect("/")


@app.route("/delete/<catalogue_id>")
def delete(catalogue_id):
    if "user_id" not in session or session["username"] != "admin":
        return redirect("/")

    delete_catalogue(cursor, catalogue_id)
    conn.commit()
    return redirect("/")


@app.route("/sewa/<catalogue_id>", methods=["GET", "POST"])
def sewa(catalogue_id):
    
    if request.method == "GET":
        if "user_id" not in session:
            return redirect("/")
        car = select_one(cursor, "Catalogue", catalogue_id)
        return render_template("sewa.html", catalogue_id=catalogue_id, car=car)
    
    user_id = session["user_id"]
    name = request.form["name"]
    contact_number = request.form["contact_number"]
    address = request.form["address"]
    start_date = request.form["start_date"]
    period = request.form["period"]

    #TODO tambahkan juga verify
    insert_rent(cursor, user_id, catalogue_id, name, contact_number, address, start_date, period)
    conn.commit()

    return redirect('/')

@app.route("/update_status", methods=["POST"])
def update_status():
    request_id = request.form["request_id"]
    new_status = request.form["status"]

    #TODO perlu ada verify atau nggak ya?
    cursor.execute("UPDATE Renting SET status = %s WHERE id = %s", (new_status, request_id))
    conn.commit()
    return redirect("/permintaan")

@app.route("/riwayat")
def riwayat():
    if "user_id" not in session:
        return redirect('/')
    
    requestss = select_all_join(cursor, "Renting", "Catalogue", "Catalogue.id = Renting.catalogue_id", f"Renting.user_id = {session['user_id']}")
    return render_template("permintaan.html", requests=requestss)
    