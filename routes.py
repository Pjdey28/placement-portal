from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date
from models import db, User, Student, Company, Drive, Application
routes = Blueprint("routes", __name__)
def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() == "pdf"

@routes.route("/")
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
            if company.blacklisted:
                return "Company Blacklisted"
        if user.role == "student":
            student = Student.query.get(user.id)
            if student.blacklisted:
                return "Account Blacklisted"
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
    query = request.args.get("q", "")
    students_q = []
    companies_q = []
    if query:
        students_q = Student.query.filter(
            Student.name.ilike(f"%{query}%")
        ).limit(5).all()
        companies_q = Company.query.filter(
            Company.name.ilike(f"%{query}%")
        ).limit(5).all()
    students = Student.query.count()
    companies = Company.query.count()
    drives = Drive.query.count()
    applications = Application.query.count()
    students_list = Student.query.all()
    companies_list = Company.query.all()
    pending_companies = Company.query.filter_by(approved=False).all()
    return render_template(
        "admin_dashboard.html",
        students=students,
        companies=companies,
        drives=drives,
        applications=applications,
        pending_companies=pending_companies,
        students_list=students_list,
        companies_list=companies_list,
        students_q=students_q,
        companies_q=companies_q
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
    drive.status = "Active"
    db.session.commit()
    return redirect("/admin/drives")

@routes.route("/admin/view/<role>/<int:id>")
@login_required
def admin_view(role, id):
    if current_user.role != "admin":
        return "Unauthorized"
    if role == "student":
        obj = Student.query.get_or_404(id)
        applications = Application.query.filter_by(student_id=id).all()
        return render_template(
            "admin_detail.html",
            role="student",
            obj=obj,
            applications=applications
        )
    elif role == "company":
        obj = Company.query.get_or_404(id)
        drives = Drive.query.filter_by(company_id=id).all()
        return render_template(
            "admin_detail.html",
            role="company",
            obj=obj,
            drives=drives
        )
    else:
        return "Invalid role"

@routes.route("/company/dashboard")
@login_required
def company_dashboard():
    if current_user.role != "company":
        return "Unauthorized"
    company = Company.query.get(current_user.id)
    if not company.approved:
        return "Waiting for admin approval"
    upcoming = Drive.query.filter(
        Drive.company_id == current_user.id,
        Drive.status != "Closed"
    ).all()
    closed = Drive.query.filter_by(
        company_id=current_user.id,
        status="Closed"
    ).all()
    return render_template(
        "company_dashboard.html",
        company=company,
        upcoming=upcoming,
        closed=closed
    )

@routes.route("/company/create_drive", methods=["GET","POST"])
@login_required
def create_drive():
    if current_user.role != "company":
        return "Unauthorized"
    company = Company.query.get(current_user.id)
    if not company.approved:
        return "Company not approved"
    if request.method == "POST":
        deadline_str = request.form["deadline"]
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        salary_range = request.form.get("salary") or request.form.get("salary_range") 
        skills_required = request.form.get("skills") or request.form.get("skills_required")
        drive = Drive(
            company_id=current_user.id,
            title=request.form["title"],
            description=request.form["description"],
            eligibility=request.form["eligibility"],
            deadline=deadline,
            approved=False,
            status="Pending",
            salary_range=salary_range,
            skills_required=skills_required
        )
        db.session.add(drive)
        db.session.commit()
        return redirect("/company/dashboard")
    return render_template("drive_form.html", mode="Create", drive=None)


@routes.route("/company/applications/<int:drive_id>")
@login_required
def company_applications(drive_id):
    if current_user.role != "company":
        return "Unauthorized"
    drive = Drive.query.get_or_404(drive_id)
    if drive.company_id != current_user.id:
        return "Unauthorized"
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template(
        "company_applications.html",
        applications=applications
    )

@routes.route("/company/profile", methods=["GET", "POST"])
@login_required
def company_profile():
    if current_user.role != "company":
        return "Unauthorized"
    company = Company.query.get(current_user.id)
    if request.method == "POST":
        company.name = request.form["name"]
        company.hr_contact = request.form["hr_contact"]
        company.website = request.form["website"]
        db.session.commit()
        return redirect("/company/dashboard")
    return render_template("company_profile.html", company=company)

@routes.route("/company/edit_drive/<int:id>", methods=["GET","POST"])
@login_required
def edit_drive(id):
    if current_user.role != "company":
        return "Unauthorized"
    drive = Drive.query.get_or_404(id)
    if drive.company_id != current_user.id:
        return "Unauthorized"
    if request.method == "POST":
        drive.title = request.form["title"]
        drive.description = request.form["description"]
        drive.eligibility = request.form["eligibility"]
        drive.skills_required = request.form["skills"]
        drive.salary_range = request.form["salary"]
        drive.deadline = datetime.strptime(
            request.form["deadline"], "%Y-%m-%d"
        ).date()
        db.session.commit()
        return redirect("/company/dashboard")
    return render_template("drive_form.html",
                           mode="Edit",
                           drive=drive)

@routes.route("/company/update_status/<int:app_id>/<status>")
@login_required
def update_application_status(app_id, status):
    if current_user.role != "company":
        return "Unauthorized"
    if status not in ["Shortlisted", "Selected", "Rejected"]:
        return "Invalid Status"
    application = Application.query.get_or_404(app_id)
    if application.drive.company_id != current_user.id:
        return "Unauthorized"
    application.status = status
    db.session.commit()
    return redirect(request.referrer or "/company/dashboard")

@routes.route("/company/drive/<int:id>")
@login_required
def drive_applications(id):
    drive = Drive.query.get_or_404(id)
    if drive.company_id != current_user.id:
        return "Unauthorized"
    applications = Application.query.filter_by(
        drive_id=id
    ).all()
    return render_template(
        "company_drive_applications.html",
        drive=drive,
        applications=applications
    )
@routes.route("/company/review/<int:id>", methods=["GET","POST"])
@login_required
def review_application(id):
    application = Application.query.get_or_404(id)
    if application.drive.company_id != current_user.id:
        return "Unauthorized"
    if request.method == "POST":
        application.status = request.form["status"]
        db.session.commit()
        return redirect(f"/company/drive/{application.drive_id}")
    return render_template(
        "company_review_application.html",
        application=application
    )

@routes.route("/company/update_drive/<int:id>/<status>")
@login_required
def update_drive_status(id, status):
    if current_user.role != "company":
        return "Unauthorized"
    drive = Drive.query.get_or_404(id)
    if drive.company_id != current_user.id:
        return "Unauthorized"
    if status not in ["Active", "Closed"]:
        return "Invalid Status"
    drive.status = status
    db.session.commit()
    return redirect("/company/dashboard")

@routes.route("/student/dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        return "Unauthorized"
    student = Student.query.get(current_user.id)
    drives = Drive.query.filter_by(status="Active").all()
    applications = Application.query.filter_by(student_id=current_user.id).all()
    return render_template(
        "student_dashboard.html",
        student=student,
        drives=drives,
        applications=applications
    )

@routes.route("/student/apply/<int:drive_id>")
@login_required
def apply_drive(drive_id):
    if current_user.role != "student":
        return "Unauthorized"
    drive = Drive.query.get_or_404(drive_id)
    if drive.status != "Active":
        return "Applications are closed for this drive"
    existing = Application.query.filter_by(
        student_id=current_user.id,
        drive_id=drive_id
    ).first()
    if existing:
        return "You have already applied for this drive"
    application = Application(
        student_id=current_user.id,
        drive_id=drive_id,
        application_date=date.today(),
        status="Applied"
    )
    db.session.add(application)
    db.session.commit()
    return redirect("/student/dashboard")

@routes.route("/student/profile", methods=["GET","POST"])
@login_required
def student_profile():
    if current_user.role != "student":
        return "Unauthorized"
    student = Student.query.get(current_user.id)
    if request.method == "POST":
        student.name = request.form["name"]
        student.email = request.form["email"]
        student.skills = request.form["skills"]
        db.session.commit()
        return redirect("/student/dashboard")
    return render_template("student_profile.html", student=student)


@routes.route("/student/update_resume", methods=["POST"])
@login_required
def update_resume():
    if current_user.role != "student":
        return "Unauthorized"
    student = Student.query.get(current_user.id)
    file = request.files.get("resume")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        student.resume = filename
        db.session.commit()
    return redirect("/student/profile")