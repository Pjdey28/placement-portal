from flask import Flask, request
from flask_login import LoginManager
from models import db, User
import os
app = Flask(__name__, static_folder="statics", static_url_path="/static")
app.config["SECRET_KEY"] = "secretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
ALLOWED_EXTENSIONS = {"pdf"}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "routes.login_page"
login_manager.session_protection = "strong"

@app.after_request
def add_no_cache_headers(response):
    if request.endpoint != "static":
        response.headers["Cache-Control"] = "no-store"
    return response

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes import routes
app.register_blueprint(routes)
if __name__ == "__main__":
    app.run(debug=True)
