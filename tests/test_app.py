"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to their initial state after each test"""
    from app import activities
    
    initial_state = {
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
            "description": "Competitive basketball training and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Soccer practice and friendly matches",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["marcus@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific experiments and discoveries",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Club": {
            "description": "Painting, drawing, and mixed media artistic expression",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, theater productions, and stage performance",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["ethan@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    yield
    
    # Restore initial state
    activities.clear()
    activities.update(initial_state)


# Tests for GET /
class TestRoot:
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


# Tests for GET /activities
class TestGetActivities:
    def test_get_all_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activity_structure(self, client, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess = data["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess
        assert isinstance(chess["participants"], list)
    
    def test_activity_participants(self, client, reset_activities):
        """Test that participants are correctly returned"""
        response = client.get("/activities")
        data = response.json()
        
        chess = data["Chess Club"]
        assert "michael@mergington.edu" in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]


# Tests for POST /activities/{activity_name}/signup
class TestSignup:
    def test_signup_new_student(self, client, reset_activities):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_updates_participants(self, client, reset_activities):
        """Test that signing up adds student to participants list"""
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signup returns error"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for non-existent activity returns error"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


# Tests for POST /activities/{activity_name}/unregister
class TestUnregister:
    def test_unregister_existing_student(self, client, reset_activities):
        """Test unregistering an existing student"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregistering removes student from participants list"""
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_student(self, client, reset_activities):
        """Test unregistering a student not in the activity"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notastudent@mergington.edu"}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


# Integration tests
class TestIntegration:
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test complete flow: signup then unregister"""
        email = "integration@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify removed
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity]["participants"]
    
    def test_multiple_students_signup(self, client, reset_activities):
        """Test multiple students can sign up for same activity"""
        activity = "Drama Club"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for student in students:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": student}
            )
            assert response.status_code == 200
        
        # Verify all added
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for student in students:
            assert student in participants
