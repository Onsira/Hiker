from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DB
from flask_app.models import user, location


class Comment:
    def __init__(self, data):
        self.id = data["id"]
        self.content = data["content"]
        self.user_id = data["user_id"]
        self.location_id = data["location_id"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

    @classmethod
    def create_comment(cls, data):
        query = """INSERT INTO comments (content, user_id, location_id, created_at)
                VALUES ( %(content)s, %(user_id)s, %(location_id)s, NOW() );"""
        results = connectToMySQL(DB).query_db(query, data)
        return results

    @classmethod
    def delete_comment(cls, data):
        query = """DELETE FROM comments WHERE id = %(id)s;"""
        return connectToMySQL(DB).query_db(query, data)

    @classmethod
    def get_all_comments_from_location(cls, data):
        query = """
                SELECT * FROM comments LEFT JOIN users ON comments.user_id = users.id
                WHERE comments.location_id = %(id)s ;       
        """
        results = connectToMySQL(DB).query_db(query, data)
        all_comments = []
        if results:
            for row in results:
                this_location = cls(row)
                user_data = {
                    **row,
                    "id": row["users.id"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
                this_user = user.User(user_data)
                this_location.data = this_user
                all_comments.append(this_location)
        return all_comments

    @classmethod
    def get_location_id(cls, data):
        query = """SELECT location_id FROM comments WHERE id = %(id)s;"""
        results = connectToMySQL(DB).query_db(query, data)
        if results: 
            return results[0]['location_id'] 
        return None