"""
Integration tests for multi-step workflows.

Tests complete workflows like signup → verify → remove, and complex scenarios
involving multiple participants and activities.
"""

import pytest


class TestSignupAndRemovalWorkflows:
    """Test suite for multi-step workflows combining signup and removal."""

    def test_full_workflow_signup_verify_remove(self, client):
        """
        Test: Complete workflow of signing up, verifying, and removing.
        
        Arrange: Select Science Olympiad and new email
        Act: 
            1. Sign up new student
            2. Verify student is in participants list
            3. Remove student
            4. Verify student is no longer present
        Assert: All operations succeed with correct state changes
        """
        # Arrange
        activity_name = "Science Olympiad"
        new_email = "workflow_test@mergington.edu"
        
        # Act 1 - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert 1
        assert signup_response.status_code == 200
        
        # Act 2 - Verify in list
        verify_response = client.get("/activities")
        verify_activities = verify_response.json()
        
        # Assert 2
        assert new_email in verify_activities[activity_name]["participants"]
        
        # Act 3 - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": new_email}
        )
        
        # Assert 3
        assert remove_response.status_code == 200
        
        # Act 4 - Verify removed
        final_response = client.get("/activities")
        final_activities = final_response.json()
        
        # Assert 4
        assert new_email not in final_activities[activity_name]["participants"]

    def test_multiple_students_signup_then_remove_one(self, client):
        """
        Test: Multiple students sign up, then one is removed.
        
        Arrange: Prepare 2 new emails
        Act:
            1. Sign up student 1
            2. Sign up student 2
            3. Remove student 1
            4. Verify student 2 still present, student 1 removed
        Assert: Final state shows only student 2 remaining
        """
        # Arrange
        activity_name = "Debate Team"
        email1 = "debater1@mergington.edu"
        email2 = "debater2@mergington.edu"
        
        # Act 1 - Sign up first student
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        
        # Assert 1
        assert response1.status_code == 200
        
        # Act 2 - Sign up second student
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert 2
        assert response2.status_code == 200
        
        # Verify both are present
        check_response = client.get("/activities")
        check_activities = check_response.json()
        assert email1 in check_activities[activity_name]["participants"]
        assert email2 in check_activities[activity_name]["participants"]
        
        # Act 3 - Remove first student
        remove_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email1}
        )
        
        # Assert 3
        assert remove_response.status_code == 200
        
        # Act 4 - Verify final state
        final_response = client.get("/activities")
        final_activities = final_response.json()
        
        # Assert 4
        assert email1 not in final_activities[activity_name]["participants"]
        assert email2 in final_activities[activity_name]["participants"]

    def test_student_signup_different_activities(self, client):
        """
        Test: Same student can sign up for multiple different activities.
        
        Arrange: Select student email and two different activities
        Act:
            1. Sign up student for Chess Club
            2. Sign up same student for Programming Class
            3. Get all activities and verify in both
        Assert: Student appears in participants of both activities
        """
        # Arrange
        student_email = "multitasker@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act 1 - Sign up for first activity
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": student_email}
        )
        
        # Assert 1
        assert response1.status_code == 200
        
        # Act 2 - Sign up for second activity
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": student_email}
        )
        
        # Assert 2
        assert response2.status_code == 200
        
        # Act 3 - Verify in both
        verify_response = client.get("/activities")
        verify_activities = verify_response.json()
        
        # Assert 3
        assert student_email in verify_activities[activity1]["participants"]
        assert student_email in verify_activities[activity2]["participants"]

    def test_activity_state_consistency_across_operations(self, client):
        """
        Test: Activity state remains consistent across multiple operations.
        
        Arrange: Track activity counts before and after operations
        Act:
            1. Get initial state of all activities
            2. Add 3 participants to different activities
            3. Remove 2 participants
            4. Get final state
        Assert: Counts and state match expectations
        """
        # Arrange
        changes = [
            ("Chess Club", "add", "add1@merger.edu"),
            ("Programming Class", "add", "add2@merger.edu"),
            ("Gym Class", "add", "add3@merger.edu"),
            ("Chess Club", "remove", "add1@merger.edu"),
            ("Programming Class", "remove", "add2@merger.edu"),
        ]
        
        # Act 1 - Get initial state
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_counts = {
            activity: len(data["participants"]) 
            for activity, data in initial_activities.items()
        }
        
        # Act 2-6 - Perform changes
        for activity_name, operation, email in changes:
            if operation == "add":
                client.post(
                    f"/activities/{activity_name}/signup",
                    params={"email": email}
                )
            elif operation == "remove":
                client.delete(
                    f"/activities/{activity_name}/participants",
                    params={"email": email}
                )
        
        # Act 7 - Get final state
        final_response = client.get("/activities")
        final_activities = final_response.json()
        final_counts = {
            activity: len(data["participants"]) 
            for activity, data in final_activities.items()
        }
        
        # Assert
        # Chess Club: +1 then -1 = no net change
        assert final_counts["Chess Club"] == initial_counts["Chess Club"]
        
        # Programming Class: +1 then -1 = no net change
        assert final_counts["Programming Class"] == initial_counts["Programming Class"]
        
        # Gym Class: +1 only = increase by 1
        assert final_counts["Gym Class"] == initial_counts["Gym Class"] + 1
        
        # Other activities unchanged
        for activity in initial_counts:
            if activity not in ["Chess Club", "Programming Class", "Gym Class"]:
                assert final_counts[activity] == initial_counts[activity]

    def test_error_states_do_not_modify_state(self, client):
        """
        Test: Failed operations don't change application state.
        
        Arrange: Get initial state
        Act:
            1. Attempt invalid signup (duplicate email)
            2. Attempt invalid removal (non-existent email)
            3. Attempt invalid activity access
        Assert: All fail with appropriate status codes, state unchanged
        """
        # Arrange
        activity_name = "Art Studio"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_state = {
            activity: data["participants"].copy()
            for activity, data in initial_activities.items()
        }
        
        # Act 1 - Attempt duplicate signup
        duplicate_email = "isabella@mergington.edu"  # Already in Art Studio
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )
        
        # Assert 1
        assert response1.status_code == 400
        
        # Act 2 - Attempt remove non-existent
        response2 = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": "phantom@mergington.edu"}
        )
        
        # Assert 2
        assert response2.status_code == 404
        
        # Act 3 - Attempt access invalid activity
        response3 = client.post(
            f"/activities/FakeActivity/signup",
            params={"email": "someone@mergington.edu"}
        )
        
        # Assert 3
        assert response3.status_code == 404
        
        # Act 4 - Verify state unchanged
        final_response = client.get("/activities")
        final_activities = final_response.json()
        
        # Assert 4 - All participants lists unchanged
        for activity, data in final_activities.items():
            assert data["participants"] == initial_state[activity], \
                f"State of {activity} was modified by failed operation"
