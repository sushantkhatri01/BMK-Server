#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://192.168.0.9:8001"

# Test 1: Create user with minimal parameters (like Flutter app does)
print("Test 1: Create user with name only")
response = requests.post(f"{BASE_URL}/users", json={"name": "Test User"})
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}\n")

# Test 2: Get tasks
print("Test 2: Get tasks")
response = requests.get(f"{BASE_URL}/tasks")
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}\n")

# Test 3: Create task
print("Test 3: Create task")
task_data = {
    "title": "Fix the app",
    "description": "Debug the API calls",
    "status": "open",
    "user_id": 1
}
response = requests.post(f"{BASE_URL}/tasks", json=task_data)
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}\n")

print("All tests completed!")
