from flask import Flask, render_template
from model import fetch_db

app = Flask(__name__)

@app.route("/student")
def students():
	return "Welcome students to GLA university Mthura"

@app.route("/")
def root():
	return "Welcome students to GLA university Mthura"

@app.route("/flask")
def flask_fun():
	return "Welcoem to flask"

@app.route("/html")
def teml_fun():
	sec = "2D"
	list_of_students = fetch_list_of_students()
	return render_template("test.html", sec=sec, los=list_of_students)

def fetch_list_of_students():
	return  ["aryan", "satpal", "Ananya"]


if __name__ == "__main__":
	app.run(debug=True)



