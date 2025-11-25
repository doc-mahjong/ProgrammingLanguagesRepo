from flask import Flask, render_template, request, jsonify, redirect
import string
import random
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder="static", template_folder="templates")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    original_url = db.Column(db.Text, nullable=False)
    clicks = db.Column(db.Integer, default=0)

def generate_code():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    url = data.get("url")

    # 1️⃣ Check if URL already exists
    existing = URL.query.filter_by(original_url=url).first()
    if existing:
        return jsonify({"code": existing.short_code})

    # 2️⃣ Generate a unique short code
    code = generate_code()
    while URL.query.filter_by(short_code=code).first():
        code = generate_code()

    # 3️⃣ Store in database
    new_url = URL(short_code=code, original_url=url)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({"code": code})

@app.route("/<code>")
def redirect_short(code):
    entry = URL.query.filter_by(short_code=code).first()

    if entry:
        entry.clicks += 1
        db.session.commit()
        return redirect(entry.original_url)

    return jsonify({"error": "Short URL not found"}), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
