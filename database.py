import mysql.connector
from mysql.connector import Error
import bcrypt
import csv

#TODO update karena ada fungsi baru insert_template_catalogue dan insert_rent, select_one, select_all_join
"""Nama fungsi dan parameternya:
1. readfile(filename)
2. create_database(cursor)
3. create_tbcatalogue(cursor)
4. create_tbuser(cursor)
5. create_tbrenting(cursor)
6. insert_catalogue(cursor) -> semua image formatnya .jpeg
7. insert_user(cursor, username, password)
8. verify_user(cursor, username, password)
9. update_catalogue(cursor, catalogue_id, column, new_value) -> ini cuma bisa edit 1 kolom, perlu bikin bisa edit banyak kolom ga?
10. delete_catalogue(cursor, catalogue_id)
- select_all(cursor, table)
- drop_database(cursor)
"""

def readfile(filename):
    lines = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(line.replace("\n", "").split(","))
    return lines[1:]


def create_database(cursor):
    try:
        cursor.execute("create database if not exists carDB")
        print("database created")
    except Error as e:
        print(e)
    cursor.execute("use carDB")


def create_tbcatalogue(cursor):
    try:
        cursor.execute("""create table if not exists Catalogue (
                       id int primary key auto_increment not null,
                       brand varchar(31),
                       model varchar(31),
                       color varchar(31),
                       plate varchar(31),
                       year year,
                       seats int,
                       price int,
                       availability enum("Yes", "No"),
                       image mediumblob
                       )""")
        print("table Catalogue created")
    except Error as e:
        print(e)


def create_tbuser(cursor):
    try:
        cursor.execute("""create table if not exists User (
                       id int auto_increment primary key,
                       username varchar(31) unique,
                       password varchar(100)
                       )""")
        print("table User created")
    except Error as e:
        print(e)


def create_tbrenting(cursor):
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS Renting (
                           id int primary key auto_increment,
                           user_id INT,
                           catalogue_id INT,
                           name VARCHAR(255),
                           contact_number VARCHAR(20),
                           address VARCHAR(255),
                           start_date DATE,
                           period INT,
                           status ENUM('Pending', 'Accepted', 'Rejected') DEFAULT 'Pending', -- Tambah default
                           FOREIGN KEY (user_id) REFERENCES User(id),
                           FOREIGN KEY (catalogue_id) REFERENCES Catalogue(id)
                       )""")
        print("Table Renting created")
    except Error as e:
        print(f"Error: {e}")


def insert_template_catalogue(cursor):
    lines = readfile("catalogue.csv")
    new_lines = []

    for line in lines:
        id, brand, model, color, plate, year, seats, price, availability = line
        binary_data = None
        img_path = f"catalogue_img/{line[0]}.jpeg"
        with open(img_path, "rb") as file:
            binary_data = file.read()

        new_lines.append([brand, model, color, plate, year, seats, price, availability, binary_data])
    
    string = """
    INSERT INTO Catalogue (brand, model, color, plate, year, seats, price, availability, image)
    VALUES ({})""".format(", ".join(["%s"] * 9))

    try:
        cursor.executemany(string, new_lines)
        print("data inserted into catalogue")
    except Error as e:
        print("Error:", e)


def insert_catalogue(cursor, brand, model, color, plate, year, seats, price, availability, image): 
    string = """
    INSERT INTO Catalogue (brand, model, color, plate, year, seats, price, availability, image)
    VALUES ({})""".format(", ".join(["%s"] * 9))

    try:
        cursor.execute(string, (brand, model, color, plate, year, seats, price, availability, image))
        print("data inserted into catalogue")
    except Error as e:
        print("Error:", e)


def insert_rent(cursor, user_id, catalogue_id, name, contact_number, address, start_date, period):
    string = """
    INSERT INTO Renting (user_id, catalogue_id, name, contact_number, address, start_date, period)
    VALUES ({})""".format(", ".join(["%s"] * 7))

    try:
        cursor.execute(string, (user_id, catalogue_id, name, contact_number, address, start_date, period))
        print("Data inserted into Renting")
    except Error as e:
        print("Error:", e)


def insert_user(cursor, username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    print(hashed_password)
    query = "insert into User (username, password) values (%s, %s)"
    
    try:
        cursor.execute(query, (username, hashed_password))
        print("User added successfully!")
    except Error as e:
        print("Error:", e)


def verify_login(cursor, username, password):
    query = "SELECT id, password FROM User WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    if result and bcrypt.checkpw(password.encode(), result[1].encode()):  # result[1] adalah password
        print("Login successful!")
        return {"id": result[0], "username": username}  # result[0] adalah id
    else:
        print("Invalid username or password")
        return None


def verify_signup(cursor, username, password, con_password):
    query = "select username from user where username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchall()
    if result:
        print("Username exists, please log in.")
        return False
    if password != con_password:
        print("Password does not match.")
        return False
        
    return True


def update_column(cursor, catalogue_id, column, new_value):
    try:
        query = f"update Catalogue set {column} = %s where id = %s"
        cursor.execute(query, (new_value, catalogue_id))
        print("table Catalogue updated")
    except Error as e:
        print("Error:", e)


def update_columns(cursor, catalogue_id, columns, new_values):
    string = ", ".join([f"{col} = %s" for col in columns])
    try:
        query = f"update Catalogue set {string} where id = %s"
        print(query)
        cursor.execute(query, (*new_values, catalogue_id))
        print("table Catalogue updated")
    except Error as e:
        print("Error:", e)


def delete_catalogue(cursor, catalogue_id):
    try:
        cursor.execute("delete from Renting where catalogue_id = %s", (catalogue_id,))
        cursor.execute("delete from Catalogue where id = %s", (catalogue_id,))
        print("catalogue and related rentings deleted")
    except Error as e:
        print("Error:", e)

def select_one(cursor, table, id):
    cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (id,))
    data = cursor.fetchone()
    return data


def select_all(cursor, table, order_by=None, order="ASC"):
    query = f"SELECT * FROM {table}"
    
    if order_by:
        query += f" ORDER BY {order_by} {order}"
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    return data


def select_all_join(cursor, table1, table2, on_condition, where_condition=None):
    query = f"SELECT * FROM {table1} JOIN {table2} ON {on_condition}"
    
    if where_condition:
        query += f" WHERE {where_condition}"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def drop_database(cursor):
    cursor.execute(f"drop database carDB")