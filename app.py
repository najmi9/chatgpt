from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import db, create_user, authenticate_user, User
from dotenv import load_dotenv
import os
import requests
from flask_login import login_required

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
db.init_app(app)

@app.context_processor
def inject_globals():
    if not 'user_id' in session:
        return {}

    user = User.query.filter_by(id=session['user_id']).first()
    return {'current_user': user}

# Create a registration form that allows users to create an account and store their information in the database
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Create a new user and store their information in the database
        if create_user(username, password):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Username already exists')

    return render_template('register.html')

# Create a login form that allows users to authenticate themselves and access the chatbot
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate the user and store their ID in the session
        user_id = authenticate_user(username, password)
        if user_id is not None:
            session['user_id'] = user_id
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove the user ID from the session
    session.pop('user_id', None)

    return redirect(url_for('login'))

# Define a route for the chatbot that requires authentication
@login_required
@app.route('/chat')
def chat():
    # Check if the user is authenticated
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=session['user_id']).first()

    # Check if the user is enabled
    #if not user.is_enabled:
    #    flash('Your account has been disabled', 'danger')
    #    return redirect(url_for('login'))

    return render_template(
        'chat.html',
        user=user
    )

@login_required
@app.route('/chatbot', methods=['POST'])
def chatbot():
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_URL = 'https://api.openai.com/v1/chat/completions'
    message = request.json['message']
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'prompt': f'User: {message}\nBot:',
        'max_tokens': 50,
        'temperature': 0.7,
        'model': 'gpt-3.5-turbo',
    }
    try:
        response = requests.post(OPENAI_URL, json=data, headers=headers)
        chatbot_response = response.json()['choices'][0]['text'].strip()
        return jsonify({'message': chatbot_response})
    except:
        return jsonify({'message': 'Sorry, something went wrong'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
