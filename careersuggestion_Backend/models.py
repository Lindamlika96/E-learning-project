"""
Database models for the Career Guidance application.

Models:
- User: User accounts with authentication
- ChatHistory: Chat conversation history
- SavedCourse: User's saved course recommendations
"""

from extensions import db
from datetime import datetime


class User(db.Model):
    """User model for authentication and profile management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    chat_histories = db.relationship('ChatHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    saved_courses = db.relationship('SavedCourse', backref='user', lazy=True, cascade='all, delete-orphan')
    career_suggestions = db.relationship('CareerSuggestion', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convert user object to dictionary (exclude password)."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ChatHistory(db.Model):
    """Chat history model to store user conversations."""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    conversation_id = db.Column(db.String(36), nullable=False, index=True)  # UUID for grouping messages
    chat_title = db.Column(db.String(255), nullable=True)  # Title of conversation
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatHistory {self.id} - User {self.user_id} - Conv {self.conversation_id}>'
    
    def to_dict(self):
        """Convert chat history object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'conversation_id': self.conversation_id,
            'chat_title': self.chat_title,
            'message': self.message,
            'reply': self.reply,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SavedCourse(db.Model):
    """Saved course model to store user's bookmarked courses."""
    __tablename__ = 'saved_courses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_title = db.Column(db.String(255), nullable=False)
    provider = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SavedCourse {self.course_title} - User {self.user_id}>'
    
    def to_dict(self):
        """Convert saved course object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_title': self.course_title,
            'provider': self.provider,
            'description': self.description,
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CareerSuggestion(db.Model):
    """Career suggestion session model to store user's career path questionnaire results."""
    __tablename__ = 'career_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUID for session
    session_title = db.Column(db.String(255), nullable=True)  # Title of suggestion session
    answers = db.Column(db.Text, nullable=False)  # JSON string of Q&A pairs
    suggestions = db.Column(db.Text, nullable=False)  # JSON string of career suggestions
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CareerSuggestion {self.id} - User {self.user_id} - Session {self.session_id}>'
    
    def to_dict(self):
        """Convert career suggestion object to dictionary."""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'session_title': self.session_title,
            'answers': json.loads(self.answers) if self.answers else {},
            'suggestions': json.loads(self.suggestions) if self.suggestions else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

