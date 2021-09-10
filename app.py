import hmac
from logging import debug
import sqlite3
import os
import json
from flask import Flask, request, jsonify, flash, redirect, url_for, send_from_directory
from flask.scaffold import F
from flask_mail import Mail, Message
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from werkzeug.utils import secure_filename

from jwt.api_jwt import PyJWT

UPLOAD_FOLDER = './images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class User(object):
    def __init__(self, id, name, surname, email, city, username, password):
        self.id = id
        self.name = name
        self.surname = surname
        self.email = email
        self.city = city
        self.username = username
        self.password = password

    def get_user_object(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'city': self.city,
            'username': self.username,
            'password': self.password
        }


class Book(object):
    def __init__(self, user_id, book_image, book_title, author, description, category, price):
        self.user_id = user_id
        self.book_image = book_image
        self.book_title = book_title
        self.author = author
        self.description = description
        self.category = category
        self.price = price


class Database(object):
    def __init__(self):
        self.db = sqlite3.connect('books_online_api.db')
        self.cursor = self.db.cursor()

    def register_user(self, name, surname, email, city, username, password):
        self.cursor.execute(
            f"INSERT INTO users (surname, name, email, city, username, password) values(?, ?, ?, ?, ?, ?)", [name, surname, email, city, username, password])
        self.db.commit()

    # viewing books based on city
    def view_books_in_city(self, city):
        self.cursor.execute(f"SELECT * FROM books WHERE city = '{city}'")
        self.cursor.fetchall()

    # view by author
    def view_by_author(self, author):
        self.cursor.execute(f"SELECT * FROM books WHERE author = '{author}'")
        self.cursor.fetchall()


def user_table():
    conn = sqlite3.connect('books_online_api.db')
    print('db opened successfully')

    conn.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "name VARCHAR NOT NULL,"
                 "surname VARCHAR NOT NULL,"
                 "email VARCHAR NOT NULL,"
                 "city VARCHAR NOT NULL,"
                 "username VARCHAR NOT NULL,"
                 "password VARCHAR NOT NULL)")
    conn.close()


def book_table():
    conn = sqlite3.connect('books_online_api.db')
    print('db opened successfully')

    conn.execute("CREATE TABLE IF NOT EXISTS books("
                 "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "user_id INTEGER NOT NULL,"
                 "book_image VARCHAR NOT NULL,"
                 "book_title VARCHAR NOT NULL,"
                 "author VARCHAR NOT NULL,"
                 "description VARCHAR NOT NULL,"
                 "category VARCHAR NOT NULL,"
                 "price VARCHAR NOT NULL,"
                 "FOREIGN KEY(user_id) REFERENCES users(id))")
    conn.close()


def payments_table():
    conn = sqlite3.connect('books_online_api.db')
    print('db opened successfully')

    conn.execute("CREATE TABLE IF NOT EXISTS payments("
                 "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "user_id INTEGER NOT NULL,"
                 "address_line_1 VARCHAR NOT NULL,"
                 "address_line_2 VARCHAR NOT NULL,"
                 "city VARCHAR NOT NULL,"
                 "region VARCHAR NOT NULL,"
                 "postal_code VARCHAR NOT NULL,"
                 "country VARCHAR NOT NULL,"
                 "card_number INTEGER NOT NULL,"
                 "card_holder VARCHAR NOT NULL,"
                 "cvv INTEGER NOT NULL,"
                 "expiry_date VARCHAR NOT NULL,"
                 "amount VARCHAR NOT NULL,"
                 "FOREIGN KEY(user_id) REFERENCES users(id))")
    conn.close()

def payments_books_table():
    conn = sqlite3.connect('books_online_api.db')
    print('db opened successfully')

    conn.execute("CREATE TABLE IF NOT EXISTS payments_books("
                 "book_id INTEGER NOT NULL,"
                 "payment_id INTEGER NOT NULL,"
                 "FOREIGN KEY(book_id) REFERENCES books(id),"
                 "FOREIGN KEY(payment_id) REFERENCES payments(id))")
    conn.close()


user_table()
book_table()
payments_table()
payments_books_table()

def identity(payload):
    user_id = payload['identity']
    user = userid_table.get(user_id, None)
    return jsonify({user_id: user.id})


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


# function that fetches all the users from the user table in the Products Database
def fetch_users():
    with sqlite3.connect('books_online_api.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, surname, email, city, username, password FROM users")
        users = cursor.fetchall()
        new_data = []
        #       for loop
        for data in users:
            user = User(data[0], data[1], data[2],
                        data[3], data[4], data[5], data[6])
            new_data.append(user)
    return new_data


# function that fetches the user for login purposes stored in a variable
users = fetch_users()

# variable that are getting the username and id of the users
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

print(username_table)

app = Flask(__name__, static_url_path='/')
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lottogirl92@gmail.com'
app.config['MAIL_PASSWORD'] = 'loahdtTvc473!&'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/protected/')
@jwt_required()
def protected():
    return '%s' % current_identity


def get_user_logged_in(token):
    pyjwt = PyJWT()
    decode_token = pyjwt.decode(token, app.config['SECRET_KEY'], verify=False, algorithms=["hs256"])
    return decode_token["identity"]


@app.route('/registration/', methods=['POST'])
def registration():
    response = {}

    if request.method == "POST":
        name = request.form['first_name']
        surname = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        city = request.form['city']

        database = Database()
        database.register_user(name, surname, email, city, username, password)

        response["status"] = 200
        response["message"] = "User added successfully"
    return response


@app.route('/view_users/', methods=['GET'])
def get_all_users():
    all_users = fetch_users()
    new_users = []
    for user in all_users:
        new_user = user.get_user_object()
        new_users.append(new_user)

    return jsonify(new_users)


@app.route('/view_books/', methods=['GET'])
def view_all_books():
    response = {}

    books = []

    with sqlite3.connect("books_online_api.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT book_title, book_image, author, description, category, price, books.id, user_id, users.city FROM books join users on users.id = books.user_id")
        all_books = cursor.fetchall()

        for book in all_books:
            books.append({
                'title': book[0],
                'filename': book[1],
                'author': book[2],
                'description': book[3],
                'category': book[4],
                'price': book[5],
                'id': book[6],
                'city': book[8]
            })


    response['status_code'] = 200
    response['data'] = books
    return jsonify(response)


@app.route('/view_all_books_by_user/', methods=['GET'])
@jwt_required()
def view_all_books_by_user():
    token = request.headers["Authorization"].replace("JWT ", "")
    user_id = get_user_logged_in(token)
    
    response = {}
    books = []

    with sqlite3.connect("books_online_api.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT book_title, book_image, author, description, category, price, id FROM books where user_id = ?", [user_id])
        all_books = cursor.fetchall()

        for book in all_books:
            books.append({ 'title': book[0], 'filename': book[1], 'author': book[2], 'description': book[3], 'category': book[4], 'price': book[5], 'id': book[6] })

    response['status_code'] = 200
    response['data'] = books
    return jsonify(response)


@app.route('/view_book_by_id/<int:book_id>', methods=['GET'])
def view_book_by_id(book_id):
    response = {}

    book = {}

    with sqlite3.connect("books_online_api.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT book_title, book_image, author, description, category, price, id FROM books where id = ?", [book_id])
        resp = cursor.fetchall()
        all_books = resp[0]

        book['title'] = all_books[0]
        book['filename'] = all_books[1]
        book['author'] = all_books[2]
        book['description'] = all_books[3]
        book['category'] = all_books[4]
        book['price'] = all_books[5]
        book['id'] = all_books[6]

    response['status_code'] = 200
    response['data'] = book
    return jsonify(response)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/add_books/', methods=['POST'])
@jwt_required()
def add_books():
    response = {}

    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if request.method == "POST":
            token = request.headers["Authorization"].replace("JWT ", "")
            user_id = get_user_logged_in(token)
            book_title = request.form['book_title']
            author = request.form['author']
            description = request.form['description']
            category = request.form['category']
            price = request.form['price']

            with sqlite3.connect("books_online_api.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO books (user_id, book_image, book_title, author, description, category, price) values(?, ?, ?, ?, ?, ?, ?)", [
                            user_id, file.filename, book_title, author, description, category, price])
                conn.commit()

                response["status_code"] = 201
                response["message"] = "Book added successfully"
            return response


@app.route("/view_image/<name>", methods=["GET"])
def get_image(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/delete/<int:id>/', methods=['GET'])
def delete_book(id):
    response = {}

    with sqlite3.connect('books_online_api.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = '" + str(id) + "'")
        conn.commit()
        response['status_code'] = 200
        response['message'] = "book deleted successfully."
    return response


@app.route('/edit/<int:id>', methods=['PUT'])
def edit_book(id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('books_online_api.db') as conn:
            incoming_data = dict(request.form)
            put_data = {}

            print(incoming_data)

            if incoming_data.get("book_title") is not None:
                put_data['book_title'] = incoming_data.get('book_title')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE books SET book_title =? WHERE id=?", [put_data["book_title"], id])
                    conn.commit()

                    response["book_title"] = "Content updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("author") is not None:
                put_data['author'] = incoming_data.get('author')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE books SET author =? WHERE id=?", (put_data["author"], id))
                    conn.commit()

                    response["author"] = "Content updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("author") is not None:
                put_data['author'] = incoming_data.get('author')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE books SET author =? WHERE id=?", (put_data["author"], id))
                    conn.commit()

                    response["author"] = "Author updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE books SET description =? WHERE id=?", (put_data["description"], id))
                    conn.commit()

                    response["description"] = "Description updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("category") is not None:
                put_data['category'] = incoming_data.get('category')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE books SET category =? WHERE id=?", (put_data["category"], id))
                    conn.commit()

                    response["category"] = "Category updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE books SET price =? WHERE id=?", (put_data["price"], id))
                    conn.commit()

                    response["price"] = "Price updated successfully"
                    response["status_code"] = 200
    return response


@app.route('/create_payment/', methods=['POST'])
@jwt_required()
def create_payment():
    response = {}

    if request.method == "POST":
        token = request.headers["Authorization"].replace("JWT ", "")
        user_id = get_user_logged_in(token)
        address_line_1 = request.form['address_line_1']
        address_line_2 = request.form['address_line_2']
        city = request.form['city']
        region = request.form['region']
        postal_code = request.form['postal_code']
        country = request.form['country']
        card_number = request.form['card_number']
        card_holder = request.form['card_holder']
        cvv = request.form['cvv']
        expiry_date = request.form['expiry_date']
        total = request.form['total']

        with sqlite3.connect('books_online_api.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO payments (user_id, address_line_1, address_line_2, city, region, postal_code, country, card_number, card_holder, cvv, expiry_date, amount) "
                " values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                , [user_id, address_line_1, address_line_2, city, region, postal_code, country, card_number, card_holder, cvv, expiry_date, total])
            conn.commit()
            payment_id = cursor.lastrowid

        print("request", request.form['books'])
        books = json.loads(request.form['books'])
        print("books", books)

        for book in books:
            with sqlite3.connect('books_online_api.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO payments_books (book_id, payment_id)"
                    " values(?, ?)"
                    , [book['id'], payment_id])
                conn.commit()

        response["status"] = 200
        response["message"] = "User added successfully"
    return response


@app.route('/customer_payments/', methods=['GET'])
@jwt_required()
def payments():
    response = {}
    payments = []

    token = request.headers["Authorization"].replace("JWT ", "")
    user_id = get_user_logged_in(token)

    with sqlite3.connect('books_online_api.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT users.name, users.surname, payments.amount, books.book_title, 'bought' status"
            "from payments_books"
            "join payments on payments.id = payments_books.payment_id"
            "join books on books.id = payments_books.book_id"
            "join users on users.id = books.user_id"
            "users.id = ?"
            , [user_id, user_id]
            )
        all_payments = cursor.fetchall()

        for payment in all_payments:
            payment.append({ 'name': payment[0], 'surname': payment[1], 'amount': payment[2], 'book_title': payment[3] })

        response['status'] = 200
        response['data'] = payments

        conn.commit()

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)