# dynamic_url_test.py
# flask --app practice/dynamic_url_test.py run

from flask import Flask, url_for
app = Flask(__name__)

@app.route('/')
def index():
   return "Welcome to the homepage!"

@app.route('/about')
def about():
   return "About Us"

@app.route('/user/<username>')
def show_user_profile(username):
   # show the user profile for that user
   return f'User {username}'
   
with app.test_request_context():  # simple way to test parts of your app without a client
   print(url_for('index'))  # Output: '/'
   print(url_for('about'))  # Output: '/about'
   print(url_for('show_user_profile', username='JohnDoe'))  # Output: '/user/JohnDoe'
   print(url_for('index', page=2, filter='name'))  # Output: '/?page=2&filter=name'

# In Jinja2 templates
# <a href="{{ url_for('about') }}">About Us</a>

# In static files such as CSS or JavaScript
# url_for('static', filename='style.css')