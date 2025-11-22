import pytest
from crud.user import user_crud
from sqlalchemy.orm import Session


@pytest.mark.crud
class TestUserCRUD:
    """Test User CRUD operations"""

    def test_create_user(self, clean_db: Session):
        """Test creating a user"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password != "testpassword123"
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_get_user_by_id(self, clean_db: Session):
        """Test getting user by ID"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        fetched_user = user_crud.get(db=clean_db, id=user.id)

        assert fetched_user is not None
        assert fetched_user.id == user.id
        assert fetched_user.username == user.username
        assert fetched_user.email == user.email

    def test_get_user_by_email(self, clean_db: Session):
        """Test getting user by email"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        fetched_user = user_crud.get_by_email(db=clean_db, email="test@example.com")

        assert fetched_user is not None
        assert fetched_user.id == user.id
        assert fetched_user.email == "test@example.com"

    def test_get_user_by_username(self, clean_db: Session):
        """Test getting user by username"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        fetched_user = user_crud.get_by_username(db=clean_db, username="testuser")

        assert fetched_user is not None
        assert fetched_user.id == user.id
        assert fetched_user.username == "testuser"

    def test_get_nonexistent_user(self, clean_db: Session):
        """Test getting non-existent user returns None"""
        fetched_user = user_crud.get(db=clean_db, id=999)
        assert fetched_user is None

        fetched_user = user_crud.get_by_email(
            db=clean_db, email="nonexistent@example.com"
        )
        assert fetched_user is None

        fetched_user = user_crud.get_by_username(db=clean_db, username="nonexistent")
        assert fetched_user is None

    def test_get_multi_users(self, clean_db: Session):
        """Test getting multiple users"""
        user_crud.create(
            db=clean_db,
            username="user1",
            email="user1@example.com",
            password="password123",
        )
        user_crud.create(
            db=clean_db,
            username="user2",
            email="user2@example.com",
            password="password123",
        )
        user_crud.create(
            db=clean_db,
            username="user3",
            email="user3@example.com",
            password="password123",
        )

        users = user_crud.get_multi(db=clean_db, skip=0, limit=100)

        assert len(users) == 3

    def test_get_multi_with_pagination(self, clean_db: Session):
        """Test pagination"""
        for i in range(5):
            user_crud.create(
                db=clean_db,
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="password123",
            )

        users = user_crud.get_multi(db=clean_db, skip=0, limit=2)
        assert len(users) == 2

        users = user_crud.get_multi(db=clean_db, skip=2, limit=2)
        assert len(users) == 2

        users = user_crud.get_multi(db=clean_db, skip=4, limit=2)
        assert len(users) == 1

    def test_update_user_username(self, clean_db: Session):
        """Test updating user username"""
        user = user_crud.create(
            db=clean_db,
            username="oldusername",
            email="test@example.com",
            password="testpassword123",
        )

        updated_user = user_crud.update(db=clean_db, user=user, username="newusername")

        assert updated_user.username == "newusername"
        assert updated_user.email == "test@example.com"

    def test_update_user_email(self, clean_db: Session):
        """Test updating user email"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="old@example.com",
            password="testpassword123",
        )

        updated_user = user_crud.update(db=clean_db, user=user, email="new@example.com")

        assert updated_user.email == "new@example.com"
        assert updated_user.username == "testuser"

    def test_update_user_password(self, clean_db: Session):
        """Test updating user password"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="oldpassword",
        )
        old_hash = user.hashed_password

        updated_user = user_crud.update(db=clean_db, user=user, password="newpassword")

        assert updated_user.hashed_password != old_hash
        assert updated_user.hashed_password != "newpassword"

    def test_delete_user(self, clean_db: Session):
        """Test deleting user"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        result = user_crud.delete(db=clean_db, id=user.id)

        assert result is True

        fetched_user = user_crud.get(db=clean_db, id=user.id)
        assert fetched_user is None

    def test_delete_nonexistent_user(self, clean_db: Session):
        """Test deleting non-existent user"""
        result = user_crud.delete(db=clean_db, id=999)
        assert result is False

    def test_authenticate_valid_user(self, clean_db: Session):
        """Test authenticating with valid credentials"""
        user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        authenticated_user = user_crud.authenticate(
            db=clean_db, username="testuser", password="testpassword123"
        )

        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"

    def test_authenticate_invalid_username(self, clean_db: Session):
        """Test authenticating with invalid username"""
        user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        authenticated_user = user_crud.authenticate(
            db=clean_db, username="wronguser", password="testpassword123"
        )

        assert authenticated_user is None

    def test_authenticate_invalid_password(self, clean_db: Session):
        """Test authenticating with invalid password"""
        user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        authenticated_user = user_crud.authenticate(
            db=clean_db, username="testuser", password="wrongpassword"
        )

        assert authenticated_user is None

    def test_is_active(self, clean_db: Session):
        """Test is_active check"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        assert user_crud.is_active(user) is True
