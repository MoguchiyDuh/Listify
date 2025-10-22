import pytest
from app.crud import UserCRUD
from app.schemas import UserCreate, UserUpdate


@pytest.mark.crud
class TestUserCRUD:

    def test_create_user(self, db_session):
        user_data = UserCreate(
            username="testuser", email="test@example.com", password="SecurePass123"
        )
        user = UserCRUD.create(db_session, user_data)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password != "SecurePass123"
        assert user.is_active is True
        assert user.id is not None

    def test_get_user_by_id(self, db_session):
        user_data = UserCreate(
            username="test", email="test@test.com", password="password123"
        )
        created_user = UserCRUD.create(db_session, user_data)

        fetched_user = UserCRUD.get_by_id(db_session, created_user.id)

        assert fetched_user is not None
        assert fetched_user.id == created_user.id
        assert fetched_user.username == "test"

    def test_get_user_by_username(self, db_session):
        user_data = UserCreate(
            username="uniqueuser", email="unique@test.com", password="password123"
        )
        UserCRUD.create(db_session, user_data)

        fetched_user = UserCRUD.get_by_username(db_session, "uniqueuser")

        assert fetched_user is not None
        assert fetched_user.username == "uniqueuser"

    def test_get_user_by_email(self, db_session):
        user_data = UserCreate(
            username="emailtest", email="email@test.com", password="password123"
        )
        UserCRUD.create(db_session, user_data)

        fetched_user = UserCRUD.get_by_email(db_session, "email@test.com")

        assert fetched_user is not None
        assert fetched_user.email == "email@test.com"

    def test_get_user_by_username_or_email(self, db_session):
        user_data = UserCreate(
            username="testuser", email="test@example.com", password="password123"
        )
        UserCRUD.create(db_session, user_data)

        by_username = UserCRUD.get_by_username_or_email(db_session, "testuser")
        by_email = UserCRUD.get_by_username_or_email(db_session, "test@example.com")

        assert by_username is not None
        assert by_email is not None
        assert by_username.id == by_email.id

    def test_update_user(self, db_session):
        user_data = UserCreate(
            username="oldname", email="old@test.com", password="password123"
        )
        user = UserCRUD.create(db_session, user_data)

        update_data = UserUpdate(email="new@test.com")
        updated_user = UserCRUD.update(db_session, user.id, update_data)

        assert updated_user is not None
        assert updated_user.email == "new@test.com"
        assert updated_user.username == "oldname"

    def test_update_user_password(self, db_session):
        user_data = UserCreate(
            username="test", email="test@test.com", password="oldpass123"
        )
        user = UserCRUD.create(db_session, user_data)
        old_hash = user.hashed_password

        update_data = UserUpdate(password="newpass123")
        updated_user = UserCRUD.update(db_session, user.id, update_data)

        assert updated_user.hashed_password != old_hash

    def test_delete_user(self, db_session):
        user_data = UserCreate(
            username="deleteme", email="delete@test.com", password="password123"
        )
        user = UserCRUD.create(db_session, user_data)

        result = UserCRUD.delete(db_session, user.id)

        assert result is True
        assert UserCRUD.get_by_id(db_session, user.id) is None

    def test_delete_nonexistent_user(self, db_session):
        import uuid

        fake_id = uuid.uuid4()

        result = UserCRUD.delete(db_session, fake_id)

        assert result is False

    def test_user_exists_by_username(self, db_session):
        user_data = UserCreate(
            username="existsuser", email="exists@test.com", password="password123"
        )
        UserCRUD.create(db_session, user_data)

        exists = UserCRUD.exists(db_session, username="existsuser")
        not_exists = UserCRUD.exists(db_session, username="nonexistent")

        assert exists is True
        assert not_exists is False

    def test_user_exists_by_email(self, db_session):
        user_data = UserCreate(
            username="emailcheck", email="check@test.com", password="password123"
        )
        UserCRUD.create(db_session, user_data)

        exists = UserCRUD.exists(db_session, email="check@test.com")
        not_exists = UserCRUD.exists(db_session, email="notfound@test.com")

        assert exists is True
        assert not_exists is False

    def test_user_exists_by_both(self, db_session):
        user_data = UserCreate(
            username="bothcheck", email="both@test.com", password="password123"
        )
        UserCRUD.create(db_session, user_data)

        exists = UserCRUD.exists(
            db_session, username="bothcheck", email="both@test.com"
        )

        assert exists is True
