# Backend - Career Guidance API

Flask-based REST API with SQLite database for user authentication and career guidance features.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python app.py
```

Server starts on: http://127.0.0.1:5000

### 3. Test Authentication
```bash
python test_auth.py
```

## Database

**Location:** `instance/course_recommendation.db` (auto-created)

**View with:** [DB Browser for SQLite](https://sqlitebrowser.org/)

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user

### Career Features
- `POST /api/chatbot/message` - AI career chat
- `GET /api/suggester/start` - Start career suggestion
- `POST /api/suggester/answer` - Submit survey answer
- `POST /api/recommender/start` - Start course search
- `POST /api/recommender/submit` - Get recommendations

## Documentation

- 📘 **[AUTH_TESTING_GUIDE.md](AUTH_TESTING_GUIDE.md)** - Detailed testing instructions
- 📗 **[AUTHENTICATION_SUMMARY.md](AUTHENTICATION_SUMMARY.md)** - Complete setup overview

## Project Structure

```
Backend/
├── app.py                    # Main Flask application
├── models.py                 # Database models
├── requirements.txt          # Python dependencies
├── test_auth.py             # Authentication test script
├── blueprints/
│   ├── auth_bp.py           # Authentication endpoints
│   ├── chatbot_bp.py        # AI chatbot
│   ├── suggester_bp.py      # Career suggester
│   └── recommender_bp.py    # Course recommender
├── services/
│   ├── llm_service.py       # LLM integration (Groq)
│   └── job_search_service.py # Job search logic
└── instance/
    └── course_recommendation.db  # SQLite database
```

## Environment Variables

Create a `.env` file:
```bash
FLASK_SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key-here
```

## Tech Stack

- **Framework:** Flask
- **Database:** SQLite + Flask-SQLAlchemy
- **Auth:** Flask-Bcrypt
- **LLM:** Groq API
- **CORS:** Flask-CORS

