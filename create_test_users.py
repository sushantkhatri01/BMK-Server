#!/usr/bin/env python3
"""
BMK Server - Generate 60 Test Users
Creates realistic test user data for load testing and demo purposes
"""

import sys
sys.path.insert(0, '.')

from server import SessionLocal, User
from datetime import datetime
import random

def create_test_users(count=60):
    """Create test users in the database"""
    db = SessionLocal()
    
    roles = ["admin", "worker", "manager", "supervisor"]
    locations = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
        "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal"
    ]
    
    created_count = 0
    skipped_count = 0
    
    print(f"Creating {count} test users...")
    print("-" * 60)
    
    for i in range(1, count + 1):
        username = f"testuser{i}"
        email = f"testuser{i}@bmk.local"
        name = f"Test User {i}"
        phone = f"+91{random.randint(6000000000, 9999999999)}"
        location = random.choice(locations)
        role = random.choice(roles)
        
        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            skipped_count += 1
            print(f"  [{i:2d}] ⊘ {email} (already exists)")
            continue
        
        # Create new user
        user = User(
            email=email,
            name=name,
            role=role,
            password_hash="$2b$12$placeholder"  # Placeholder hash
        )
        
        db.add(user)
        created_count += 1
        print(f"  [{i:2d}] ✓ {email} ({role}) - {location}")
        
        # Commit every 10 users
        if i % 10 == 0:
            db.commit()
            print(f"       → Committed {created_count} users...")
    
    # Final commit
    db.commit()
    db.close()
    
    print("-" * 60)
    print(f"✓ Created: {created_count} users")
    print(f"⊘ Skipped: {skipped_count} users (already exist)")
    print(f"✓ Total in database: {created_count + skipped_count}")
    print("")
    print("Test users created successfully!")
    print("")
    print("Login credentials:")
    print("  Username: testuser1 to testuser60")
    print("  Password: (use any password, will be hashed)")
    print("  Email: testuser<N>@bmk.local")
    print("")
    print("Sample test users:")
    for i in [1, 30, 60]:
        print(f"  • testuser{i}@bmk.local")

if __name__ == "__main__":
    try:
        # Check if server can load
        print("Loading server configuration...")
        from server import Base, engine
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✓ Database initialized")
        print("")
        
        # Create users
        create_test_users(60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
