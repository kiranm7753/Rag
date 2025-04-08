from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from auth.models import User, db
from flask_bcrypt import Bcrypt

auth_bp = Blueprint("auth", __name__, template_folder="../templates")
bcrypt = Bcrypt()

@auth_bp.record_once
def init_bcrypt(setup_state):
    bcrypt.init_app(setup_state.app)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("auth.login"))
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("index"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid credentials.")
        return redirect(url_for("auth.login"))
    return render_template("login.html")
