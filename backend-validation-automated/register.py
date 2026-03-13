import bcrypt
from flask import Flask, redirect, render_template, request, session, url_for
from form import RegisterForm
from model.user import db, User

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:Nopassword%4003@localhost/test"
)
db.init_app(app)

with app.app_context():
    db.create_all()
    print("Test Database tables created successfully...")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
        usrname = form.username.data
        email = form.email.data
        password = form.password.data

        print(
            f"Received registration data: username={usrname}, email={email}, password={password}"
        )

        user = User(username=usrname, email=email, password=password)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return render_template(
            "login.html",
            message=f"Registration successful for user {usrname}! Please log in.",
        )
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(
            password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            session["user_id"] = user.id
            return redirect(url_for("dashboard_method", username=username))
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


@app.route("/update_email", methods=["GET", "POST"])
def update_email():
    if request.method == "POST":
        email = request.form["email"]
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user:
                user.email = email
                db.session.commit()
                return redirect(url_for("dashboard_method", username=user.username))
    return render_template("update_email.html")


@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if request.method == "POST":
        if "user_id" in session:
            user_id = session["user_id"]
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                session.pop("user_id", None)
                return redirect(url_for("login"))
      
    return render_template("delete_account.html", message="Are you sure you want to delete your account?")


@app.route("/dashboard/<username>")
def dashboard_method(username=None):
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template(
        "dashboard.html", message="Welcome to the dashboard!", username=username
    )


app.run(debug=True)
