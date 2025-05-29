"""
Database Seeding Script

This script populates the database with sample users and notes for development and testing.
"""

from faker import Faker
from random import randint, choice
from app import app
from models import db, User, Note

fake = Faker()

def seed_database():
    """Seed the database with sample data."""
    
    with app.app_context():
        print("🗑️  Clearing existing data...")
        
        # Clear existing data
        Note.query.delete()
        User.query.delete()
        db.session.commit()
        
        print("👥 Creating sample users...")
        
        # Create sample users
        users = []
        
        # Create a test user with known credentials
        test_user = User(
            username='testuser',
            email='test@example.com'
        )
        test_user.password_hash = 'password123'
        users.append(test_user)
        
        # Create additional random users
        for i in range(9):
            username = fake.user_name()
            # Ensure unique usernames
            while any(u.username == username for u in users):
                username = fake.user_name()
            
            user = User(
                username=username,
                email=fake.email()
            )
            user.password_hash = 'password123'  # Same password for all test users
            users.append(user)
        
        db.session.add_all(users)
        db.session.commit()
        
        print(f"✅ Created {len(users)} users")
        
        print("📝 Creating sample notes...")
        
        # Create sample notes for each user
        notes = []
        note_templates = [
            "Project Meeting Notes",
            "Daily Reflection",
            "Book Summary",
            "Ideas and Inspiration",
            "Travel Plans",
            "Recipe Collection",
            "Workout Log",
            "Learning Notes",
            "Personal Goals",
            "Shopping List"
        ]
        
        content_templates = [
            "This is a detailed note about my thoughts and observations.",
            "Today I learned something new and wanted to document it here.",
            "Important points to remember for future reference.",
            "A collection of ideas that came to mind during my walk.",
            "Meeting notes from today's discussion with the team.",
            "Personal reflections on recent experiences and growth.",
            "Research findings and key insights from my reading.",
            "Creative thoughts and potential project ideas.",
            "Daily planning and priority setting for productivity.",
            "Observations and lessons learned from recent events."
        ]
        
        for user in users:
            # Create 5-15 notes per user
            num_notes = randint(5, 15)
            
            for _ in range(num_notes):
                note = Note(
                    title=choice(note_templates) + f" #{randint(1, 100)}",
                    content=fake.paragraph(nb_sentences=randint(3, 8)) + "\n\n" + choice(content_templates),
                    user_id=user.id
                )
                notes.append(note)
        
        db.session.add_all(notes)
        db.session.commit()
        
        print(f"✅ Created {len(notes)} notes")
        
        print("\n🎉 Database seeding completed!")
        print("\n📊 Summary:")
        print(f"   Users: {User.query.count()}")
        print(f"   Notes: {Note.query.count()}")
        
        print("\n🔑 Test Account:")
        print("   Username: testuser")
        print("   Email: test@example.com")
        print("   Password: password123")
        
        print(f"\n📝 Sample notes for testuser: {Note.query.filter_by(user_id=test_user.id).count()}")


if __name__ == '__main__':
    seed_database()