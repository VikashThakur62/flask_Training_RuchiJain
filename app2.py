from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flaskproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("vikash")

db = SQLAlchemy(app)


# Database Model
class user(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone_num = db.Column(db.Integer, nullable=True)
    meg = db.Column(db.String(80), nullable=True)


# Create database table
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)