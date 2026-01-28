"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Ensure the app module can be imported
sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    from app import app
    return TestClient(app)


@pytest.fixture
def mock_database():
    """Mock database collections with common behaviors"""
    mock_db = {
        "users_collection": MagicMock(),
        "progress_collection": MagicMock(),
        "notes_collection": MagicMock()
    }
    
    # Set up default return values
    mock_db["users_collection"].find_one.return_value = None
    mock_db["users_collection"].insert_one.return_value = MagicMock(inserted_id="test_id")
    mock_db["users_collection"].update_one.return_value = MagicMock(matched_count=1, modified_count=1)
    mock_db["users_collection"].delete_one.return_value = MagicMock(deleted_count=1)
    
    mock_db["progress_collection"].find_one.return_value = None
    mock_db["progress_collection"].update_one.return_value = MagicMock(matched_count=1, modified_count=1)
    mock_db["progress_collection"].delete_one.return_value = MagicMock(deleted_count=1)
    
    mock_db["notes_collection"].find_one.return_value = None
    mock_db["notes_collection"].update_one.return_value = MagicMock(matched_count=1, modified_count=1)
    mock_db["notes_collection"].delete_one.return_value = MagicMock(deleted_count=1)
    
    return mock_db


@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "phone_or_email": "test@example.com",
        "password": "SecurePassword123!"
    }


@pytest.fixture
def sample_progress():
    """Sample progress data for testing"""
    from datetime import datetime
    return {
        "user_identifier": "test@example.com",
        "progress": {"level1": {"week1": {"completed": True}}},
        "current_level": "level1",
        "current_week": 1,
        "current_audio": "audio_001",
        "updated_at": datetime.now().isoformat()
    }


@pytest.fixture
def sample_notes():
    """Sample notes data for testing"""
    from datetime import datetime
    return {
        "user_identifier": "test@example.com",
        "notes": {
            "audio_001": "First note",
            "audio_002": "Second note"
        },
        "updated_at": datetime.now().isoformat()
    }


@pytest.fixture
def auth_token():
    """Create a valid JWT token for testing"""
    from utils.util import create_access_token
    return create_access_token(data={"sub": "test@example.com"})