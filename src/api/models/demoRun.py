from flask import Blueprint, jsonify, request, render_template, session
from src.db.core import db
from src.db.models.quiz_db import Questions, Answers, Options, Response

demo_bp = Blueprint('demo', __name__)
@demo_bp.route('/api/demo/questions', methods=['GET'])
def demo_view():
    return render_template('demoRun.html')

@demo_bp.route('/api/demo/questions/submit', methods=['GET', 'POST'])
def demo_question():
    '''view demo questions'''
    if request.method == 'GET':
        # fetch question 1-5 from the database
        demo_questions = Questions.query.filter(Questions.question_no.between(1,5)).order_by(Questions.question_no).all()
        if not demo_questions:
            return jsonify({'error': 'No demo questions found'}), 404
        
        result = []
        for question in demo_questions:
            # get options for each question
            options = Options.query.filter_by(question_id=question.question_id).all()
            options_list =[{'label': opt.label, 'text': opt.text} for opt in options]
            question_data = {
                'question_no': question.question_no,
                'question': question.question,
                'options': options_list
            }
            result.append(question_data)
        
        return jsonify(result), 200
        
    elif request.method == 'POST':
    # for demo submission
        data = request.get_json()
        user_answers = data.get('answers', {})
        score = 0 
        total_questions = 5
        results = []

    # loop through question 1-5
    for question_no in range(1, 6):
        question = Questions.query.filter_by(question_no=question_no).first()
        if not question:
            return jsonify({'error': f'Question {question_no} not found'}), 404
        if question:
            # get correct answer
            correct_answer = Answers.query.filter_by(question_id=question.question_id).first()
            user_ans = user_answers.get(str(question_no))
            # Convert both answers to lowercase and strip whitespace
            user_ans_clean = user_ans.strip().lower() if user_ans else None
            correct_ans_clean = correct_answer.correct_answer.strip().lower() if correct_answer else None
            is_correct = (user_ans_clean == correct_ans_clean)
            if is_correct:
                score += 1
            results.append({
                "question_no": question_no,
                "question": question.question,
                "user_answer": user_ans,
                "correct_answer": correct_answer.correct_answer if correct_answer else None,
                "is_correct": is_correct
            })

    return jsonify({
        "score": score,
        "total": total_questions,
        "percentage": (score / total_questions) * 100 if total_questions > 0 else 0,
        "results": results
    }), 200