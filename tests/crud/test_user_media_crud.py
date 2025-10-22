import pytest
from app.crud import MediaCRUD, UserCRUD, UserMediaCRUD
from app.models import MediaTypeEnum, PriorityEnum, StatusEnum
from app.schemas import (MovieCreate, SeriesCreate, UserCreate,
                         UserMediaCreate, UserMediaUpdate)


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user_data = UserCreate(
        username="testuser", email="test@example.com", password="password123"
    )
    return UserCRUD.create(db_session, user_data)


@pytest.fixture
def test_movie(db_session):
    """Create a test movie."""
    movie_data = MovieCreate(title="Test Movie", runtime=120)
    return MediaCRUD.create_movie(db_session, movie_data)


@pytest.fixture
def test_series(db_session):
    """Create a test series."""
    series_data = SeriesCreate(title="Test Series", seasons=5)
    return MediaCRUD.create_series(db_session, series_data)


@pytest.mark.crud
class TestUserMediaCRUD:

    def test_create_user_media(self, db_session, test_user, test_movie):
        user_media_data = UserMediaCreate(
            media_id=test_movie.id,
            status=StatusEnum.IN_PROGRESS,
            priority=PriorityEnum.HIGH,
            rating=8,
        )
        user_media = UserMediaCRUD.create(db_session, test_user.id, user_media_data)

        assert user_media.user_id == test_user.id
        assert user_media.media_id == test_movie.id
        assert user_media.status == StatusEnum.IN_PROGRESS
        assert user_media.priority == PriorityEnum.HIGH
        assert user_media.rating == 8

    def test_create_user_media_sets_complete_date(
        self, db_session, test_user, test_movie
    ):
        user_media_data = UserMediaCreate(
            media_id=test_movie.id, status=StatusEnum.COMPLETED
        )
        user_media = UserMediaCRUD.create(db_session, test_user.id, user_media_data)

        assert user_media.complete_date is not None

    def test_get_user_media_by_id(self, db_session, test_user, test_movie):
        user_media_data = UserMediaCreate(
            media_id=test_movie.id, status=StatusEnum.PLANNING
        )
        created = UserMediaCRUD.create(db_session, test_user.id, user_media_data)

        fetched = UserMediaCRUD.get_by_id(db_session, created.id, test_user.id)

        assert fetched is not None
        assert fetched.id == created.id

    def test_get_user_media_by_media_id(self, db_session, test_user, test_movie):
        user_media_data = UserMediaCreate(
            media_id=test_movie.id, status=StatusEnum.PLANNING
        )
        UserMediaCRUD.create(db_session, test_user.id, user_media_data)

        fetched = UserMediaCRUD.get_by_media_id(db_session, test_movie.id, test_user.id)

        assert fetched is not None
        assert fetched.media_id == test_movie.id

    def test_get_user_list(self, db_session, test_user, test_movie, test_series):
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=test_movie.id, status=StatusEnum.IN_PROGRESS),
        )
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=test_series.id, status=StatusEnum.COMPLETED),
        )

        user_list = UserMediaCRUD.get_user_list(db_session, test_user.id)

        assert len(user_list) == 2

    def test_get_user_list_filtered_by_status(
        self, db_session, test_user, test_movie, test_series
    ):
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=test_movie.id, status=StatusEnum.IN_PROGRESS),
        )
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=test_series.id, status=StatusEnum.COMPLETED),
        )

        in_progress = UserMediaCRUD.get_user_list(
            db_session, test_user.id, status=StatusEnum.IN_PROGRESS
        )

        assert len(in_progress) == 1
        assert in_progress[0].status == StatusEnum.IN_PROGRESS

    def test_get_user_list_filtered_by_priority(
        self, db_session, test_user, test_movie, test_series
    ):
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=test_movie.id, priority=PriorityEnum.HIGH),
        )
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=test_series.id, priority=PriorityEnum.LOW),
        )

        high_priority = UserMediaCRUD.get_user_list(
            db_session, test_user.id, priority=PriorityEnum.HIGH
        )

        assert len(high_priority) == 1
        assert high_priority[0].priority == PriorityEnum.HIGH

    def test_get_user_list_filtered_by_favorite(
        self, db_session, test_user, test_movie, test_series
    ):
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=test_movie.id, is_favorite=True),
        )
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=test_series.id, is_favorite=False),
        )

        favorites = UserMediaCRUD.get_user_list(
            db_session, test_user.id, is_favorite=True
        )

        assert len(favorites) == 1
        assert favorites[0].is_favorite is True

    def test_update_user_media(self, db_session, test_user, test_movie):
        user_media_data = UserMediaCreate(media_id=test_movie.id, rating=7)
        user_media = UserMediaCRUD.create(db_session, test_user.id, user_media_data)

        update_data = UserMediaUpdate(rating=9, note="Amazing movie!")
        updated = UserMediaCRUD.update(
            db_session, user_media.id, test_user.id, update_data
        )

        assert updated.rating == 9
        assert updated.note == "Amazing movie!"

    def test_update_status_to_completed_sets_date(
        self, db_session, test_user, test_movie
    ):
        user_media_data = UserMediaCreate(
            media_id=test_movie.id, status=StatusEnum.IN_PROGRESS
        )
        user_media = UserMediaCRUD.create(db_session, test_user.id, user_media_data)

        update_data = UserMediaUpdate(status=StatusEnum.COMPLETED)
        updated = UserMediaCRUD.update(
            db_session, user_media.id, test_user.id, update_data
        )

        assert updated.status == StatusEnum.COMPLETED
        assert updated.complete_date is not None

    def test_update_status_from_completed_clears_date(
        self, db_session, test_user, test_movie
    ):
        user_media_data = UserMediaCreate(
            media_id=test_movie.id, status=StatusEnum.COMPLETED
        )
        user_media = UserMediaCRUD.create(db_session, test_user.id, user_media_data)

        update_data = UserMediaUpdate(status=StatusEnum.IN_PROGRESS)
        updated = UserMediaCRUD.update(
            db_session, user_media.id, test_user.id, update_data
        )

        assert updated.status == StatusEnum.IN_PROGRESS
        assert updated.complete_date is None

    def test_delete_user_media(self, db_session, test_user, test_movie):
        user_media_data = UserMediaCreate(media_id=test_movie.id)
        user_media = UserMediaCRUD.create(db_session, test_user.id, user_media_data)

        result = UserMediaCRUD.delete(db_session, user_media.id, test_user.id)

        assert result is True
        assert UserMediaCRUD.get_by_id(db_session, user_media.id, test_user.id) is None

    def test_user_media_exists(self, db_session, test_user, test_movie):
        user_media_data = UserMediaCreate(media_id=test_movie.id)
        UserMediaCRUD.create(db_session, test_user.id, user_media_data)

        exists = UserMediaCRUD.exists(db_session, test_user.id, test_movie.id)
        not_exists = UserMediaCRUD.exists(db_session, test_user.id, 99999)

        assert exists is True
        assert not_exists is False

    def test_get_statistics(self, db_session, test_user):
        movie1 = MediaCRUD.create_movie(db_session, MovieCreate(title="M1", runtime=90))
        movie2 = MediaCRUD.create_movie(
            db_session, MovieCreate(title="M2", runtime=100)
        )
        movie3 = MediaCRUD.create_movie(
            db_session, MovieCreate(title="M3", runtime=110)
        )

        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(
                media_id=movie1.id, status=StatusEnum.COMPLETED, is_favorite=True
            ),
        )
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=movie2.id, status=StatusEnum.IN_PROGRESS),
        )
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=movie3.id, status=StatusEnum.PLANNING),
        )

        stats = UserMediaCRUD.get_statistics(db_session, test_user.id)

        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["in_progress"] == 1
        assert stats["planning"] == 1
        assert stats["favorites"] == 1

    def test_get_by_priority_sorted(self, db_session, test_user):
        movie1 = MediaCRUD.create_movie(db_session, MovieCreate(title="M1", runtime=90))
        movie2 = MediaCRUD.create_movie(
            db_session, MovieCreate(title="M2", runtime=100)
        )
        movie3 = MediaCRUD.create_movie(
            db_session, MovieCreate(title="M3", runtime=110)
        )

        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=movie1.id, priority=PriorityEnum.LOW),
        )
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=movie2.id, priority=PriorityEnum.HIGH),
        )
        UserMediaCRUD.create(
            db_session,
            test_user.id,
            UserMediaCreate(media_id=movie3.id, priority=PriorityEnum.MEDIUM),
        )

        sorted_list = UserMediaCRUD.get_by_priority_sorted(db_session, test_user.id)

        assert sorted_list[0].priority == PriorityEnum.HIGH
        assert sorted_list[1].priority == PriorityEnum.MEDIUM
        assert sorted_list[2].priority == PriorityEnum.LOW

    def test_user_isolation(self, db_session, test_movie):
        user1 = UserCRUD.create(
            db_session,
            UserCreate(username="user1", email="u1@test.com", password="password123"),
        )
        user2 = UserCRUD.create(
            db_session,
            UserCreate(username="user2", email="u2@test.com", password="password123"),
        )

        UserMediaCRUD.create(
            db_session, user1.id, UserMediaCreate(media_id=test_movie.id)
        )

        user1_list = UserMediaCRUD.get_user_list(db_session, user1.id)
        user2_list = UserMediaCRUD.get_user_list(db_session, user2.id)

        assert len(user1_list) == 1
        assert len(user2_list) == 0
