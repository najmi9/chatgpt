from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Define a User model that represents a row in the user table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Create a new user and store their information in the database
def create_user(username, password):
    # Check if the username already exists in the database
    user = User.query.filter_by(username=username).first()
    if user:
        return False

    # Create a new user and store their information in the database
    new_user = User(username=username, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    return True

# Authenticate a user and return their ID
def authenticate_user(username, password):
    # Check if the username exists in the database
    user = User.query.filter_by(username=username).first()
    if not user:
        return None

    # Check if the password is correct
    if not check_password_hash(user.password, password):
        return None

    return user.id
