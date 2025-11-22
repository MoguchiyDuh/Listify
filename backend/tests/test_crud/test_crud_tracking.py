from datetime import date

import pytest
from crud.media import media_crud
from crud.tracking import tracking_crud
from crud.user import user_crud
from models import MediaTypeEnum, TrackingStatusEnum
from schemas.anime import AnimeCreate
from schemas.movie import MovieCreate
from schemas.tracking import TrackingCreate, TrackingUpdate
from sqlalchemy.orm import Session


@pytest.mark.crud
class TestTrackingCRUD:
    """Test Tracking CRUD operations"""

    def test_create_tracking(self, clean_db: Session):
        """Test creating a tracking entry"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.PLANNED,
            rating=8.5,
            progress=0,
        )

        tracking = tracking_crud.create(
            db=clean_db, obj_in=tracking_data, user_id=user.id
        )

        assert tracking.id is not None
        assert tracking.user_id == user.id
        assert tracking.media_id == movie.id
        assert tracking.media_type == MediaTypeEnum.MOVIE
        assert tracking.status == TrackingStatusEnum.PLANNED
        assert tracking.rating == 8.5
        assert tracking.progress == 0
        assert tracking.favorite is False

    def test_create_duplicate_tracking_fails(self, clean_db: Session):
        """Test creating duplicate tracking entry raises error"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.PLANNED,
        )

        tracking_crud.create(db=clean_db, obj_in=tracking_data, user_id=user.id)

        with pytest.raises(ValueError, match="already exists"):
            tracking_crud.create(db=clean_db, obj_in=tracking_data, user_id=user.id)

    def test_create_tracking_with_dates(self, clean_db: Session):
        """Test creating tracking with dates"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 15),
        )

        tracking = tracking_crud.create(
            db=clean_db, obj_in=tracking_data, user_id=user.id
        )

        assert tracking.start_date == date(2024, 1, 1)
        assert tracking.end_date == date(2024, 1, 15)

    def test_create_tracking_with_notes(self, clean_db: Session):
        """Test creating tracking with notes"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
            notes="Great movie! Really enjoyed the plot.",
        )

        tracking = tracking_crud.create(
            db=clean_db, obj_in=tracking_data, user_id=user.id
        )

        assert tracking.notes == "Great movie! Really enjoyed the plot."

    def test_get_tracking_by_user_and_media(self, clean_db: Session):
        """Test getting tracking by user and media"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
        )

        created = tracking_crud.create(
            db=clean_db, obj_in=tracking_data, user_id=user.id
        )

        fetched = tracking_crud.get_by_user_and_media(
            db=clean_db, user_id=user.id, media_id=movie.id
        )

        assert fetched is not None
        assert fetched.id == created.id

    def test_get_by_user(self, clean_db: Session):
        """Test getting all tracking entries for user"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        for i in range(3):
            movie = media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            tracking_data = TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            )
            tracking_crud.create(db=clean_db, obj_in=tracking_data, user_id=user.id)

        entries = tracking_crud.get_by_user(db=clean_db, user_id=user.id)

        assert len(entries) == 3

    def test_get_by_user_filtered_by_status(self, clean_db: Session):
        """Test getting tracking entries filtered by status"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        statuses = [
            TrackingStatusEnum.PLANNED,
            TrackingStatusEnum.IN_PROGRESS,
            TrackingStatusEnum.COMPLETED,
        ]

        for i, status in enumerate(statuses):
            movie = media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            tracking_data = TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=status,
            )
            tracking_crud.create(db=clean_db, obj_in=tracking_data, user_id=user.id)

        completed = tracking_crud.get_by_user(
            db=clean_db, user_id=user.id, status=TrackingStatusEnum.COMPLETED
        )

        assert len(completed) == 1
        assert completed[0].status == TrackingStatusEnum.COMPLETED

    def test_get_by_user_filtered_by_media_type(self, clean_db: Session):
        """Test getting tracking entries filtered by media type"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie", description="Test")
        )
        anime = media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Anime", description="Test")
        )

        tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=user.id,
        )
        tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=user.id,
        )

        movies = tracking_crud.get_by_user(
            db=clean_db, user_id=user.id, media_type=MediaTypeEnum.MOVIE
        )

        assert len(movies) == 1
        assert movies[0].media_type == MediaTypeEnum.MOVIE

    def test_get_by_user_with_pagination(self, clean_db: Session):
        """Test pagination"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        for i in range(5):
            movie = media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            tracking_crud.create(
                db=clean_db,
                obj_in=TrackingCreate(
                    media_id=movie.id,
                    media_type=MediaTypeEnum.MOVIE,
                    status=TrackingStatusEnum.PLANNED,
                ),
                user_id=user.id,
            )

        page1 = tracking_crud.get_by_user(db=clean_db, user_id=user.id, skip=0, limit=2)
        assert len(page1) == 2

        page2 = tracking_crud.get_by_user(db=clean_db, user_id=user.id, skip=2, limit=2)
        assert len(page2) == 2

        page3 = tracking_crud.get_by_user(db=clean_db, user_id=user.id, skip=4, limit=2)
        assert len(page3) == 1

    def test_get_favorites(self, clean_db: Session):
        """Test getting user's favorite media"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        for i in range(3):
            movie = media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            tracking_crud.create(
                db=clean_db,
                obj_in=TrackingCreate(
                    media_id=movie.id,
                    media_type=MediaTypeEnum.MOVIE,
                    status=TrackingStatusEnum.COMPLETED,
                    favorite=(i == 0 or i == 2),
                ),
                user_id=user.id,
            )

        favorites = tracking_crud.get_favorites(db=clean_db, user_id=user.id)

        assert len(favorites) == 2
        assert all(f.favorite is True for f in favorites)

    def test_get_favorites_filtered_by_media_type(self, clean_db: Session):
        """Test getting favorites filtered by media type"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie", description="Test")
        )
        anime = media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Anime", description="Test")
        )

        tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                favorite=True,
            ),
            user_id=user.id,
        )
        tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.COMPLETED,
                favorite=True,
            ),
            user_id=user.id,
        )

        movie_favorites = tracking_crud.get_favorites(
            db=clean_db, user_id=user.id, media_type=MediaTypeEnum.MOVIE
        )

        assert len(movie_favorites) == 1
        assert movie_favorites[0].media_type == MediaTypeEnum.MOVIE

    def test_update_tracking_status(self, clean_db: Session):
        """Test updating tracking status"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=user.id,
        )

        update_data = TrackingUpdate(status=TrackingStatusEnum.COMPLETED)
        updated = tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.status == TrackingStatusEnum.COMPLETED

    def test_update_tracking_rating(self, clean_db: Session):
        """Test updating tracking rating"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                rating=7.0,
            ),
            user_id=user.id,
        )

        update_data = TrackingUpdate(rating=9.5)
        updated = tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.rating == 9.5

    def test_update_tracking_progress(self, clean_db: Session):
        """Test updating tracking progress"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        anime = media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Test Anime", description="Test")
        )

        tracking = tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.IN_PROGRESS,
                progress=0,
            ),
            user_id=user.id,
        )

        update_data = TrackingUpdate(progress=12)
        updated = tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.progress == 12

    def test_update_tracking_favorite(self, clean_db: Session):
        """Test updating favorite status"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                favorite=False,
            ),
            user_id=user.id,
        )

        update_data = TrackingUpdate(favorite=True)
        updated = tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.favorite is True

    def test_update_tracking_notes(self, clean_db: Session):
        """Test updating tracking notes"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=user.id,
        )

        update_data = TrackingUpdate(notes="Amazing film!")
        updated = tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.notes == "Amazing film!"

    def test_delete_tracking(self, clean_db: Session):
        """Test deleting tracking entry"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=user.id,
        )

        result = tracking_crud.delete(db=clean_db, user_id=user.id, media_id=movie.id)

        assert result is True

        fetched = tracking_crud.get_by_user_and_media(
            db=clean_db, user_id=user.id, media_id=movie.id
        )
        assert fetched is None

    def test_delete_nonexistent_tracking(self, clean_db: Session):
        """Test deleting non-existent tracking"""
        result = tracking_crud.delete(db=clean_db, user_id=999, media_id=999)
        assert result is False

    def test_get_statistics(self, clean_db: Session):
        """Test getting user statistics"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        statuses_with_ratings = [
            (TrackingStatusEnum.COMPLETED, 8.0),
            (TrackingStatusEnum.COMPLETED, 9.0),
            (TrackingStatusEnum.IN_PROGRESS, 7.5),
            (TrackingStatusEnum.PLANNED, None),
            (TrackingStatusEnum.DROPPED, 5.0),
        ]

        for i, (status, rating) in enumerate(statuses_with_ratings):
            movie = media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            tracking_crud.create(
                db=clean_db,
                obj_in=TrackingCreate(
                    media_id=movie.id,
                    media_type=MediaTypeEnum.MOVIE,
                    status=status,
                    rating=rating,
                    favorite=(i == 0),
                ),
                user_id=user.id,
            )

        stats = tracking_crud.get_statistics(db=clean_db, user_id=user.id)

        assert stats["total"] == 5
        assert stats["completed"] == 2
        assert stats["in_progress"] == 1
        assert stats["plan_to_watch"] == 1
        assert stats["dropped"] == 1
        assert stats["on_hold"] == 0
        assert stats["favorites"] == 1
        assert stats["average_rating"] == 7.375

    def test_get_statistics_filtered_by_media_type(self, clean_db: Session):
        """Test getting statistics filtered by media type"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie", description="Test")
        )
        anime = media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Anime", description="Test")
        )

        tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=user.id,
        )
        tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=user.id,
        )

        movie_stats = tracking_crud.get_statistics(
            db=clean_db, user_id=user.id, media_type=MediaTypeEnum.MOVIE
        )

        assert movie_stats["total"] == 1

    def test_get_statistics_no_ratings(self, clean_db: Session):
        """Test statistics with no ratings"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie = media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie", description="Test")
        )
        tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=user.id,
        )

        stats = tracking_crud.get_statistics(db=clean_db, user_id=user.id)

        assert stats["average_rating"] == 0
