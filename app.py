from flask import Flask, render_template, request, jsonify, redirect
import string, random, os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Use DATABASE_URL if available, else fallback to local SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///urls.db")
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

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shortenURL():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    code = generateCode()
    domain = request.host_url.rstrip("/")

    existing = URL.query.filter_by(original_url=url).first()
    if existing:
        return jsonify({"shortURL": domain + "/" + existing.short_code})

    while URL.query.filter_by(short_code=code).first():
        code = generateCode()

    new_url = URL(short_code=code, original_url=url)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({"shortURL": domain + "/" + code})

@app.route("/<code>")
def shortRedirect(code):
    entry = URL.query.filter_by(short_code=code).first()
    if entry:
        entry.clicks += 1
        db.session.commit()
        return redirect(entry.original_url)
    return jsonify({"error": "Short URL not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)