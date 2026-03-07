from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from models import db, User, Student, Company, Drive, Application
routes = Blueprint("routes", __name__)
def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() == "pdf"

@routes.route("/")
def login_page():
    return render_template("login.html")
def login_page():
    return render_template("login.html")

@routes.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password,password):
        if user.role == "company":
            company = Company.query.get(user.id)
            if not company.approved:
                return "Company not approved by admin yet"
        login_user(user)
        if user.role == "admin":
            return redirect("/admin/dashboard")
        if user.role == "student":
            return redirect("/student/dashboard")
        if user.role == "company":
            return redirect("/company/dashboard")
    return "Invalid Login"

@routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@routes.route("/register/student", methods=["GET","POST"])
def register_student():
    if request.method == "POST":
        file = request.files["resume"]
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config["UPLOAD_FOLDER"],filename)
            file.save(path)
        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            role="student"
        )
        db.session.add(user)
        db.session.commit()
        student = Student(
            id=user.id,
            name=request.form["name"],
            email=request.form["email"],
            skills=request.form["skills"],
            resume=filename
        )
        db.session.add(student)
        db.session.commit()
        return redirect("/")
    return render_template("register_student.html")

@routes.route("/register/company", methods=["GET","POST"])
def register_company():
    if request.method == "POST":

        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            role="company"
        )
        db.session.add(user)
        db.session.commit()
        company = Company(
            id=user.id,
            name=request.form["name"],
            hr_contact=request.form["hr_contact"],
            website=request.form["website"],
            approved=False
        )
        db.session.add(company)
        db.session.commit()
        return "Registration submitted. Wait for admin approval."
    return render_template("register_company.html")

@routes.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Unauthorized"

    students = Student.query.count()
    companies = Company.query.count()
    drives = Drive.query.count()
    applications = Application.query.count()

    pending_companies = Company.query.filter_by(approved=False).all()

    return render_template(
        "admin_dashboard.html",
        students=students,
        companies=companies,
        drives=drives,
        applications=applications,
        pending_companies=pending_companies
    )

@routes.route("/admin/approve_company/<int:id>")
@login_required
def approve_company(id):
    if current_user.role != "admin":
        return "Unauthorized"
    company = Company.query.get(id)
    company.approved = True
    db.session.commit()
    return redirect("/admin/dashboard")

@routes.route("/admin/toggle_blacklist/<role>/<int:id>")
@login_required
def toggle_blacklist(role, id):
    if current_user.role != "admin":
        return "Unauthorized"
    if role == "student":
        s = Student.query.get(id)
        s.blacklisted = not s.blacklisted
    if role == "company":
        c = Company.query.get(id)
        c.blacklisted = not c.blacklisted
    db.session.commit()
    return redirect("/admin/dashboard")

@routes.route("/admin/drives")
@login_required
def admin_drives():
    if current_user.role != "admin":
        return "Unauthorized"

    drives = Drive.query.all()
    applications = Application.query.all()

    return render_template(
        "admin_drives.html",
        drives=drives,
        applications=applications
    )

@routes.route("/admin/approve_drive/<int:id>")
@login_required
def approve_drive(id):
    if current_user.role != "admin":
        return "Unauthorized"
    drive = Drive.query.get(id)
    drive.approved = True
    drive.status = "Approved"
    db.session.commit()
    return redirect("/admin/drives")

@routes.route("/admin/search", methods=["GET","POST"])
@login_required
def admin_search():
    if current_user.role != "admin":
        return "Unauthorized"
    students = None
    companies = None
    if request.method == "POST":
        query = request.form["query"]
        students = Student.query.filter(
            Student.name.contains(query)
        ).all()
        companies = Company.query.filter(
            Company.name.contains(query)
        ).all()
    return render_template(
        "admin_search.html",
        students=students,
        companies=companies
    )

