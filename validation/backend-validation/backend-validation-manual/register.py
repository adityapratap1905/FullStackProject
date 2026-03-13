from flask import Flask, render_template, request


app = Flask(__name__)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form["password"]
        if not name:
            return "Name is required"
        if not password or len(password) < 6:
            return "Password is required and must be at least 6 characters long"
        else:
            return "Registration Successful"
    return render_template("register.html")


app.run(debug=True)
