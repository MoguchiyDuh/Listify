import pytest

from app.crud import user_crud


@pytest.mark.crud
class TestUserCRUD:
    """Tests for user CRUD operations"""

    def test_create_user(self, db_session):
        """Test creating a user"""
        user = user_crud.create(
            db_session,
            username="newuser",
            email="new@example.com",
            password="password123",
        )

        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.hashed_password != "password123"  # Password should be hashed

    def test_get_user_by_id(self, db_session, sample_user):
        """Test getting a user by ID"""
        user = user_crud.get(db_session, sample_user.id)

        assert user is not None
        assert user.id == sample_user.id
        assert user.username == sample_user.username

    def test_get_user_by_email(self, db_session, sample_user):
        """Test getting a user by email"""
        user = user_crud.get_by_email(db_session, email=sample_user.email)

        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    def test_get_user_by_username(self, db_session, sample_user):
        """Test getting a user by username"""
        user = user_crud.get_by_username(db_session, username=sample_user.username)

        assert user is not None
        assert user.id == sample_user.id
        assert user.username == sample_user.username

    def test_authenticate_user_success(self, db_session, sample_user):
        """Test successful user authentication"""
        user = user_crud.authenticate(
            db_session, username="testuser", password="testpassword123"
        )

        assert user is not None
        assert user.id == sample_user.id

    def test_authenticate_user_wrong_password(self, db_session, sample_user):
        """Test authentication with wrong password"""
        user = user_crud.authenticate(
            db_session, username="testuser", password="wrongpassword"
        )

        assert user is None

    def test_authenticate_user_not_found(self, db_session):
        """Test authentication with non-existent user"""
        user = user_crud.authenticate(
            db_session, username="nonexistent", password="password123"
        )

        assert user is None

    def test_update_user(self, db_session, sample_user):
        """Test updating a user"""
        updated_user = user_crud.update(
            db_session,
            user=sample_user,
            username="updateduser",
            email="updated@example.com",
        )

        assert updated_user.username == "updateduser"
        assert updated_user.email == "updated@example.com"

    def test_update_user_password(self, db_session, sample_user):
        """Test updating user password"""
        old_password_hash = sample_user.hashed_password

        updated_user = user_crud.update(
            db_session, user=sample_user, password="newpassword123"
        )

        assert updated_user.hashed_password != old_password_hash

        # Verify new password works
        auth_user = user_crud.authenticate(
            db_session, username=sample_user.username, password="newpassword123"
        )
        assert auth_user is not None

    def test_delete_user(self, db_session, sample_user):
        """Test deleting a user"""
        user_id = sample_user.id

        result = user_crud.delete(db_session, id=user_id)

        assert result is True

        # Verify user is deleted
        user = user_crud.get(db_session, user_id)
        assert user is None

    def test_get_multi_users(self, db_session):
        """Test getting multiple users"""
        # Create multiple users
        for i in range(5):
            user_crud.create(
                db_session,
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="password123",
            )

        users = user_crud.get_multi(db_session, skip=0, limit=10)

        assert len(users) == 5
