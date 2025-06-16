from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from src.api.auth.auth import pro_required
from src.db.models.quiz_db import Questions, Answers, Options, Response

comprehensive_bp = Blueprint('comprehensive', __name__)  # Remove url_prefix

@comprehensive_bp.route('/api/comprehensive/all-questions', methods=['GET'])
@pro_required
def all_questions():
    try:
        return render_template('questionBank.html')
    except Exception as e:
        print(f"Error accessing question bank: {e}")
        return redirect(url_for('auth.login'))

@comprehensive_bp.route('/api/comprehensive/all-questions/submit', methods=['GET', 'POST'])
@pro_required
def comprehensive_question():
    '''view comprehensive questions'''
    try:
        if request.method == 'GET':
            # fetch all questions from the database
            comprehensive_questions = Questions.query.order_by(Questions.question_no).all()
            if not comprehensive_questions:
                return jsonify({'error': 'No comprehensive questions found'}), 404
            
            result = []
            for question in comprehensive_questions:
                # get options for each question
                options = Options.query.filter_by(question_id=question.question_id).all()
                options_list = [{'label': opt.label, 'text': opt.text} for opt in options]
                question_data = {
                    'question_no': question.question_no,
                    'question': question.question,
                    'options': options_list
                }
                result.append(question_data)
            
            return jsonify(result), 200
            
        elif request.method == 'POST':
            # for comprehensive submission
            data = request.get_json()
            user_answers = data.get('answers', {})
            score = 0 
            total_questions = len(user_answers)
            results = []

            # loop through all user answers
            for question_no_str, user_answer in user_answers.items():
                question_no = int(question_no_str)
                question = Questions.query.filter_by(question_no=question_no).first()
                if not question:
                    continue
                    
                # get correct answer
                correct_answer = Answers.query.filter_by(question_id=question.question_id).first()
                
                # Convert both answers to lowercase and strip whitespace for comparison
                user_ans_clean = user_answer.strip().lower() if user_answer else None
                correct_ans_clean = correct_answer.correct_answer.strip().lower() if correct_answer else None
                is_correct = (user_ans_clean == correct_ans_clean)
                
                if is_correct:
                    score += 1
                    
                results.append({
                    "question_no": question_no,
                    "question": question.question,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer.correct_answer if correct_answer else None,
                    "is_correct": is_correct
                })

            return jsonify({
                "score": score,
                "total": total_questions,
                "percentage": (score / total_questions) * 100 if total_questions > 0 else 0,
                "results": results
            }), 200
    except Exception as e:
        print(f"Error in question bank submit: {e}")
        return jsonify({'error': str(e)}), 500

@comprehensive_bp.route('/api/comprehensive/answer/<int:question_no>')
@pro_required
def get_question_answer(question_no):
    '''Get the correct answer for a specific question'''
    question = Questions.query.filter_by(question_no=question_no).first()
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    correct_answer = Answers.query.filter_by(question_id=question.question_id).first()
    if not correct_answer:
        return jsonify({'error': 'Answer not found'}), 404
    
    return jsonify({
        'question_no': question_no,
        'correct_answer': correct_answer.correct_answer
    }), 200