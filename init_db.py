from app import create_app, db
from app.models import User, Link  # Import your models

app = create_app()

def init_database():
    with app.app_context():
        # Drop all tables (use with caution in production!)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Optional: Add test data
        if not User.query.first():
            test_user = User(username='test', email='test@example.com')
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
            print("Created test user!")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()