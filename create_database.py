from app import app
from models import db,User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(
        username="admin"
    ).first()
if not admin:
    admin = User(
        username="admin",
        password=generate_password_hash("admin123"),
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()

print("Database Created")

