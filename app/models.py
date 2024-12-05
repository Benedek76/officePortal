from flask_sqlalchemy import SQLAlchemy

# DB initialize
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    dept = db.Column(db.String(50))
    number = db.Column(db.String(20))
    extension = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __repr__(self):
        return f'<Contact {self.name}>'