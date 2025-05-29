"""
Database Models

This module defines the database models for the productivity app:
- User: Authentication and user management
- Note: User-owned notes with CRUD operations
"""

from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields
from datetime import datetime
from config import db, bcrypt


class User(db.Model):
    """
    User model for authentication and user management.
    
    Handles secure password storage and user sessions.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with notes
    notes = db.relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')

    @hybrid_property
    def password_hash(self):
        """Prevent direct access to password hash."""
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        """Hash and set password."""
        if password:
            password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
            self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        """Verify password against stored hash."""
        if self._password_hash and password:
            return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
        return False

    @validates('username')
    def validate_username(self, key, username):
        """Validate username requirements."""
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return username.strip()

    @validates('email')
    def validate_email(self, key, email):
        """Basic email validation."""
        if not email or '@' not in email:
            raise ValueError("Please provide a valid email address")
        return email.lower().strip()

    def __repr__(self):
        return f'<User {self.username}>'


class Note(db.Model):
    """
    Note model for user-owned notes.
    
    Each note belongs to a specific user and includes title and content.
    """
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @validates('title')
    def validate_title(self, key, title):
        """Validate note title."""
        if not title or len(title.strip()) < 1:
            raise ValueError("Note title is required")
        if len(title.strip()) > 200:
            raise ValueError("Note title must be less than 200 characters")
        return title.strip()

    def __repr__(self):
        return f'<Note {self.title}>'


# Marshmallow Schemas for serialization
class UserSchema(Schema):
    """Schema for User serialization."""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)
    
    class Meta:
        load_instance = True


class NoteSchema(Schema):
    """Schema for Note serialization."""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)
    user = fields.Nested(UserSchema, only=['id', 'username'], dump_only=True)
    
    class Meta:
        load_instance = True