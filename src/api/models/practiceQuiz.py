from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from src.api.auth.auth import pro_required
from src.db.models.quiz_db import Questions, Options, Answers
import random

practice_bp = Blueprint('practice', __name__)  # Remove url_prefix

@practice_bp.route('/api/practice/questions', methods=['GET'])
@pro_required
def practice_questions():
    try:
        return render_template('practiceQuiz.html')
    except Exception as e:
        print(f"Error accessing practice questions: {e}")
        return redirect(url_for('auth.login'))

@practice_bp.route('/api/practice/questions/submit', methods=['GET', 'POST'])
@pro_required
def get_practice_questions():
    try:
        if request.method == 'GET':
            # Get all questions within range 1-71
            all_questions = Questions.query.filter(
                Questions.question_no.between(1, 184)
            ).all()
            
            # Randomly select 70 questions
            selected_questions = random.sample(all_questions, min(70, len(all_questions)))
            
            # Sort selected questions by question number for consistency
            selected_questions.sort(key=lambda x: x.question_no)
            
            result = []
            for question in selected_questions:
                options = Options.query.filter_by(question_id=question.question_id).all()
                options_list = [{'label': opt.label, 'text': opt.text} for opt in options]
                result.append({
                    'question_no': question.question_no,
                    'question': question.question,
                    'options': options_list
                })
            return jsonify(result)
            
        elif request.method == 'POST':
            # Handle submission of answers
            data = request.get_json()
            user_answers = data.get('answers', {})
            
            # Get all questions for the practice
            all_questions = Questions.query.order_by(Questions.question_no).all()
            total_questions = len(all_questions)
            score = 0 
            results = []

            # loop through all questions
            for question_no in range(1, total_questions + 1):
                question = Questions.query.filter_by(question_no=question_no).first()
                if not question:
                    continue
                    
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
    except Exception as e:
        print(f"Error in practice questions submit: {e}")
        return jsonify({'error': str(e)}), 500