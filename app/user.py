from flask_login import UserMixin
from .database import DB


class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


    def create(self):
    	with DB() as db:
       		values = (self.username, self.password, self.email)
        	db.execute('''
            	INSERT INTO users (username, password, email)
            	VALUES (?, ?, ?)''', values)
        	return self


    def update(self):
    	with DB() as db:
       		values = (self.username, self.password, self.email, self.id)
        	db.execute('UPDATE users SET username = ?, password = ?, email = ? WHERE id = ?', values)
        	return self


    @staticmethod
    def find(email):
        if not email:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE email = ?',(email,)
            ).fetchone()
            if row:
                return User(*row)


    @staticmethod
    def find_by_id(id):
        if not id:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE id = ?',(id,)
            ).fetchone()
            if row:
                return User(*row)


    @staticmethod
    def find_by_sensor(sensor_id):
        if not sensor_id:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE sensor_id = ?',(sensor_id,)
            ).fetchone()
            if row:
                return User(*row)

