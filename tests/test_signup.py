"""
Tests for POST /activities/{activity_name}/signup endpoint.

Tests the signup functionality using AAA (Arrange-Act-Assert) pattern.
Covers happy path, duplicate signup, and invalid activity cases.
"""

import pytest


class TestSignupForActivity:
    """Test suite for signing up students for activities."""

    def test_signup_new_student_success(self, client):
        """
        Test: Student can successfully sign up for an activity.
        
        Arrange: Prepare valid activity name and new email not yet signed up
        Act: POST to /activities/{activity_name}/signup with email parameter
        Assert: Response is 200, confirmation message returned, participant added to activity
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity_name]["participants"]

    def test_signup_duplicate_email_returns_400(self, client):
        """
        Test: Duplicate signup attempt returns 400 Bad Request.
        
        Arrange: Use email already signed up for Chess Club (michael@mergington.edu)
        Act: POST to signup with existing email
        Assert: Response is 400, error message indicates already signed up
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_invalid_activity_returns_404(self, client):
        """
        Test: Signup to non-existent activity returns 404 Not Found.
        
        Arrange: Use activity name that doesn't exist
        Act: POST to signup with invalid activity name
        Assert: Response is 404, error message indicates activity not found
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_multiple_students_same_activity(self, client):
        """
        Test: Multiple different students can sign up for the same activity.
        
        Arrange: Prepare two different emails not yet in Programming Class
        Act: Sign up first student, then second student to same activity
        Assert: Both signups succeed with 200 responses, both added to participants
        """
        # Arrange
        activity_name = "Programming Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        
        # Act - Second signup
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both participants added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_signup_preserves_existing_participants(self, client):
        """
        Test: Adding new participant doesn't remove existing ones.
        
        Arrange: Get initial participant count for Tennis Club (should be 2)
        Act: Sign up new student
        Assert: New count is 3, original participants still present
        """
        # Arrange
        activity_name = "Tennis Club"
        # Get initial state
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_participants = initial_activities[activity_name]["participants"].copy()
        initial_count = len(initial_participants)
        
        new_email = "tennis_newbie@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify count increased by 1
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        updated_participants = updated_activities[activity_name]["participants"]
        
        assert len(updated_participants) == initial_count + 1
        # Verify original participants still there
        for original_participant in initial_participants:
            assert original_participant in updated_participants
