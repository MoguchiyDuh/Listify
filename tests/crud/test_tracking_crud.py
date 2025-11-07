from datetime import date

import pytest

from app.crud import tracking_crud
from app.models import MediaTypeEnum, TrackingStatusEnum
from app.schemas.tracking import TrackingCreate, TrackingUpdate


@pytest.mark.crud
class TestTrackingCRUD:
    """Tests for tracking CRUD operations"""

    def test_create_tracking(self, db_session, sample_user, sample_movie):
        """Test creating a tracking entry"""
        tracking_data = TrackingCreate(
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.IN_PROGRESS,
            rating=8.5,
            progress=0,
            favorite=False,
        )

        tracking = tracking_crud.create(
            db_session, obj_in=tracking_data, user_id=sample_user.id
        )

        assert tracking.id is not None
        assert tracking.user_id == sample_user.id
        assert tracking.media_id == sample_movie.id
        assert tracking.status == TrackingStatusEnum.IN_PROGRESS
        assert tracking.rating == 8.5

    def test_create_duplicate_tracking(self, db_session, sample_user, sample_movie):
        """Test that duplicate tracking entries raise an error"""
        tracking_data = TrackingCreate(
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
        )

        # Create first tracking
        tracking_crud.create(db_session, obj_in=tracking_data, user_id=sample_user.id)

        # Try to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            tracking_crud.create(
                db_session, obj_in=tracking_data, user_id=sample_user.id
            )

    def test_get_by_user_and_media(self, db_session, sample_user, sample_movie):
        """Test getting tracking by user and media"""
        # Create tracking
        tracking_data = TrackingCreate(
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
        )
        created = tracking_crud.create(
            db_session, obj_in=tracking_data, user_id=sample_user.id
        )

        # Get tracking
        tracking = tracking_crud.get_by_user_and_media(
            db_session, user_id=sample_user.id, media_id=sample_movie.id
        )

        assert tracking is not None
        assert tracking.id == created.id

    def test_get_by_user(self, db_session, sample_user, sample_movie, sample_anime):
        """Test getting all tracking entries for a user"""
        # Create multiple tracking entries
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=sample_user.id,
        )
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.IN_PROGRESS,
            ),
            user_id=sample_user.id,
        )

        # Get all tracking
        tracking_list = tracking_crud.get_by_user(db_session, user_id=sample_user.id)

        assert len(tracking_list) == 2

    def test_get_by_user_filtered_by_status(
        self, db_session, sample_user, sample_movie, sample_anime
    ):
        """Test getting tracking filtered by status"""
        # Create tracking with different statuses
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=sample_user.id,
        )
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.IN_PROGRESS,
            ),
            user_id=sample_user.id,
        )

        # Get only completed
        completed = tracking_crud.get_by_user(
            db_session, user_id=sample_user.id, status=TrackingStatusEnum.COMPLETED
        )

        assert len(completed) == 1
        assert completed[0].status == TrackingStatusEnum.COMPLETED

    def test_get_by_user_filtered_by_media_type(
        self, db_session, sample_user, sample_movie, sample_anime
    ):
        """Test getting tracking filtered by media type"""
        # Create tracking for different media types
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=sample_user.id,
        )
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.IN_PROGRESS,
            ),
            user_id=sample_user.id,
        )

        # Get only anime
        anime_tracking = tracking_crud.get_by_user(
            db_session, user_id=sample_user.id, media_type=MediaTypeEnum.ANIME
        )

        assert len(anime_tracking) == 1
        assert anime_tracking[0].media_type == MediaTypeEnum.ANIME

    def test_get_favorites(
        self, db_session, sample_user, sample_movie, sample_anime, sample_game
    ):
        """Test getting favorite media"""
        # Create tracking with favorites
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                favorite=True,
            ),
            user_id=sample_user.id,
        )
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.COMPLETED,
                favorite=False,
            ),
            user_id=sample_user.id,
        )
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_game.id,
                media_type=MediaTypeEnum.GAME,
                status=TrackingStatusEnum.COMPLETED,
                favorite=True,
            ),
            user_id=sample_user.id,
        )

        # Get favorites
        favorites = tracking_crud.get_favorites(db_session, user_id=sample_user.id)

        assert len(favorites) == 2
        assert all(t.favorite is True for t in favorites)

    def test_update_tracking(self, db_session, sample_user, sample_movie):
        """Test updating a tracking entry"""
        # Create tracking
        tracking = tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.IN_PROGRESS,
                progress=50,
            ),
            user_id=sample_user.id,
        )

        # Update tracking
        update_data = TrackingUpdate(
            status=TrackingStatusEnum.COMPLETED,
            progress=100,
            rating=9.0,
            end_date=date.today(),
        )

        updated = tracking_crud.update(
            db_session, tracking=tracking, obj_in=update_data
        )

        assert updated.status == TrackingStatusEnum.COMPLETED
        assert updated.progress == 100
        assert updated.rating == 9.0
        assert updated.end_date == date.today()

    def test_delete_tracking(self, db_session, sample_user, sample_movie):
        """Test deleting a tracking entry"""
        # Create tracking
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=sample_user.id,
        )

        # Delete tracking
        result = tracking_crud.delete(
            db_session, user_id=sample_user.id, media_id=sample_movie.id
        )

        assert result is True

        # Verify tracking is deleted
        tracking = tracking_crud.get_by_user_and_media(
            db_session, user_id=sample_user.id, media_id=sample_movie.id
        )
        assert tracking is None

    def test_delete_nonexistent_tracking(self, db_session, sample_user):
        """Test deleting non-existent tracking"""
        result = tracking_crud.delete(
            db_session, user_id=sample_user.id, media_id=99999
        )

        assert result is False

    def test_get_statistics(
        self, db_session, sample_user, sample_movie, sample_anime, sample_game
    ):
        """Test getting user statistics"""
        # Create various tracking entries
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                rating=8.5,
                favorite=True,
            ),
            user_id=sample_user.id,
        )
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.IN_PROGRESS,
                rating=7.0,
            ),
            user_id=sample_user.id,
        )
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_game.id,
                media_type=MediaTypeEnum.GAME,
                status=TrackingStatusEnum.DROPPED,
                rating=5.0,
            ),
            user_id=sample_user.id,
        )

        # Get statistics
        stats = tracking_crud.get_statistics(db_session, user_id=sample_user.id)

        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["in_progress"] == 1
        assert stats["dropped"] == 1
        assert stats["favorites"] == 1
        assert stats["average_rating"] == pytest.approx((8.5 + 7.0 + 5.0) / 3)

    def test_get_statistics_filtered_by_type(
        self, db_session, sample_user, sample_movie, sample_anime
    ):
        """Test getting statistics filtered by media type"""
        # Create tracking for different types
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                rating=9.0,
            ),
            user_id=sample_user.id,
        )
        tracking_crud.create(
            db_session,
            obj_in=TrackingCreate(
                media_id=sample_anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.IN_PROGRESS,
                rating=7.0,
            ),
            user_id=sample_user.id,
        )

        # Get movie statistics only
        movie_stats = tracking_crud.get_statistics(
            db_session, user_id=sample_user.id, media_type=MediaTypeEnum.MOVIE
        )

        assert movie_stats["total"] == 1
        assert movie_stats["completed"] == 1
        assert movie_stats["average_rating"] == 9.0

    def test_tracking_with_dates(self, db_session, sample_user, sample_movie):
        """Test tracking with start and end dates"""
        tracking_data = TrackingCreate(
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 15),
        )

        tracking = tracking_crud.create(
            db_session, obj_in=tracking_data, user_id=sample_user.id
        )

        assert tracking.start_date == date(2024, 1, 1)
        assert tracking.end_date == date(2024, 1, 15)

    def test_tracking_with_notes(self, db_session, sample_user, sample_movie):
        """Test tracking with notes"""
        tracking_data = TrackingCreate(
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
            notes="Great movie! Loved the plot twist.",
        )

        tracking = tracking_crud.create(
            db_session, obj_in=tracking_data, user_id=sample_user.id
        )

        assert tracking.notes == "Great movie! Loved the plot twist."
