"""
Pytest configuration and shared fixtures for FastAPI tests.

This module provides:
- client fixture with TestClient and fresh activity data for each test
- activities_data fixture with initial activity data structure reference
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities as app_activities


@pytest.fixture
def client():
    """
    Provide a TestClient for making HTTP requests to the FastAPI application.
    
    This fixture resets the app's global activities dictionary to initial state
    before each test, ensuring tests don't share state.
    """
    # Reset activities to initial state before each test
    _reset_activities()
    return TestClient(app)


def _get_initial_activities():
    """Return the initial state of all activities."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for tournament play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["sarah@mergington.edu", "alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["tyler@mergington.edu", "grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and experiments",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        }
    }


def _reset_activities():
    """Reset the app's activities to their initial state."""
    # Clear and reset the global activities dict in the app module
    app_activities.clear()
    app_activities.update(_get_initial_activities())


def _reset_activities():
    """Reset the app's activities to their initial state."""
    # Clear and reset the global activities dict in the app module
    app_activities.clear()
    app_activities.update(_get_initial_activities())


@pytest.fixture
def activities_data():
    """
    Provide reference to initial activity data structure.
    
    Returns a dictionary with 9 activities for reference/documentation purposes.
    For actual tests, the client fixture resets the app's global activities.
    """
    return _get_initial_activities()
