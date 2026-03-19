"""
Test suite for Mergington High School Activities API
Using AAA (Arrange-Act-Assert) pattern for test structure
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Should return all available activities"""
        # Arrange
        expected_activity = "Chess Club"
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert expected_activity in data
        assert len(data) >= 3
    
    def test_get_activities_includes_required_fields(self, client, reset_activities):
        """Should include description, schedule, max_participants, and participants"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"
    
    def test_get_activities_participants_is_list(self, client, reset_activities):
        """Should have participants as a list"""
        # Arrange
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity in data.values():
            assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_succeeds(self, client, reset_activities):
        """Should successfully add a new participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
        
        # Verify participant was actually added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email in participants
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Should reject duplicate signup with 400 error"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Should return 404 for nonexistent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_response_contains_message(self, client, reset_activities):
        """Should return a message field in response"""
        # Arrange
        activity_name = "Programming Class"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_succeeds(self, client, reset_activities):
        """Should successfully remove a participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]
        
        # Verify participant was actually removed
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email not in participants
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Should return 400 when participant not registered"""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity_fails(self, client, reset_activities):
        """Should return 404 for nonexistent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_response_contains_message(self, client, reset_activities):
        """Should return a message field in response"""
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)


class TestIntegrationScenarios:
    """Integration tests for multi-step workflows"""
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Should handle signup followed by unregister"""
        # Arrange
        activity_name = "Gym Class"
        email = "workflow@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert signup succeeded
        assert signup_response.status_code == 200
        
        # Verify participant is in list
        get_response = client.get("/activities")
        assert email in get_response.json()[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert unregister succeeded
        assert unregister_response.status_code == 200
        
        # Verify participant is removed
        get_response = client.get("/activities")
        assert email not in get_response.json()[activity_name]["participants"]
    
    def test_multiple_signups_same_activity(self, client, reset_activities):
        """Should allow multiple different participants to sign up"""
        # Arrange
        activity_name = "Programming Class"
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        # Act - Sign up multiple users
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert all are in the list
        get_response = client.get("/activities")
        participants = get_response.json()[activity_name]["participants"]
        for email in emails:
            assert email in participants
