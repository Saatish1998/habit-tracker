from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    habits = db.relationship('Habit', backref='user', lazy=True)
    evaluations = db.relationship('DailyEvaluation', backref='user', lazy=True)

class Habit(db.Model):
    __tablename__ = 'habit'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    frequency = db.Column(db.String(50))  # e.g., daily, weekly, or “3 times/week”
    reminder_time = db.Column(db.String(5))  # Format: "HH:MM"
    non_productive = db.Column(db.Boolean, default=False)
    goal_target = db.Column(db.Integer, nullable=True)  # Number of times to complete
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade='all, delete-orphan')

class HabitLog(db.Model):
    __tablename__ = 'habit_log'
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, default=0)  # Duration in minutes

class DailyEvaluation(db.Model):
    __tablename__ = 'daily_evaluation'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    is_productive = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class SmartwatchData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    steps = db.Column(db.Integer)
    sleep = db.Column(db.Float)
    heart_rate = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

