from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DB
from flask import flash
import re
from flask_app.models import user

ALPHA = re.compile(r"^[a-zA-Z ]+$")

class Location:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.state = data['state']
        self.distance = data['distance']
        self.difficulty_level = data['difficulty_level']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.users = []

    @classmethod
    def create(cls ,data):
        query = """INSERT INTO locations (name, state, distance, difficulty_level, user_id, created_at)
                VALUES ( %(name)s, %(state)s, %(distance)s, %(difficulty_level)s, %(user_id)s, NOW() );"""
        results = connectToMySQL(DB).query_db(query, data)
        return results
    
    @classmethod
    def get_all_locations(cls):
        query = """ SELECT * FROM locations JOIN users ON locations.user_id = users.id ORDER BY locations.created_at DESC;"""
        results = connectToMySQL(DB).query_db(query)
        all_locations = []
        if results:
            for row in results:
                this_location = cls(row)
                user_data = {
                    **row,
                    'id' : row['users.id'],
                    'created_at' : row ['created_at'],
                    'updated_at' : row ['updated_at']
                }
                this_user = user.User(user_data)
                this_location.data = this_user
                all_locations.append(this_location)
        return all_locations
    
    @classmethod
    def get_users_with_locations(cls, data):
        query = """
                SELECT * FROM users LEFT JOIN favorites ON favorites.user_id = users.id
                LEFT JOIN locations ON favorites.location_id = locations.id WHERE users.id = %(id)s;       
        """
        results = connectToMySQL(DB).query_db(query, data)
        all_locations = []
        if results:
            for row in results:
                this_location = cls(row)
                user_data = {
                    **row,
                    'id' : row['users.id'],
                    'created_at' : row ['created_at'],
                    'updated_at' : row ['updated_at']
                }
                this_user = user.User(user_data)
                this_location.data = this_user
                all_locations.append(this_location)
        return all_locations

    
    @classmethod
    def get_one_location(cls, data):
        query = """ SELECT * FROM locations JOIN users ON locations.user_id = users.id
                WHERE locations.id = %(id)s;"""
        results = connectToMySQL(DB).query_db(query, data)
        if results:
            row = results[0]
            this_location = cls (row)
            user_data = {
                **row,
                'id' : row['users.id'],
                'created_at' : row ['created_at'],
                'updated_at' : row ['updated_at']
            }
            this_user = user.User(user_data)
            this_location.data = this_user
            return this_location
        return False
    
    @classmethod
    def update_location(cls, data):
        query = """
                UPDATE locations SET name = %(name)s,
                state = %(state)s,
                distance = %(distance)s,
                difficulty_level = %(difficulty_level)s
                WHERE locations.id = %(id)s;
        """
        return connectToMySQL(DB).query_db(query, data)
    
    @classmethod
    def add_to_favorites(cls, data):
        query = """INSERT INTO favorites (user_id, location_id) VALUES (%(user_id)s, %(location_id)s);"""
        return connectToMySQL(DB).query_db(query,data)


    @classmethod
    def delete_location(cls, data):
        query = "DELETE FROM locations WHERE id = %(id)s;"
        return connectToMySQL(DB).query_db(query, data)

    @staticmethod
    def validate_data (data):
        is_valid = True
        if len(data['name']) < 1:
            is_valid = False
            flash ('Name is required', 'location')
        elif len(data['name']) < 2:
            is_valid = False
            flash ('Name must be at least 2 characters', 'location')
        elif not ALPHA.match(data['name']):
            is_valid = False
            flash ('Name must be letters only', 'location')
        if len(data['state']) < 1:
            is_valid = False
            flash ('State is required', 'location')
        elif not ALPHA.match(data['state']):
            is_valid = False
            flash ('State must be letters only', 'location')
        if len(data['distance']) < 1:
            is_valid = False
            flash ('Distance is required', 'location')
        if data['difficulty_level'] == "-1":
            is_valid = False
            flash ('Please select a difficulty level', 'location')
        return is_valid