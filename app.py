import hmac
from logging import debug
import sqlite3
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS

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
        self.cursor.execute(f"INSERT INTO users (surname, name, email, city, username, password) values('{name}', '{surname}', '{email}', '{city}', '{username}', '{password}')")
        self.db.commit()

    # viewing books based on city 
    def view_books_in_city(self, city):
        self.cursor.execute(f"SELECT * FROM books WHERE city = '{city}'")
        self.cursor.fetchall()

    # viewing all books from everyone everywhere
    

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

# def user_profiles():
#     conn = sqlite3.connect('books_online_api.db')

#     conn.execute("CREATE TABLE IF NOT EXISTS user_profiles("
#                  "id INTEGER PRIMARY KEY AUTOINCREMENT,"
#                  "user_id INTEGER NOT NULL,"
#                  "book_image TEXT NOT NULL,"
#                  "book_title TEXT NOT NULL,"
#                  "author TEXT NOT NULL,"
#                  "description TEXT NOT NULL,"
#                  "category TEXT NOT NULL,"
#                  "price TEXT NOT NULL,"
#                  "FOREIGN KEY(user_id) REFERENCES users(id))")
#     conn.close()

user_table()
book_table()

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


# function that fetches all the users from the user table in the Products Database
def fetch_users():
    with sqlite3.connect('books_online_api.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, surname, email, city, username, password FROM users")
        users = cursor.fetchall()
        new_data = []
        #       for loop
        for data in users:
            user = User(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
            new_data.append(user)
    return new_data


# function that fetches the user for login purposes stored in a variable
users = fetch_users()

# variable that are getting the username and id of the users
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

app = Flask(__name__)
CORS(app)
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


@app.route('/registration/', methods=['POST'])
def registration():
    response = {}

    if request.method == "POST":
        name = request.form['name']
        surname = request.form['surname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        city = request.form['city']

        print(request.json)
        
        database = Database()
        database.register_user(name, surname, email, city, username, password)


        with sqlite3.connect("books_online_api.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users VALUES(null,"
                           "'" + name + "',"
                                "'" + surname + "',"
                                    "'" + email + "',"
                                        "'" + city + "',"
                                            "'" + username + "',"
                                                 "'" + password + "')")


        response["status"] = 200
        response["message"] = "User added successfully"
    elif request.method == "POST":
        name = request.json['name']
        surname = request.json['surname']
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']
        city = request.json['city']

        print(request.json)
        
        database = Database()
        database.register_user(name, surname, email, city, username, password)

        with sqlite3.connect("books_online_api.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users VALUES(null,"
                           "'" + name + "',"
                                "'" + surname + "',"
                                    "'" + email + "',"
                                        "'" + city + "',"
                                            "'" + username + "',"
                                                 "'" + password + "')")

        response["status"] = 200
        response["message"] = "User added successfully"

    # if response["status_code"] == 201:
    #             msg = Message('Registration Successful', sender='lottogirl92@gmail.com', recipients=[email])
    #             msg.body = "Welcome '" + str(name) + "', You have Successfully Registered as a user of this app"
    #             mail.send(msg)
    #             return "Sent email"
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

    with sqlite3.connect("books_online_api.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        all_books = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = all_books
    return jsonify(response)    

@app.route('/add_books/', methods=['POST'])
# @jwt_required()
def add_books():
    response = {}

    if request.method == "POST":
        user_id = request.form['user_id']
        book_image = request.form['book_image']
        book_title = request.form['book_title']
        author = request.form['author']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']   

        with sqlite3.connect("books_online_api.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (user_id, book_image, book_title, author, description, category, price) values(?, ?, ?, ?, ?, ?, ?)", [user_id, book_image, book_title, author, description, category, price])
            conn.commit()
            
            response["status_code"] = 201
            response["message"] = "Book added successfully"
        return response


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
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("book_image") is not None:
                put_data["book_image"] = incoming_data.get("book_image")
                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET book_image =? WHERE id=?", (put_data["book_image"], id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200
            if incoming_data.get("book_title") is not None:
                put_data['book_title'] = incoming_data.get('book_title')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET book_title =? WHERE id=?", (put_data["book_title"], id))
                    conn.commit()

                    response["book_title"] = "Content updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("author") is not None:
                put_data['author'] = incoming_data.get('author')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET author =? WHERE id=?", (put_data["author"], id))
                    conn.commit()

                    response["author"] = "Content updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("author") is not None:
                put_data['author'] = incoming_data.get('author')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET author =? WHERE id=?", (put_data["author"], id))
                    conn.commit()

                    response["author"] = "Author updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET description =? WHERE id=?", (put_data["description"], id))
                    conn.commit()

                    response["description"] = "Description updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("category") is not None:
                put_data['category'] = incoming_data.get('category')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET category =? WHERE id=?", (put_data["category"], id))
                    conn.commit()

                    response["category"] = "Category updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('books_online_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET price =? WHERE id=?", (put_data["price"], id))
                    conn.commit()

                    response["price"] = "Price updated successfully"
                    response["status_code"] = 200
    return response

# @app.route('/view_books_by_city/<string:city>/', methods=['GET'])
# def view_books_city(city):
#     response = {}

#     with sqlite3.connect("books_online_api.db") as conn:
#         cursor = conn.cursor()
#         city = cursor.execute("SELECT * FROM users WHERE city = '"+ city +"' ")
#         all_books = cursor.fetchall()

#     response['status_code'] = 200
#     response['data'] = all_books
#     return jsonify(response) 


if __name__ == "__main__":
    app.run(debug=True)
