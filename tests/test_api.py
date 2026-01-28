"""
Comprehensive API Endpoint Tests
Testing all endpoints in app.py with 2-3 tests per endpoint
"""
import pytest
from unittest.mock import patch, Mock
from utils.util import get_password_hash


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_returns_correct_info(self, client):
        """Test root endpoint returns expected data"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello Godslighthouse Starter Kit Server"
        assert data["version"] == "1.0.0"


class TestRegisterEndpoint:
    """Tests for /api/auth/register"""
    
    @patch('app.database')
    def test_register_success(self, mock_db, client, sample_user, mock_database):
        """Test successful user registration"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        
        response = client.post("/api/auth/register", json=sample_user)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] is True
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["message"] == "User registered successfully"
    
    @patch('app.database')
    def test_register_duplicate_user(self, mock_db, client, sample_user, mock_database):
        """Test registration fails when user already exists"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["users_collection"].find_one.return_value = {
            "phone_or_email": sample_user["phone_or_email"]
        }
        
        response = client.post("/api/auth/register", json=sample_user)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestLoginEndpoint:
    """Tests for /api/auth/login"""
    
    @patch('app.database')
    def test_login_success(self, mock_db, client, sample_user, mock_database):
        """Test successful login with correct credentials"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["users_collection"].find_one.return_value = {
            "phone_or_email": sample_user["phone_or_email"],
            "hashed_password": get_password_hash(sample_user["password"])
        }
        
        response = client.post("/api/auth/login", json=sample_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert "access_token" in data
        assert data["user_identifier"] == sample_user["phone_or_email"]
    
    @patch('app.database')
    def test_login_wrong_password(self, mock_db, client, sample_user, mock_database):
        """Test login fails with wrong password"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["users_collection"].find_one.return_value = {
            "phone_or_email": sample_user["phone_or_email"],
            "hashed_password": get_password_hash("WrongPassword123!")
        }
        
        response = client.post("/api/auth/login", json=sample_user)
        
        assert response.status_code == 401
        assert "Incorrect phone/email or password" in response.json()["detail"]
    
    @patch('app.database')
    def test_login_user_not_found(self, mock_db, client, sample_user, mock_database):
        """Test login fails when user doesn't exist"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        
        response = client.post("/api/auth/login", json=sample_user)
        
        assert response.status_code == 401
        assert "Incorrect phone/email or password" in response.json()["detail"]


class TestProgressUploadEndpoint:
    """Tests for /api/progress/upload"""
    
    @patch('app.database')
    def test_upload_progress_success(self, mock_db, client, sample_progress, mock_database):
        """Test successful progress upload"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        
        response = client.post("/api/progress/upload", json=sample_progress)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["message"] == "Progress uploaded successfully"
        
        # Verify upsert was called
        mock_database["progress_collection"].update_one.assert_called_once()
    
    @patch('app.database')
    def test_upload_progress_database_error(self, mock_db, client, sample_progress, mock_database):
        """Test progress upload handles database errors"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["progress_collection"].update_one.side_effect = Exception("DB Error")
        
        response = client.post("/api/progress/upload", json=sample_progress)
        
        assert response.status_code == 500
        assert "Failed to upload progress" in response.json()["detail"]


class TestProgressDownloadEndpoint:
    """Tests for /api/progress/download/{user_identifier}"""
    
    @patch('app.database')
    def test_download_progress_success(self, mock_db, client, sample_progress, mock_database):
        """Test successful progress download"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["progress_collection"].find_one.return_value = sample_progress
        
        response = client.get(f"/api/progress/download/{sample_progress['user_identifier']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["user_identifier"] == sample_progress["user_identifier"]
    
    @patch('app.database')
    def test_download_progress_not_found(self, mock_db, client, mock_database):
        """Test progress download when no data exists"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        
        response = client.get("/api/progress/download/nonexistent@example.com")
        
        assert response.status_code == 404
        assert "No progress found" in response.json()["detail"]


class TestNotesBackupEndpoint:
    """Tests for /api/notes/backup"""
    
    @patch('app.database')
    def test_backup_notes_success(self, mock_db, client, sample_notes, mock_database):
        """Test successful notes backup"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        
        response = client.post("/api/notes/backup", json=sample_notes)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["message"] == "Notes backed up successfully"
        
        # Verify upsert was called
        mock_database["notes_collection"].update_one.assert_called_once()
    
    @patch('app.database')
    def test_backup_notes_database_error(self, mock_db, client, sample_notes, mock_database):
        """Test notes backup handles database errors"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["notes_collection"].update_one.side_effect = Exception("DB Error")
        
        response = client.post("/api/notes/backup", json=sample_notes)
        
        assert response.status_code == 500
        assert "Failed to backup notes" in response.json()["detail"]


class TestNotesRetrieveEndpoint:
    """Tests for /api/notes/retrieve/{user_identifier}"""
    
    @patch('app.database')
    def test_retrieve_notes_success(self, mock_db, client, sample_notes, mock_database):
        """Test successful notes retrieval"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["notes_collection"].find_one.return_value = sample_notes
        
        response = client.get(f"/api/notes/retrieve/{sample_notes['user_identifier']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["user_identifier"] == sample_notes["user_identifier"]
    
    @patch('app.database')
    def test_retrieve_notes_not_found(self, mock_db, client, mock_database):
        """Test notes retrieval when no notes exist"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        
        response = client.get("/api/notes/retrieve/nonexistent@example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["notes"] == {}
        assert "No notes found" in data["data"]["message"]


class TestVerifyTokenEndpoint:
    """Tests for /api/auth/verify"""
    
    def test_verify_valid_token(self, client, auth_token):
        """Test verification with valid token"""
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["valid"] is True
    
    def test_verify_without_token(self, client):
        """Test verification without token"""
        response = client.get("/api/auth/verify")
        
        assert response.status_code == 401


class TestRefreshTokenEndpoint:
    """Tests for /api/auth/refresh"""
    
    def test_refresh_token_success(self, client, auth_token):
        """Test successful token refresh"""
        response = client.post(
            "/api/auth/refresh",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_without_token(self, client):
        """Test refresh without authorization"""
        response = client.post("/api/auth/refresh")
        
        assert response.status_code == 401


class TestChangePasswordEndpoint:
    """Tests for /api/auth/change-password"""
    
    @patch('app.database')
    def test_change_password_success(self, mock_db, client, mock_database):
        """Test successful password change"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        old_password = "OldPassword123!"
        mock_database["users_collection"].find_one.return_value = {
            "phone_or_email": "test@example.com",
            "hashed_password": get_password_hash(old_password)
        }
        
        response = client.post("/api/auth/change-password", json={
            "user_identifier": "test@example.com",
            "old_password": old_password,
            "new_password": "NewPassword123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["message"] == "Password changed successfully"
    
    @patch('app.database')
    def test_change_password_wrong_old_password(self, mock_db, client, mock_database):
        """Test password change with incorrect old password"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["users_collection"].find_one.return_value = {
            "phone_or_email": "test@example.com",
            "hashed_password": get_password_hash("CorrectOldPassword123!")
        }
        
        response = client.post("/api/auth/change-password", json={
            "user_identifier": "test@example.com",
            "old_password": "WrongPassword123!",
            "new_password": "NewPassword123!"
        })
        
        assert response.status_code == 401
        assert "Incorrect old password" in response.json()["detail"]


# class TestDeleteAccountEndpoint:
#     """Tests for /api/auth/delete-account"""
    
#     @patch('app.database')
#     def test_delete_account_success(self, mock_db, client, mock_database):
#         """Test successful account deletion"""
#         mock_db.__getitem__.side_effect = mock_database.__getitem__
#         password = "Password123!"
#         mock_database["users_collection"].find_one.return_value = {
#             "phone_or_email": "test@example.com",
#             "hashed_password": get_password_hash(password)
#         }
        
#         response = client.delete("/api/auth/delete-account", json={
#             "user_identifier": "test@example.com",
#             "password": password
#         })
        
#         assert response.status_code == 200
#         data = response.json()
#         assert data["status"] is True
#         assert "deleted successfully" in data["message"]
        
#         # Verify all collections were called to delete data
#         mock_database["users_collection"].delete_one.assert_called_once()
#         mock_database["progress_collection"].delete_one.assert_called_once()
#         mock_database["notes_collection"].delete_one.assert_called_once()
    
#     @patch('app.database')
#     def test_delete_account_wrong_password(self, mock_db, client, mock_database):
#         """Test account deletion with wrong password"""
#         mock_db.__getitem__.side_effect = mock_database.__getitem__
#         mock_database["users_collection"].find_one.return_value = {
#             "phone_or_email": "test@example.com",
#             "hashed_password": get_password_hash("CorrectPassword123!")
#         }
        
#         response = client.delete("/api/auth/delete-account", json={
#             "user_identifier": "test@example.com",
#             "password": "WrongPassword123!"
#         })
        
#         assert response.status_code == 401
#         assert "Incorrect password" in response.json()["detail"]


class TestUserProfileEndpoint:
    """Tests for /api/user/profile/{user_identifier}"""
    
    @patch('app.database')
    def test_get_profile_success(self, mock_db, client, mock_database):
        """Test successful profile retrieval"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["users_collection"].find_one.return_value = {
            "phone_or_email": "test@example.com",
            "created_at": "2026-01-28T12:00:00"
        }
        
        response = client.get("/api/user/profile/test@example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["phone_or_email"] == "test@example.com"
    
    @patch('app.database')
    def test_get_profile_not_found(self, mock_db, client, mock_database):
        """Test profile retrieval for non-existent user"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        
        response = client.get("/api/user/profile/nonexistent@example.com")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestDeleteNoteEndpoint:
    """Tests for /api/notes/delete/{user_identifier}/{audio_id}"""
    
    @patch('app.database')
    def test_delete_note_success(self, mock_db, client, mock_database):
        """Test successful note deletion"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["notes_collection"].update_one.return_value = Mock(matched_count=1)
        
        response = client.delete("/api/notes/delete/test@example.com/audio_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert "deleted successfully" in data["message"]
    
    @patch('app.database')
    def test_delete_note_user_not_found(self, mock_db, client, mock_database):
        """Test note deletion when user doesn't exist"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["notes_collection"].update_one.return_value = Mock(matched_count=0)
        
        response = client.delete("/api/notes/delete/nonexistent@example.com/audio_001")
        
        assert response.status_code == 404
        assert "User notes not found" in response.json()["detail"]


class TestResetProgressEndpoint:
    """Tests for /api/progress/reset/{user_identifier}"""
    
    @patch('app.database')
    def test_reset_progress_success(self, mock_db, client, mock_database):
        """Test successful progress reset"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["progress_collection"].delete_one.return_value = Mock(deleted_count=1)
        
        response = client.delete("/api/progress/reset/test@example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert "reset successfully" in data["message"]
    
    @patch('app.database')
    def test_reset_progress_not_found(self, mock_db, client, mock_database):
        """Test progress reset when no progress exists"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["progress_collection"].delete_one.return_value = Mock(deleted_count=0)
        
        response = client.delete("/api/progress/reset/nonexistent@example.com")
        
        assert response.status_code == 404
        assert "No progress found" in response.json()["detail"]


class TestUserStatsEndpoint:
    """Tests for /api/stats/{user_identifier}"""
    
    @patch('app.database')
    def test_get_stats_with_data(self, mock_db, client, mock_database):
        """Test stats retrieval when user has data"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        mock_database["progress_collection"].find_one.return_value = {
            "user_identifier": "test@example.com",
            "current_level": "level1",
            "current_week": 2,
            "updated_at": "2026-01-28T12:00:00"
        }
        mock_database["notes_collection"].find_one.return_value = {
            "user_identifier": "test@example.com",
            "notes": {"audio_001": "Note 1", "audio_002": "Note 2"}
        }
        
        response = client.get("/api/stats/test@example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["has_progress"] is True
        assert data["data"]["current_level"] == "level1"
        assert data["data"]["notes_count"] == 2
    
    @patch('app.database')
    def test_get_stats_without_data(self, mock_db, client, mock_database):
        """Test stats retrieval when user has no data"""
        mock_db.__getitem__.side_effect = mock_database.__getitem__
        
        response = client.get("/api/stats/test@example.com")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert data["data"]["has_progress"] is False
        assert data["data"]["notes_count"] == 0