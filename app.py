from flask import Flask, session, render_template, request, jsonify, redirect
import string
import random
import os 
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash, check_password_hash
import re

USERNAME = "Admin"
PASS = "scrypt:32768:8:1$JCONEeUadJf1KA6S$d603a8e9e2aae83419e38b8844117a955edd4bc14fe0b872bb3b88bbc4c4c26d1933b337bc690948b5458943807ce8a42d7de869c8ef6667d5116b3cb1f2f3c9"

app = Flask(__name__)
app.secret_key = "Super_Secret_Key_Nobody_Will_Ever_Guess"

URL_REGEX = re.compile(r'^(https?://)([a-zA-Z0-9]+-?)+\.([a-zA-Z0-9]+-?\.?)+(:\d+)?(\/.*)?$')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    original_url = db.Column(db.Text, nullable=False)
    clicks = db.Column(db.Integer, default=0)

def generateCode():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))
    
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/shorten", methods=['POST'])
def shortenURL():
    data = request.get_json()
    url = data.get('url')
    code = generateCode()
    domain = request.host_url.rstrip('/')

    #Check if the url is valid
    if not bool(URL_REGEX.match(url)):
        return jsonify({"error": "Invalid url..."}), 400
    
    #Check if the long url already has a short url
    existing = URL.query.filter_by(original_url=url).first()
    if existing:
        return jsonify({'shortURL' : domain + "/" + existing.short_code})
    
    #Check if the generated short code exists; regenerate if so
    existing = URL.query.filter_by(short_code=code).first()
    while existing:
        code = generateCode()
        existing = URL.query.filter_by(short_code=code).first()
    
    # Save new short url to data base
    new_url = URL(short_code=code, original_url=url)
    db.session.add(new_url)
    db.session.commit()
    
    return jsonify({'shortURL' : domain +"/" + code})

@app.route("/<code>")
def shortRedirect(code):
    originalUrl = URL.query.filter_by(short_code=code).first()
    if originalUrl:
        originalUrl.clicks += 1
        db.session.commit()
        return redirect(originalUrl.original_url)
    return jsonify({"error": "Short URL not found"}), 404

@app.route("/stats")
def table():
    if not session.get('logged_in'):
        return redirect('/login')
    session.pop('logged_in', None)
    urls = URL.query.all()
    return render_template("stats.html", urls=urls)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
    
        if username != USERNAME or not check_password_hash(PASS, password):
            return render_template('login.html', error="Incorrect Credentials...")

        session['logged_in'] = True
            
        return redirect('/stats')

    return render_template('login.html')
