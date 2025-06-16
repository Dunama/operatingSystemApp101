from flask import Blueprint, jsonify, request, render_template
from src.db.core import db
import time 
from src.db.models.quiz_questions import quiz_questions
from src.db.models.quiz_db import Questions, Answers, Options, Response 
quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz', methods=['GET'])
def get_all_quiz():
    ''' view all the quiz questions'''
    return jsonify(quiz_questions),200

@quiz_bp.route('/quiz/db', methods=['GET'])
def get_all_questions_from_db():
    '''view all questions in the db'''
    questions = Questions.query.all()
    result = []
    for q in questions:
        options = Options.query.filter_by(question_id=q.question_id).all()
        options_list = [{"label": opt.label, "text": opt.text} for opt in options]
        result.append({
            "question_no": q.question_no,
            "question": q.question,
            "options": options_list
        })
    return jsonify(result), 200

@quiz_bp.route('/quiz/check', methods=['POST'])
def check_answers():
    data = request.get_json()
    question_no = data.get('question_no')
    user_ans = data.get('user_ans')
    user_id = data.get('user_id')

    # Get the question from the database
    question = Questions.query.filter_by(question_no=question_no).first()
    if not question:
        return jsonify({"error": "Question not found"}), 404

    # Get the answer from the database
    answer = Answers.query.filter_by(question_id=question.question_id).first()
    if not answer:
        return jsonify({"error": "Answer not found"}), 404

    # Get the options from the database
    options = Options.query.filter_by(question_id=question.question_id).all()
    options_list = [{"label": opt.label, "text": opt.text} for opt in options]

    is_correct = (user_ans == answer.correct_answer)

    # Save the user's response
    user_response = Response(
        user_id=user_id,
        answers_id=answer.answer_id,
        correct_answer=answer.correct_answer,
        question_no=question_no,
        timestamp=time.time()
    )
    db.session.add(user_response)
    db.session.commit()

    return jsonify({
    "correct": is_correct,
    "selected": user_ans,
    "expected": answer.correct_answer
    }), 200


