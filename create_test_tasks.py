#!/usr/bin/env python3
"""
BMK Server - Generate Test Tasks for 60 Users
Creates realistic test task data for load testing and demo purposes
"""

import sys
sys.path.insert(0, '.')

from server import SessionLocal, Task, User
from datetime import datetime
import random

def create_test_tasks(tasks_per_user=3):
    """Create test tasks for all users"""
    db = SessionLocal()
    
    # Task titles
    titles = [
        "Fix plumbing issue",
        "Clean garden",
        "Repair fence",
        "Paint house",
        "Install door",
        "Fix electrical outlet",
        "Clean gutters",
        "Repair roof",
        "Fix window",
        "Landscape yard",
        "Install flooring",
        "Paint walls",
        "Fix leaky tap",
        "Clean basement",
        "Repair steps",
        "Install shelves",
        "Fix drywall",
        "Repair deck",
        "Clean attic",
        "Install lights"
    ]
    
    descriptions = [
        "Urgent maintenance needed",
        "Regular upkeep required",
        "Scheduled maintenance",
        "Emergency repair",
        "Seasonal maintenance",
        "Quality improvement",
        "Safety inspection",
        "Customer request",
        "Preventive maintenance",
        "Damage repair"
    ]
    
    statuses = ["open", "in-progress", "completed", "pending"]
    
    # Get all users
    users = db.query(User).all()
    print(f"Found {len(users)} users")
    print(f"Creating {tasks_per_user} tasks per user ({len(users) * tasks_per_user} total)...")
    print("-" * 60)
    
    created_count = 0
    
    for user_idx, user in enumerate(users, 1):
        for task_num in range(tasks_per_user):
            title = random.choice(titles)
            description = random.choice(descriptions)
            status = random.choice(statuses)
            
            task = Task(
                title=f"{title} - {user.name}",
                description=description,
                status=status,
                user_id=user.id
            )
            
            db.add(task)
            created_count += 1
            
            # Progress indicator
            if created_count % 10 == 0:
                print(f"  ✓ Created {created_count} tasks...")
    
    # Commit all
    db.commit()
    db.close()
    
    print("-" * 60)
    print(f"✓ Created: {created_count} tasks")
    print(f"✓ Users: {len(users)}")
    print(f"✓ Tasks per user: {tasks_per_user}")
    print("")
    print("Task distribution:")
    print(f"  • Open: ~25%")
    print(f"  • In-progress: ~25%")
    print(f"  • Completed: ~25%")
    print(f"  • Pending: ~25%")
    print("")
    print("Task generation complete!")

if __name__ == "__main__":
    try:
        create_test_tasks(tasks_per_user=3)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
