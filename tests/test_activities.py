"""
Tests for GET /activities endpoint.

Tests the retrieval of all activities and verification of response structure.
"""

import pytest


class TestGetActivities:
    """Test suite for retrieving all activities."""

    def test_get_all_activities_returns_200(self, client):
        """
        Test: GET /activities returns 200 OK response.
        
        Arrange: No setup needed, activities are pre-populated in app
        Act: Make GET request to /activities endpoint
        Assert: Response status code is 200
        """
        # Arrange
        expected_status = 200
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == expected_status

    def test_get_activities_returns_all_nine_activities(self, client):
        """
        Test: GET /activities returns all 9 activities.
        
        Arrange: Expected 9 activities (Chess Club, Programming Class, etc.)
        Act: Make GET request to /activities endpoint
        Assert: Response contains exactly 9 activities
        """
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities) == expected_activity_count

    def test_get_activities_returns_correct_structure(self, client):
        """
        Test: Each activity has required fields.
        
        Arrange: Required fields are description, schedule, max_participants, participants
        Act: Make GET request to /activities endpoint
        Assert: Each activity contains all required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str), f"Activity name should be string, got {type(activity_name)}"
            assert set(activity_data.keys()) == required_fields, \
                f"Activity {activity_name} missing or has extra fields. Got {set(activity_data.keys())}"

    def test_get_activities_participants_are_lists(self, client):
        """
        Test: Participants field in each activity is a list.
        
        Arrange: Each activity should have participants as list of emails
        Act: Make GET request to /activities endpoint
        Assert: All participants fields are lists
        """
        # Arrange - no specific arrange needed
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Activity {activity_name} participants should be list, got {type(activity_data['participants'])}"
            # Optional: verify emails in the list are strings
            for participant in activity_data["participants"]:
                assert isinstance(participant, str), \
                    f"Participant in {activity_name} should be string email, got {type(participant)}"

    def test_get_activities_returns_specific_known_activity(self, client):
        """
        Test: Known activity 'Chess Club' is present with correct details.
        
        Arrange: Chess Club should have description, schedule, max 12 participants
        Act: Make GET request to /activities endpoint
        Assert: Chess Club data matches expected values
        """
        # Arrange
        expected_activity_name = "Chess Club"
        expected_description = "Learn strategies and compete in chess tournaments"
        expected_max = 12
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert expected_activity_name in activities
        chess_club = activities[expected_activity_name]
        assert chess_club["description"] == expected_description
        assert chess_club["max_participants"] == expected_max
