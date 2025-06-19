from app import create_app
from src.db.core import db
from src.db.models.quiz_db import Questions, Options, Answers
from src.db.models.quiz_questions import quiz_questions

def populate_database():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Answers.query.delete() 
        Options.query.delete()
        Questions.query.delete()
        db.session.commit()
        
        print("Populating database with quiz questions...")
        
        for question_data in quiz_questions:
            # Create question
            question = Questions(
                question_no=question_data['question_no'],
                question=question_data['question']
            )
            db.session.add(question)
            db.session.flush()  # Get the question_id
            
            # Create options
            for option_data in question_data['options']:
                option = Options(
                    question_id=question.question_id,
                    label=option_data['label'],
                    text=option_data['text']
                )
                db.session.add(option)
            
            # Create answer
            answer = Answers(
                question_id=question.question_id,
                correct_answer=question_data['answer']
            )
            db.session.add(answer)
        
        db.session.commit()
        print(f"Successfully populated database with {len(quiz_questions)} questions!")

if __name__ == '__main__':
    populate_database()
