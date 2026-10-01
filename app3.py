from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flaskproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("vikash")
db = SQLAlchemy(app)


# Employee Table
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    email_id = db.Column(db.String(120), nullable=False)
    employee_company = db.Column(db.String(100), nullable=False)


# Create table
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)