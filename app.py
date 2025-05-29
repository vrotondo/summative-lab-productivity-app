"""
Flask Productivity App - Main Application

A secure Flask API with session-based authentication and user-owned notes.
Includes full CRUD operations, pagination, and access controls.
"""

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from functools import wraps

from config import app, db, api
from models import User, Note, UserSchema, NoteSchema


# Initialize schemas
user_schema = UserSchema()
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)


def login_required(f):
    """Decorator to require authentication for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return {'error': 'Authentication required'}, 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get the currently logged-in user."""
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None


# Authentication Routes
class Signup(Resource):
    """User registration endpoint."""
    
    def post(self):
        """Register a new user."""
        try:
            data = request.get_json()
            
            if not data:
                return {'errors': ['No data provided']}, 400
            
            # Validate required fields
            required_fields = ['username', 'email', 'password']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return {'errors': [f'Missing required fields: {", ".join(missing_fields)}']}, 400
            
            # Create new user
            new_user = User(
                username=data['username'],
                email=data['email']
            )
            new_user.password_hash = data['password']
            
            # Save to database
            db.session.add(new_user)
            db.session.commit()
            
            # Log user in
            session['user_id'] = new_user.id
            
            return user_schema.dump(new_user), 201
            
        except ValueError as e:
            db.session.rollback()
            return {'errors': [str(e)]}, 422
        except IntegrityError as e:
            db.session.rollback()
            if 'username' in str(e):
                return {'errors': ['Username already exists']}, 422
            elif 'email' in str(e):
                return {'errors': ['Email already exists']}, 422
            return {'errors': ['Registration failed']}, 422
        except Exception as e:
            db.session.rollback()
            return {'errors': ['Registration failed']}, 500


class Login(Resource):
    """User login endpoint."""
    
    def post(self):
        """Authenticate user and create session."""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No data provided'}, 400
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return {'error': 'Username and password required'}, 400
            
            # Find user by username
            user = User.query.filter_by(username=username).first()
            
            if user and user.authenticate(password):
                session['user_id'] = user.id
                return user_schema.dump(user), 200
            
            return {'error': 'Invalid credentials'}, 401
            
        except Exception as e:
            return {'error': 'Login failed'}, 500


class Logout(Resource):
    """User logout endpoint."""
    
    @login_required
    def delete(self):
        """End user session."""
        session.pop('user_id', None)
        return '', 204


class CheckSession(Resource):
    """Check current user session."""
    
    def get(self):
        """Get current user if logged in."""
        user = get_current_user()
        if user:
            return user_schema.dump(user), 200
        return {'error': 'No active session'}, 401


# Notes CRUD Routes
class NotesResource(Resource):
    """Notes collection endpoint - GET (paginated) and POST."""
    
    @login_required
    def get(self):
        """Get paginated notes for current user."""
        user = get_current_user()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Query user's notes with pagination
        pagination = Note.query.filter_by(user_id=user.id)\
                              .order_by(Note.updated_at.desc())\
                              .paginate(
                                  page=page,
                                  per_page=per_page,
                                  error_out=False
                              )
        
        # Serialize notes
        notes = notes_schema.dump(pagination.items)
        
        return {
            'notes': notes,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'total_pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }, 200
    
    @login_required
    def post(self):
        """Create a new note for current user."""
        try:
            user = get_current_user()
            data = request.get_json()
            
            if not data:
                return {'errors': ['No data provided']}, 400
            
            # Validate required fields
            if not data.get('title'):
                return {'errors': ['Title is required']}, 400
            
            # Create new note
            new_note = Note(
                title=data['title'],
                content=data.get('content', ''),
                user_id=user.id
            )
            
            db.session.add(new_note)
            db.session.commit()
            
            return note_schema.dump(new_note), 201
            
        except ValueError as e:
            db.session.rollback()
            return {'errors': [str(e)]}, 422
        except Exception as e:
            db.session.rollback()
            return {'errors': ['Failed to create note']}, 500


class NoteResource(Resource):
    """Individual note endpoint - GET, PATCH, DELETE."""
    
    @login_required
    def get(self, note_id):
        """Get a specific note (only if owned by current user)."""
        user = get_current_user()
        note = Note.query.filter_by(id=note_id, user_id=user.id).first()
        
        if not note:
            return {'error': 'Note not found'}, 404
        
        return note_schema.dump(note), 200
    
    @login_required
    def patch(self, note_id):
        """Update a specific note (only if owned by current user)."""
        try:
            user = get_current_user()
            note = Note.query.filter_by(id=note_id, user_id=user.id).first()
            
            if not note:
                return {'error': 'Note not found'}, 404
            
            data = request.get_json()
            if not data:
                return {'errors': ['No data provided']}, 400
            
            # Update fields if provided
            if 'title' in data:
                note.title = data['title']
            if 'content' in data:
                note.content = data['content']
            
            db.session.commit()
            
            return note_schema.dump(note), 200
            
        except ValueError as e:
            db.session.rollback()
            return {'errors': [str(e)]}, 422
        except Exception as e:
            db.session.rollback()
            return {'errors': ['Failed to update note']}, 500
    
    @login_required
    def delete(self, note_id):
        """Delete a specific note (only if owned by current user)."""
        try:
            user = get_current_user()
            note = Note.query.filter_by(id=note_id, user_id=user.id).first()
            
            if not note:
                return {'error': 'Note not found'}, 404
            
            db.session.delete(note)
            db.session.commit()
            
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            return {'errors': ['Failed to delete note']}, 500


# Register API routes
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(NotesResource, '/notes', endpoint='notes')
api.add_resource(NoteResource, '/notes/<int:note_id>', endpoint='note')


@app.route('/')
def home():
    """Health check endpoint."""
    return {
        'message': 'Productivity App API',
        'status': 'running',
        'auth_method': 'sessions'
    }


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)