from flask import Flask, render_template, request, jsonify, redirect
import string
import random
import os 
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)

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
