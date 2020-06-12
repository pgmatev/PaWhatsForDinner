from .database import DB
import os


class Recipe:
    def __init__(self, id, name, user_id, description, rating, time, picture):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.description = description
        self.rating = rating
        self.time = time
        self.picture = picture


    @staticmethod
    def all():
        with DB() as db:
            rows = db.execute('SELECT * FROM recipes').fetchall()
            return [Recipe(*row) for row in rows]


    def create(self):
        with DB() as db:
            values = (self.name, self.user_id, self.description, self.rating, self.time, self.picture)
            db.execute('''
                INSERT INTO recipes(name, user_id, description, rating, time, picture)
                VALUES (?, ?, ?, ?, ?, ?)''', values)
            return self


    @staticmethod
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    @staticmethod
    def find(id):
        with DB() as db:
            row = db.execute('SELECT * FROM recipes WHERE id = ?',(id,)).fetchone()
            return Recipe(*row)


    @staticmethod
    def find_last_id():
        with DB() as db:
            last_id = db.execute('SELECT MAX(id) from recipes').fetchone()
            return last_id


    def remove_picture(self):
        path = "/home/vesko/Desktop/gesko/Ma-whats-for-dinner-/app" + self.picture
        if self.picture != "/static/img/default.jpeg" and os.path.exists(path):
            os.remove(path)


    @staticmethod
    def find_by_name(name):
        if not name:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM recipes WHERE name = ?',
                (name,)
            ).fetchone()
            if row:
                return Recipe(*row)


    @staticmethod
    def get_by_user_id(user_id):
        with DB() as db:
            rows = db.execute('SELECT * FROM recipes WHERE user_id = ?', (user_id,)).fetchall()
            return [Recipe(*row) for row in rows]


    def save(self):
        with DB() as db:
            values = (self.name, self.description, self.time, self.picture, self.id)
            db.execute('UPDATE recipes SET name = ?, description = ?, time = ?, picture = ? WHERE id = ?', values)
            return self


    def delete(self):
        with DB() as db:
            db.execute('DELETE FROM recipes WHERE id = ?', (self.id,))
            return self