"""
Basic Test Suite for Productivity App

This module contains basic tests for the Flask API endpoints.
Run with: python -m pytest test_app.py -v
"""

import pytest
import json
from app import app, db
from models import User, Note


@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def test_user(client):
    """Create a test user."""
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    response = client.post('/signup', 
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    return json.loads(response.data)


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_signup_success(self, client):
        """Test successful user registration."""
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123'
        }
        
        response = client.post('/signup', 
                              data=json.dumps(user_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['username'] == 'newuser'
        assert data['email'] == 'new@example.com'
        assert 'id' in data
    
    def test_signup_missing_fields(self, client):
        """Test signup with missing required fields."""
        user_data = {
            'username': 'newuser'
            # Missing email and password
        }
        
        response = client.post('/signup', 
                              data=json.dumps(user_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data
    
    def test_signup_duplicate_username(self, client, test_user):
        """Test signup with duplicate username."""
        user_data = {
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'password123'
        }
        
        response = client.post('/signup', 
                              data=json.dumps(user_data),
                              content_type='application/json')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        assert 'errors' in data
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }
        
        response = client.post('/login',
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = client.post('/login',
                              data=json.dumps(login_data),
                              content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_check_session_logged_in(self, client, test_user):
        """Test check session when logged in."""
        response = client.get('/check_session')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
    
    def test_logout(self, client, test_user):
        """Test logout functionality."""
        response = client.delete('/logout')
        
        assert response.status_code == 204
        
        # Check that session is ended
        response = client.get('/check_session')
        assert response.status_code == 401


class TestNotes:
    """Test notes CRUD endpoints."""
    
    def test_create_note_success(self, client, test_user):
        """Test successful note creation."""
        note_data = {
            'title': 'Test Note',
            'content': 'This is a test note content'
        }
        
        response = client.post('/notes',
                              data=json.dumps(note_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Test Note'
        assert data['content'] == 'This is a test note content'
        assert data['user_id'] == test_user['id']
    
    def test_create_note_missing_title(self, client, test_user):
        """Test note creation with missing title."""
        note_data = {
            'content': 'Content without title'
        }
        
        response = client.post('/notes',
                              data=json.dumps(note_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data
    
    def test_create_note_unauthorized(self, client):
        """Test note creation without authentication."""
        note_data = {
            'title': 'Test Note',
            'content': 'This should fail'
        }
        
        response = client.post('/notes',
                              data=json.dumps(note_data),
                              content_type='application/json')
        
        assert response.status_code == 401
    
    def test_get_notes_success(self, client, test_user):
        """Test getting user's notes."""
        # Create a test note first
        note_data = {
            'title': 'Test Note',
            'content': 'Test content'
        }
        client.post('/notes',
                   data=json.dumps(note_data),
                   content_type='application/json')
        
        response = client.get('/notes')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'notes' in data
        assert 'pagination' in data
        assert len(data['notes']) == 1
        assert data['notes'][0]['title'] == 'Test Note'
    
    def test_get_notes_pagination(self, client, test_user):
        """Test notes pagination."""
        # Create multiple notes
        for i in range(15):
            note_data = {
                'title': f'Test Note {i+1}',
                'content': f'Content {i+1}'
            }
            client.post('/notes',
                       data=json.dumps(note_data),
                       content_type='application/json')
        
        # Test first page
        response = client.get('/notes?page=1&per_page=5')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['notes']) == 5
        assert data['pagination']['page'] == 1
        assert data['pagination']['total'] == 15
        assert data['pagination']['total_pages'] == 3
    
    def test_get_notes_unauthorized(self, client):
        """Test getting notes without authentication."""
        response = client.get('/notes')
        assert response.status_code == 401
    
    def test_get_single_note_success(self, client, test_user):
        """Test getting a single note."""
        # Create a note first
        note_data = {
            'title': 'Single Note Test',
            'content': 'Single note content'
        }
        create_response = client.post('/notes',
                                     data=json.dumps(note_data),
                                     content_type='application/json')
        note = json.loads(create_response.data)
        
        # Get the note
        response = client.get(f'/notes/{note["id"]}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Single Note Test'
        assert data['id'] == note['id']
    
    def test_update_note_success(self, client, test_user):
        """Test successful note update."""
        # Create a note first
        note_data = {
            'title': 'Original Title',
            'content': 'Original content'
        }
        create_response = client.post('/notes',
                                     data=json.dumps(note_data),
                                     content_type='application/json')
        note = json.loads(create_response.data)
        
        # Update the note
        update_data = {
            'title': 'Updated Title',
            'content': 'Updated content'
        }
        response = client.patch(f'/notes/{note["id"]}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Title'
        assert data['content'] == 'Updated content'
    
    def test_delete_note_success(self, client, test_user):
        """Test successful note deletion."""
        # Create a note first
        note_data = {
            'title': 'Note to Delete',
            'content': 'This will be deleted'
        }
        create_response = client.post('/notes',
                                     data=json.dumps(note_data),
                                     content_type='application/json')
        note = json.loads(create_response.data)
        
        # Delete the note
        response = client.delete(f'/notes/{note["id"]}')
        
        assert response.status_code == 204
        
        # Verify note is gone
        get_response = client.get(f'/notes/{note["id"]}')
        assert get_response.status_code == 404


class TestSecurity:
    """Test security features."""
    
    def test_user_cannot_access_other_notes(self, client):
        """Test that users cannot access notes belonging to other users."""
        # Create first user and note
        user1_data = {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'password123'
        }
        client.post('/signup',
                   data=json.dumps(user1_data),
                   content_type='application/json')
        
        note_data = {
            'title': 'User 1 Note',
            'content': 'Private content'
        }
        create_response = client.post('/notes',
                                     data=json.dumps(note_data),
                                     content_type='application/json')
        user1_note = json.loads(create_response.data)
        
        # Logout and create second user
        client.delete('/logout')
        
        user2_data = {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'password123'
        }
        client.post('/signup',
                   data=json.dumps(user2_data),
                   content_type='application/json')
        
        # Try to access user1's note as user2
        response = client.get(f'/notes/{user1_note["id"]}')
        assert response.status_code == 404
        
        # Try to update user1's note as user2
        update_data = {'title': 'Hacked!'}
        response = client.patch(f'/notes/{user1_note["id"]}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        assert response.status_code == 404
        
        # Try to delete user1's note as user2
        response = client.delete(f'/notes/{user1_note["id"]}')
        assert response.status_code == 404


class TestHealthCheck:
    """Test utility endpoints."""
    
    def test_home_endpoint(self, client):
        """Test the home/health check endpoint."""
        response = client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'running'
        assert data['auth_method'] == 'sessions'


if __name__ == '__main__':
    pytest.main(['-v', __file__])