from flask_sqlalchemy import SQLAlchemy 
db = SQLAlchemy()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True,nullable=False)
    password = db.Column(db.String(200), unique=True,nullable=False)
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
