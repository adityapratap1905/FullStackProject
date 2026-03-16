import os

from flask import Flask, abort, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from model.users import Users
from model.users import db

from form import RegisterForm


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key_here")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///users.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

loginmanager = LoginManager()
loginmanager.init_app(app)
loginmanager.login_view = "login"


@loginmanager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))


db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        user = Users(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template(
                "register.html",
                form=form,
                error="Username or email already exists.",
            )
        return render_template(
            "login.html", message="Registration successful! Please log in."
        )
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("login.html", error="Username and password are required")

    user = Users.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for("dashboard", user_id=user.id))
    return render_template("login.html", error="Invalid credentials")


@app.route("/dashboard/<int:user_id>")
@login_required
def dashboard(user_id):
    if current_user.id != user_id:
        abort(403)

    return render_template(
        "dashboard.html", user_id=user_id, current_user=current_user.username
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/delete_account/<int:user_id>", methods=["GET", "POST"])
@login_required
def delete_account(user_id):
    if current_user.id != user_id:
        abort(403)

    if request.method == "GET":
        return redirect(url_for("dashboard", user_id=current_user.id))

    user = db.session.get(Users, user_id)
    if user is None:
        abort(404)

    db.session.delete(user)
    db.session.commit()
    session.pop("user_id", None)
    logout_user()
    return redirect("/login")


@app.route("/update_email/<int:user_id>", methods=["POST", "GET"])
@login_required
def update_email(user_id):
    if current_user.id != user_id:
        abort(403)

    user = db.session.get(Users, user_id)
    if user is None:
        abort(404)

    if request.method == "POST":
        new_email = request.form.get("new_email")
        if new_email:
            user.email = new_email
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return render_template(
                    "update_email.html",
                    user=user,
                    error="That email address is already in use.",
                )
            return redirect(url_for("dashboard", user_id=user_id))

    return render_template("update_email.html", user=user)


@app.route("/fetch_all")
@login_required
def fetch_all():
    users = Users.query.all()
    return render_template("fetch_all_users.html", users=users)


if __name__ == "__main__":
    app.run(debug=True)
