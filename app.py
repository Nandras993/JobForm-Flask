from datetime import datetime
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import json

app = Flask(__name__)

path = "config.json"  # Rename config-example.json to config.json and fill it with your data
with open(path, "r") as handler:
    info = json.load(handler)

app.config["SECRET_KEY"] = info["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = info["SQLALCHEMY_DATABASE_URI"]  # mysql:///data.db if you use mysql
app.config["MAIL_SERVER"] = info["MAIL_SERVER"]
app.config["MAIL_PORT"] = info["MAIL_PORT"]
app.config["MAIL_USE_SSL"] = info["MAIL_USE_SSL"]
app.config["MAIL_USERNAME"] = info["MAIL_USERNAME"]
app.config["MAIL_PASSWORD"] = info["MAIL_PASSWORD"]

db = SQLAlchemy(app)

mail = Mail(app)


class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    date = db.Column(db.Date)
    occupation = db.Column(db.String(80))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        date = request.form["date"]
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        occupation = request.form["occupation"]

        form = Form(first_name=first_name,
                    last_name=last_name,
                    email=email,
                    date=date_obj,
                    occupation=occupation)
        db.session.add(form)
        db.session.commit()

        message_body = f"Thank you for your submission, {first_name}! " \
                       f"Here are your data:\n{first_name}\n{last_name}\n{date}\n{email}\n{occupation}\n" \
                       f"We will contact you soon!"
        message = Message(subject="New job application form submission",
                          sender=app.config["MAIL_USERNAME"],
                          recipients=[email],
                          body=message_body)

        mail.send(message)

        flash(f"Dear {first_name}, your form was submitted successfully!", "success")

    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5001)
