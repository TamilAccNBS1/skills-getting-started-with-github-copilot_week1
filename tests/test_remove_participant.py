"""
Tests for DELETE /activities/{activity_name}/participants endpoint.

Tests the participant removal functionality using AAA (Arrange-Act-Assert) pattern.
Covers happy path, non-existent participant, and invalid activity cases.
"""

import pytest


class TestRemoveParticipant:
    """Test suite for removing students from activities."""

    def test_remove_existing_participant_success(self, client):
        """
        Test: Existing participant can be successfully removed from activity.
        
        Arrange: Select activity with existing participants (Chess Club has michael@mergington.edu)
        Act: DELETE request to remove participant
        Assert: Response is 200, confirmation message, participant no longer in list
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"  # Known participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email_to_remove not in activities[activity_name]["participants"]

    def test_remove_non_existent_participant_returns_404(self, client):
        """
        Test: Removing non-existent participant returns 404 Not Found.
        
        Arrange: Use email not signed up for Tennis Club
        Act: DELETE request to remove non-existent participant
        Assert: Response is 404, error message indicates student not signed up
        """
        # Arrange
        activity_name = "Tennis Club"
        non_existent_email = "notasignedupstudent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": non_existent_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"].lower()

    def test_remove_from_invalid_activity_returns_404(self, client):
        """
        Test: Removing from non-existent activity returns 404 Not Found.
        
        Arrange: Use activity name that doesn't exist
        Act: DELETE request with invalid activity name
        Assert: Response is 404, error message indicates activity not found
        """
        # Arrange
        invalid_activity = "Ghost Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_participant_preserves_others(self, client):
        """
        Test: Removing one participant doesn't affect others in same activity.
        
        Arrange: Drama Club has 2 participants (tyler@mergington.edu, grace@mergington.edu)
        Act: Remove tyler
        Assert: grace still in participants, count decreased by 1
        """
        # Arrange
        activity_name = "Drama Club"
        email_to_remove = "tyler@mergington.edu"
        other_email = "grace@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify count decreased by 1
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        updated_participants = updated_activities[activity_name]["participants"]
        
        assert len(updated_participants) == initial_count - 1
        assert email_to_remove not in updated_participants
        assert other_email in updated_participants  # Other participant still there

    def test_remove_last_participant_from_activity(self, client):
        """
        Test: Can remove the last (only) participant from an activity.
        
        Arrange: Basketball Team has 1 participant (james@mergington.edu)
        Act: Remove the only participant
        Assert: Response is 200, participant list becomes empty
        """
        # Arrange
        activity_name = "Basketball Team"
        only_email = "james@mergington.edu"
        
        # Verify Basketball Team has james
        check_response = client.get("/activities")
        check_activities = check_response.json()
        assert only_email in check_activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": only_email}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify participants list is now empty
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        assert len(updated_activities[activity_name]["participants"]) == 0

    def test_remove_participant_twice_second_fails(self, client):
        """
        Test: Attempting to remove already-removed participant fails.
        
        Arrange: Select participant and remove once successfully
        Act: Attempt to remove same participant again
        Assert: First removal succeeds (200), second removal fails (404)
        """
        # Arrange
        activity_name = "Art Studio"
        email = "isabella@mergington.edu"
        
        # Act - First removal
        response1 = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Act - Second removal attempt
        response2 = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 404
        assert "not signed up" in response2.json()["detail"].lower()
