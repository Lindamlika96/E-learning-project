🎓 CareerGuide AI - Course Recommendation System
CareerGuide AI is a comprehensive Flask + React application created by raslen ferchichi that provides personalized career guidance, course recommendations, and AI-powered career advice. The system uses Large Language Models (LLaMA3 via Groq) combined with structured data to deliver accurate, Tunisia-focused guidance for career development and learning paths.

✨ Features
Core AI Features :

🤖 AI Career Chatbot - Real-time conversational career advice with chat history
📋 Career Suggester - 11-question assessment for personalized career path recommendations
🔍 Course Recommender - Survey-based course recommendations with filtering
💾 Chat History Management - Save, load, update, and delete conversations (ChatGPT-style sidebar)
💼 Session Management - Save and revisit career assessment sessions

Authentication & Database

🔐 User Authentication - Secure signup/login with password hashing (Flask-Bcrypt)
🗄️ SQLite Database - Persistent storage for users, chat history, and career suggestions
👤 User Profiles - Track individual user progress and saved data
 
 AI Testing & Quality Assurance :

🧪 Frontend-Integrated Testing - Real-time AI interaction recording and analysis
📊 Detailed Test Reports - Comprehensive quality reports with scores, issues, and metrics
🎯 Automatic AI Detection - Smart detection of which AI component is being tested
📈 Performance Metrics - Response time tracking and quality scoring
🔍 CLI Test Runner - Command-line tools for automated AI diagnostics
📁 JSON Report Export - Timestamped diagnostic logs saved to Backend/logs/

User Experience : 

🎨 Modern React UI - Responsive design with smooth animations
🌍 Tunisia-Localized - All career data and examples tailored to Tunisian market
📱 Mobile Responsive - Works seamlessly on all device sizes
🎭 Guided Tour - Onboarding tour for new users
🔔 Toast Notifications - Real-time feedback for user actions

🏗️ Project Structure :

course-recommendation-main/
├── Backend/
│   ├── app.py                           # Flask application entrypoint
│   ├── extensions.py                    # SQLAlchemy & Bcrypt initialization
│   ├── models.py                        # Database models (User, ChatHistory, etc.)
│   ├── blueprints/
│   │   ├── auth_bp.py                   # Authentication endpoints
│   │   ├── chatbot_bp.py                # Chatbot with history management
│   │   ├── suggester_bp.py              # Career suggester with sessions
│   │   ├── recommender_bp.py            # Course recommender
│   │   ├── test_reports_bp.py           # Test report API
│   │   └── test_recording_bp.py         # Real-time test recording
│   ├── services/
│   │   ├── llm_service.py               # LLM integration (Groq/LLaMA3)
│   │   └── job_search_service.py        # Static job/course data
│   ├── tests/
│   │   ├── diagnostic_framework.py      # Testing framework base classes
│   │   ├── test_chatbot.py              # Chatbot AI tests
│   │   ├── test_career_suggester.py     # Career suggester tests
│   │   └── test_course_recommender.py   # Course recommender tests
│   ├── run_ai_tests.py                  # CLI test runner
│   ├── logs/                            # AI diagnostic reports (JSON)
│   ├── instance/
│   │   └── course_recommendation.db     # SQLite database
│   ├── .env                             # Environment variables
│   ├── requirements.txt                 # Python dependencies
│   └── README.md
│
├── Frontend/
│   ├── src/
│   │   ├── App.jsx                      # Main React app
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.jsx           # Header with test controls
│   │   │   │   ├── Footer.jsx           # Footer component
│   │   │   │   ├── TestStatusIndicator.jsx  # Recording status
│   │   │   │   └── TestResultsModal.jsx # Detailed test results popup
│   │   │   ├── chatbot/
│   │   │   │   ├── ChatWindow.jsx       # Chat interface
│   │   │   │   ├── ChatMessage.jsx      # Message bubbles
│   │   │   │   └── ChatSidebar.jsx      # Conversation history sidebar
│   │   │   ├── suggester/
│   │   │   │   └── SuggesterSidebar.jsx # Session history sidebar
│   │   │   ├── layout/
│   │   │   │   └── MainLayout.jsx       # App layout wrapper
│   │   │   └── onboarding/
│   │   │       └── GuideTour.jsx        # User onboarding tour
│   │   ├── pages/
│   │   │   ├── Home.jsx                 # Landing page
│   │   │   ├── Login.jsx                # Login page
│   │   │   ├── Signup.jsx               # Registration page
│   │   │   ├── Dashboard.jsx            # User dashboard
│   │   │   ├── Chatbot.jsx              # Chatbot page
│   │   │   ├── CareerSuggester.jsx      # Career assessment page
│   │   │   └── CourseRecommender.jsx    # Course search page
│   │   ├── context/
│   │   │   ├── AuthContext.jsx          # Authentication state
│   │   │   └── TestContext.jsx          # Testing mode state
│   │   ├── services/
│   │   │   └── api.js                   # API integration layer
│   │   └── hooks/
│   │       └── useAuth.js               # Authentication hook
│   ├── public/
│   │   ├── R.png                        # Custom logo
│   │   └── raslen_teacher.png           # Auth page background
│   ├── package.json
│   └── vite.config.js



🔌 API Endpoint

AUTHENTICATION
  POST   /api/auth/signup              Register new user
  POST   /api/auth/login               Authenticate user

CHATBOT
  POST   /api/chatbot/message          Send message and get AI response
  GET    /api/chatbot/conversations    List user's saved conversations
  GET    /api/chatbot/conversations/<id> Load specific conversation
  DELETE /api/chatbot/conversations/<id> Delete conversation
  POST   /api/chatbot/save-conversation Save/update conversation

CAREER SUGGESTER
  GET    /api/suggester/start          Start new assessment
  POST   /api/suggester/answer         Submit answer, get next question
  GET    /api/suggester/sessions       List saved sessions
  GET    /api/suggester/sessions/<id>  Load specific session
  DELETE /api/suggester/sessions/<id>  Delete session
  POST   /api/suggester/save-session   Save completed assessment

COURSE RECOMMENDER
  POST   /api/recommender/start        Initialize course search
  POST   /api/recommender/submit       Submit survey, get recommendations

AI TESTING
  POST   /api/tests/start-recording    Start test recording session
  POST   /api/tests/log-interaction    Log AI interaction
  POST   /api/tests/stop-recording     Stop recording, generate report
  GET    /api/tests/session-status/<id> Get recording session status
  GET    /api/tests/reports            List all test reports
  GET    /api/tests/reports/<id>       Get specific report details
  GET    /api/tests/reports/stats      Get aggregate test statistics

GENERAL
  GET    /                             Health check and endpoint list




🚀 Setup Instructions

* Backend Setup

1 Clone the repository
git clone https://github.com/YourUsername/course-recommendation.git
cd course-recommendation-main/Backend

2 create virtual repository 
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3 install dependencies
pip install -r requirements.txt

4 create .env file 
FLASK_SECRET_KEY=your_secret_key_here(put what ever you want here )
GROQ_API_KEY=your_groq_api_key(get it from the official website of grok)

5 run the backend :
python app.py
backend runs on http:/localhost:5000


* Frontend Setup

1 Navigate to frontend
cd ../Frontend

2 Install dependencies
npm install

3 Create .env file (optional)
VITE_API_BASE_URL=http://localhost:5000

4 Run the frontend
npm run dev



📦 Dependencies

Backend (Python)

Flask>=2.0                 # Web framework
Flask-CORS>=3.0.10         # CORS support
Flask-SQLAlchemy>=3.0.0    # Database ORM
Flask-Bcrypt>=1.0.1        # Password hashing
groq>=0.22.0               # LLM API client
python-dotenv>=0.15        # Environment variables
requests>=2.25             # HTTP requests

Frontend (React)

{
  "react": "^18.2.0",
  "react-router-dom": "^6.x",
  "react-icons": "^4.x",
  "react-toastify": "^9.x"
}

🧪 AI Testing System
Running Diagnostic Tests (CLI)

Test all AI components:
cd Backend
python run_ai_tests.py --verbose

Test specific AI:
python run_ai_tests.py --test chatbot --verbose
python run_ai_tests.py --test career_suggester --verbose
python run_ai_tests.py --test course_recommender --verbose

View saved reports:
python tests/report_viewer.py --list
python tests/report_viewer.py --report <filename>
python tests/report_viewer.py --stats


rontend-Integrated Testing
Enable Test Mode - Toggle "Test Mode" in header (when logged in)
Start Recording - Click "Start" button
Use AI Features - Interact with Chatbot, Career Suggester, or Course Recommender
Stop Recording - Click "Stop" to generate detailed report
View Results - Modal popup shows comprehensive results with:
Overall score (0-100)
Per-AI performance breakdown
Individual interaction scores
Issues and warnings
Response times
Quality metrics
📊 Database Schema
Users
id, username, email, password_hash, created_at
ChatHistory
id, user_id, conversation_id, chat_title, role, message, created_at
CareerSuggestion
id, user_id, session_id, session_title, answers (JSON), suggestions (JSON), created_at

🎯 Example API Requests

Signup

POST /api/auth/signup
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}

Chatbot Message

POST /api/chatbot/message
Content-Type: application/json

{
  "message": "What career paths are available in Tunisia for IT graduates?",
  "history": [],
  "user_id": 1,
  "conversation_id": "uuid-here"
}

Response:
{
  "success": true,
  "reply": "In Tunisia, IT graduates have several promising career paths...",
  "conversation_id": "uuid-here"
}

Save Chat Conversation
POST /api/chatbot/save-conversation
Content-Type: application/json

{
  "user_id": 1,
  "conversation_id": "uuid-here",
  "title": "Career paths in Tunisia",
  "messages": [
    {"role": "user", "content": "What careers..."},
    {"role": "assistant", "content": "In Tunisia..."}
  ]
}

🌟 Key Features Explained

1. Chat History Management
-Save conversations with auto-generated titles
-Update existing conversations with new messages
-Load previous conversations to continue discussions
-Delete unwanted conversations
-Sidebar navigation similar to ChatGPT

2. Career Assessment Sessions
-Save completed career assessments
-View past results anytime
-Track career exploration journey
-Auto-generated session titles

3. Real-Time AI Testing
-No time limits - test at your own pace
-Automatic AI component detection
-Manual start/stop control
-Detailed quality analysis
-JSON reports with timestamps
-Visual score breakdowns

4. Tunisia-Focused Content
-All career advice localized to Tunisia
-Tunisia-specific job market insights
-Local education and certification recommendations

🔒 Security Features

✅ Password hashing with Bcrypt
✅ Secure session management
✅ CORS configuration for API security
✅ Environment variable protection
✅ SQL injection prevention (SQLAlchemy ORM)

🤝 Contributing

-Fork the repository
-Create a feature branch (git checkout -b feature/AmazingFeature)
-Commit your changes (git commit -m 'Add some AmazingFeature')
-Push to the branch (git push origin feature/AmazingFeature)
-Open a Pull Request

📝 License : 

This project is licensed under the MIT License.

🙏 Acknowledgments

-LLM Provider: Groq (LLaMA3-8B model)
-Frontend Framework: React + Vite
-Backend Framework: Flask
-Database: SQLite with SQLAlchemy ORM

📧 Contact

For questions or support, please open an issue on GitHub.
Built with ❤️ for the Tunisian tech community

