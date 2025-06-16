# CS205 Quiz Application

A web-based quiz application for Operating Systems course.

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate virtual environment and install dependencies: `pip install -r requirements.txt`
4. Set up environment variables in `.env` file:
   # Example .env (do NOT use real secrets here)
   FLASK_APP=src.app
   FLASK_ENV=development
   DATABASE_URL=your_database_url
   SECRET_KEY=your_secret_key
   OAUTH2_CLIENT_ID=your_google_client_id
   OAUTH2_CLIENT_SECRET=your_google_client_secret
   PAYSTACK_SECRET_KEY=your_paystack_key
5. Run migrations: `flask db upgrade`
6. Start server: `flask run`

## Features
- Practice quizzes
- Demo mode
- Question bank
- Pro features with payment integration

## License
MIT License - see LICENSE file
