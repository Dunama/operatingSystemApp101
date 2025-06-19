from src.db.core import db


class Questions(db.Model):
    __tablename__= 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question_no = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(225), nullable=False)

class Answers(db.Model):
    __tablename__= 'answers'
    answer_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

class Options(db.Model):
    __tablename__= 'options'
    options_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    label = db.Column(db.String(1), nullable=False)
    text = db.Column(db.String(225), nullable=False)

class Response(db.Model):
    __tablename__= 'response'
    id = db.Column(db.Integer, primary_key=True)
    question_no = db.Column(db.Integer, db.ForeignKey('questions.question_no'), nullable=False)
    answers_id = db.Column(db.Integer, db.ForeignKey('answers.answer_id'), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    timestamp = db.Column(db.Float, nullable=False)
   