from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DB
import re
from flask import flash
from flask_app.models import location


ALPHA = re.compile(r"^[a-zA-Z]+$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")
ALPHANUMERIC = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
)


class User:
    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.locations = []

    @classmethod
    def create(cls, data):
        query = """INSERT INTO users (first_name, last_name, email, password)
                VALUES ( %(first_name)s, %(last_name)s, %(email)s, %(password)s );"""
        results = connectToMySQL(DB).query_db(query, data)
        return results

    @classmethod
    def get_by_id(cls, data):
        query = """SELECT * FROM users
                WHERE id = %(id)s;"""
        results = connectToMySQL(DB).query_db(query, data)
        if results:
            return cls(results[0])
        return False

    @classmethod
    def get_by_email(cls, data):
        query = """SELECT * FROM users
                WHERE email = %(email)s;"""
        results = connectToMySQL(DB).query_db(query, data)
        if results:
            return cls(results[0])
        return False

    @classmethod
    def get_users_with_locations(cls, data):
        query = """
                 SELECT * FROM users
                LEFT JOIN favorites ON favorites.user_id = users.id
                LEFT JOIN locations ON favorites.location_id = locations.id
                WHERE users.id = %(id)s;   
        """
        results = connectToMySQL(DB).query_db(query, data)
        users = {}

        for row in results:
            user_id = row["id"]
            if user_id not in users:
                user_data = {
                    "id": user_id,
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "created_at": row["created_at"],
                    "locations": [],
                }
                users[user_id] = user_data

            location_data = {
                "location_id": row["location_id"],
                "name": row["name"],
                "state": row["state"],
                "distance": row["distance"],
                "difficulty_level": row["difficulty_level"],
                "created_at": row["created_at"],
            }
            users[user_id]["locations"].append(location_data)

        return list(users.values())

    @classmethod
    def get_favorite_location_id(cls, user_id):
        query = """SELECT location_id FROM favorites WHERE user_id = %(user_id)s;"""
        data = {"user_id": user_id}
        results = connectToMySQL(DB).query_db(query, data)
        return [result["location_id"] for result in results]

    @classmethod
    def update_user(cls, data):
        query = """UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s, password = %(password)s
                WHERE users.id = %(id)s;"""
        return connectToMySQL(DB).query_db(query, data)

    @staticmethod
    def validate_data(data):
        is_valid = True
        if len(data["first_name"]) < 1:
            is_valid = False
            flash("First name required", "registration")
        elif len(data["first_name"]) < 2:
            is_valid = False
            flash("First name must be at least 2 characters", "registration")
        elif not ALPHA.match(data["first_name"]):
            is_valid = False
            flash("First name must be letters only", "registration")
        if len(data["last_name"]) < 1:
            is_valid = False
            flash("Last name required", "registration")
        elif len(data["last_name"]) < 2:
            is_valid = False
            flash("Last name must be at least 2 characters", "registration")
        elif not ALPHA.match(data["last_name"]):
            is_valid = False
            flash("Last name must be letters only", "registration")
        if len(data["email"]) < 1:
            is_valid = False
            flash("Email required", "registration")
        elif not EMAIL_REGEX.match(data["email"]):
            is_valid = False
            flash("Email must be a valid format", "registration")
        else:
            user_data = {"email": data["email"]}
            potiential_user = User.get_by_email(user_data)
            if potiential_user:
                flash("Email already exists!", "registration")
                is_valid = False
        if len(data["password"]) < 1:
            is_valid = False
            flash("Password required", "registration")
        elif len(data["password"]) < 8:
            is_valid = False
            flash("Password must be at least 8 characters", "registration")
        elif data["password"] != data["confirm_password"]:
            is_valid = False
            flash("Password does not match!", "registration")
        elif not ALPHANUMERIC.match(data["password"]):
            is_valid = False
            flash(
                "Password must have at least one number and one Uppercase letter",
                "registration",
            )
        
        return is_valid
