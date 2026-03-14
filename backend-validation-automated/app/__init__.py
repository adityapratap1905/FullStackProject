import os

from flask import Flask, redirect, render_template, request, session, url_for

from .forms import RegisterForm
from .models import User, db


def create_app():
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            username = form.username.data.strip()
            email = form.email.data.strip().lower()

            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            if existing_user:
                message = "Username or email is already registered."
                return render_template("register.html", form=form, message=message), 400

            user = User(username=username, email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            return render_template(
                "login.html",
                message=f"Registration successful for user {username}. Please log in.",
            )

        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                session["user_id"] = user.id
                return redirect(url_for("dashboard"))

            return render_template(
                "login.html",
                message="Invalid username or password.",
            ), 401

        return render_template("login.html")

    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        session.pop("user_id", None)
        return redirect(url_for("login"))

    @app.route("/update_email", methods=["GET", "POST"])
    def update_email():
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))

        user = db.session.get(User, user_id)
        if user is None:
            session.pop("user_id", None)
            return redirect(url_for("login"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            existing_email = User.query.filter(
                User.email == email, User.id != user.id
            ).first()
            if existing_email:
                return render_template(
                    "update_email.html",
                    message="That email is already in use.",
                ), 400

            user.email = email
            db.session.commit()
            return redirect(url_for("dashboard"))

        return render_template("update_email.html")

    @app.route("/delete_account", methods=["GET", "POST"])
    def delete_account():
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))

        user = db.session.get(User, user_id)
        if user is None:
            session.pop("user_id", None)
            return redirect(url_for("login"))

        if request.method == "POST":
            db.session.delete(user)
            db.session.commit()
            session.pop("user_id", None)
            return redirect(url_for("login"))

        return render_template(
            "delete_account.html",
            message="Are you sure you want to delete your account?",
        )

    @app.route("/dashboard")
    def dashboard():
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))

        user = db.session.get(User, user_id)
        if user is None:
            session.pop("user_id", None)
            return redirect(url_for("login"))

        return render_template(
            "dashboard.html",
            message="Welcome to the dashboard!",
            username=user.username,
        )

    return app
