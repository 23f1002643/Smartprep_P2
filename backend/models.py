from flask_sqlalchemy import SQLAlchemy  
from datetime import datetime, timezone
# from pytz import timezone

db = SQLAlchemy() 
Base = db.Model
# IST = timezone('Asia/Kolkata')
class Account(Base):
    __tablename__ = 'Users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # reg_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reg_date = db.Column(db.DateTime, default=datetime.utcnow)
    f_name = db.Column(db.String(80), nullable=False)
    l_name = db.Column(db.String(80), nullable=False)
    pwd = db.Column(db.String(130), nullable=False)
    edu_qul = db.Column(db.String(120), nullable=False)
    mobile_no = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120),unique=False, nullable=False)
    role = db.Column(db.String(100), default="user")
    active = db.Column(db.Boolean, default=True)
    
    # Relationship with Score table
    scores = db.relationship('ExamPerformance', back_populates='user', cascade='all, delete-orphan')
    # for solving pylance error
    # def __init__(self, username, f_name, l_name, pwd, edu_qul, mobile_no, dob, email, role='user', active=True):
    #     self.username = username
    #     self.f_name = f_name
    #     self.l_name = l_name
    #     self.pwd = pwd
    #     self.edu_qul = edu_qul
    #     self.mobile_no = mobile_no
    #     self.dob = dob
    #     self.email = email
    #     self.role = role
    #     self.active = active

class Courses(Base):
    __tablename__ = 'Course_Area' #Subject
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    s_name = db.Column(db.String(80), nullable=False)
    remarks = db.Column(db.Text, nullable=False)
    
    # Relationship with Chapter table
    chapters = db.relationship('CourseModule', back_populates='course', cascade="all, delete-orphan")
    
    # # for solving pylance error
    # def __init__(self, s_name, remarks):
    #     self.s_name = s_name
    #     self.remarks = remarks

class CourseModule(Base):
    __tablename__ = 'Chapters'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('Course_Area.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Relationships
    course = db.relationship('Courses', back_populates='chapters')
    quizzes = db.relationship('Assessment', back_populates='chapter', cascade="all, delete-orphan")

    # for solving pylance error
    # def __init__(self, subject_id, name, description):
    #     self.subject_id = subject_id
    #     self.name = name
    #     self.description = description

class Assessment(Base):
    __tablename__ = 'Quiz_Table'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    q_name = db.Column(db.String(80), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('Chapters.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=False) 
    remarks = db.Column(db.Text)
    # Relationships
    questions = db.relationship('AssessmentProblem', back_populates='quiz', cascade="all, delete-orphan")
    scores = db.relationship('ExamPerformance', back_populates='quiz', cascade="all, delete-orphan")
    chapter = db.relationship('CourseModule', back_populates='quizzes')

    # for solving pylance error
    # def __init__(self, q_name, chapter_id, date_of_quiz, time_duration, remarks):
    #     self.q_name = q_name
    #     self.chapter_id = chapter_id
    #     self.date_of_quiz = date_of_quiz
    #     self.time_duration = time_duration
    #     self.remarks = remarks

class AssessmentProblem(Base):
    __tablename__ = 'Question_Table'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    que_no = db.Column(db.Integer, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('Quiz_Table.id'), nullable=False)
    statement = db.Column(db.String(200), nullable=False)
    opt1 = db.Column(db.String(150), nullable=False)
    opt2 = db.Column(db.String(150), nullable=False)
    opt3 = db.Column(db.String(150), nullable=False)
    opt4 = db.Column(db.String(150), nullable=False)
    cor_opt = db.Column(db.Integer, nullable=False)
    
    quiz = db.relationship('Assessment', back_populates='questions') 
    # def __init__(self, que_no, quiz_id, statement, opt1, opt2, opt3, opt4, cor_opt):
    #     self.que_no = que_no
    #     self.quiz_id = quiz_id
    #     self.statement = statement
    #     self.opt1 = opt1
    #     self.opt2 = opt2
    #     self.opt3 = opt3
    #     self.opt4 = opt4
    #     self.cor_opt = cor_opt

class ExamPerformance(Base):
    __tablename__ = 'Scores'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('Quiz_Table.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    time_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    max_marks = db.Column(db.Integer, nullable=False)
    
    # Relationships
    user = db.relationship('Account', back_populates='scores')
    quiz = db.relationship('Assessment', back_populates='scores')
    # def __init__(self, score, quiz_id, user_id, time_of_attempt, max_marks):
    #     self.score = score
    #     self.quiz_id = quiz_id
    #     self.user_id = user_id
    #     self.time_of_attempt = time_of_attempt
    #     self.max_marks = max_marks

print("✅ All models loaded successfully.")
