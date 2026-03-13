from flask import Flask, render_template
from model import fetch_list_of_students_from_db

app = Flask(__name__)

@app.route("/greet")
def students():
	return "Welcome students to GLA university Mthura"

@app.route("/")
def root():
	return "Welcome to GLA university Mthura"

@app.route("/flask")
def flask_fun():
	return "Welcoem to flask"

@app.route("/students")
def teml_fun():
	sec = "2D"
	list_of_students = fetch_list_of_students_from_db()
	return render_template("render_test_1601.html", sec=sec, los=list_of_students)

if __name__ == "__main__":
	app.run(debug=True)



