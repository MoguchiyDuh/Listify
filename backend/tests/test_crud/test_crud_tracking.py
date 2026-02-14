from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import AlreadyExists
from crud import media_crud, tracking_crud
from models import MediaTypeEnum, TrackingStatusEnum
from schemas import AnimeCreate, MovieCreate, TrackingCreate, TrackingUpdate


@pytest.mark.crud
class TestTrackingCRUD:
    """Test Tracking CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_tracking(self, test_user, clean_db: AsyncSession):
        """Test creating a tracking entry"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
            rating=8.5,
            progress=0,
        )

        tracking = await tracking_crud.create(
            db=clean_db, obj_in=tracking_data, user_id=test_user.id
        )

        assert tracking.id is not None
        assert tracking.user_id == test_user.id
        assert tracking.media_id == movie.id
        assert tracking.media_type == MediaTypeEnum.MOVIE
        assert tracking.status == TrackingStatusEnum.COMPLETED
        assert tracking.rating == 8.5
        assert tracking.progress == 0
        assert tracking.favorite is False

    @pytest.mark.asyncio
    async def test_create_duplicate_tracking_fails(
        self, test_user, clean_db: AsyncSession
    ):
        """Test creating duplicate tracking entry raises error"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.PLANNED,
        )

        await tracking_crud.create(
            db=clean_db, obj_in=tracking_data, user_id=test_user.id
        )

        with pytest.raises(AlreadyExists):
            await tracking_crud.create(
                db=clean_db, obj_in=tracking_data, user_id=test_user.id
            )

    @pytest.mark.asyncio
    async def test_create_tracking_with_dates(self, test_user, clean_db: AsyncSession):
        """Test creating tracking with dates"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 15),
        )

        tracking = await tracking_crud.create(
            db=clean_db, obj_in=tracking_data, user_id=test_user.id
        )

        assert tracking.start_date == date(2024, 1, 1)
        assert tracking.end_date == date(2024, 1, 15)

    @pytest.mark.asyncio
    async def test_create_tracking_with_notes(self, test_user, clean_db: AsyncSession):
        """Test creating tracking with notes"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
            notes="Great movie! Really enjoyed the plot.",
        )

        tracking = await tracking_crud.create(
            db=clean_db, obj_in=tracking_data, user_id=test_user.id
        )

        assert tracking.notes == "Great movie! Really enjoyed the plot."

    @pytest.mark.asyncio
    async def test_get_tracking_by_user_and_media(
        self, test_user, clean_db: AsyncSession
    ):
        """Test getting tracking by user and media"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking_data = TrackingCreate(
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            status=TrackingStatusEnum.COMPLETED,
        )

        created = await tracking_crud.create(
            db=clean_db, obj_in=tracking_data, user_id=test_user.id
        )

        fetched = await tracking_crud.get_by_user_and_media(
            db=clean_db, user_id=test_user.id, media_id=movie.id
        )

        assert fetched is not None
        assert fetched.id == created.id

    @pytest.mark.asyncio
    async def test_get_by_user(self, test_user, clean_db: AsyncSession):
        """Test getting all tracking entries for user"""
        for i in range(3):
            movie = await media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            tracking_data = TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            )
            await tracking_crud.create(
                db=clean_db, obj_in=tracking_data, user_id=test_user.id
            )

        entries = await tracking_crud.get_by_user(db=clean_db, user_id=test_user.id)

        assert len(entries) == 3

    @pytest.mark.asyncio
    async def test_get_by_user_filtered_by_status(
        self, test_user, clean_db: AsyncSession
    ):
        """Test getting tracking entries filtered by status"""
        statuses = [
            TrackingStatusEnum.PLANNED,
            TrackingStatusEnum.IN_PROGRESS,
            TrackingStatusEnum.COMPLETED,
        ]

        for i, status in enumerate(statuses):
            movie = await media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            tracking_data = TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=status,
            )
            await tracking_crud.create(
                db=clean_db, obj_in=tracking_data, user_id=test_user.id
            )

        completed = await tracking_crud.get_by_user(
            db=clean_db, user_id=test_user.id, status=TrackingStatusEnum.COMPLETED
        )

        assert len(completed) == 1
        assert completed[0].status == TrackingStatusEnum.COMPLETED

    @pytest.mark.asyncio
    async def test_get_by_user_filtered_by_media_type(
        self, test_user, clean_db: AsyncSession
    ):
        """Test getting tracking entries filtered by media type"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie", description="Test")
        )
        anime = await media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Anime", description="Test")
        )

        await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=test_user.id,
        )
        await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=test_user.id,
        )

        movies = await tracking_crud.get_by_user(
            db=clean_db, user_id=test_user.id, media_type=MediaTypeEnum.MOVIE
        )

        assert len(movies) == 1
        assert movies[0].media_type == MediaTypeEnum.MOVIE

    @pytest.mark.asyncio
    async def test_get_by_user_with_pagination(self, test_user, clean_db: AsyncSession):
        """Test pagination"""
        for i in range(5):
            movie = await media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            await tracking_crud.create(
                db=clean_db,
                obj_in=TrackingCreate(
                    media_id=movie.id,
                    media_type=MediaTypeEnum.MOVIE,
                    status=TrackingStatusEnum.PLANNED,
                ),
                user_id=test_user.id,
            )

        page1 = await tracking_crud.get_by_user(
            db=clean_db, user_id=test_user.id, skip=0, limit=2
        )
        assert len(page1) == 2

        page2 = await tracking_crud.get_by_user(
            db=clean_db, user_id=test_user.id, skip=2, limit=2
        )
        assert len(page2) == 2

        page3 = await tracking_crud.get_by_user(
            db=clean_db, user_id=test_user.id, skip=4, limit=2
        )
        assert len(page3) == 1

    @pytest.mark.asyncio
    async def test_get_favorites(self, test_user, clean_db: AsyncSession):
        """Test getting user's favorite media"""
        for i in range(3):
            movie = await media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            await tracking_crud.create(
                db=clean_db,
                obj_in=TrackingCreate(
                    media_id=movie.id,
                    media_type=MediaTypeEnum.MOVIE,
                    status=TrackingStatusEnum.COMPLETED,
                    favorite=(i < 2),
                ),
                user_id=test_user.id,
            )

        favorites = await tracking_crud.get_favorites(db=clean_db, user_id=test_user.id)

        assert len(favorites) == 2
        assert all(f.favorite is True for f in favorites)

    @pytest.mark.asyncio
    async def test_get_favorites_filtered_by_media_type(
        self, test_user, clean_db: AsyncSession
    ):
        """Test getting favorites filtered by media type"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie", description="Test")
        )
        anime = await media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Anime", description="Test")
        )

        await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                favorite=True,
            ),
            user_id=test_user.id,
        )
        await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.COMPLETED,
                favorite=True,
            ),
            user_id=test_user.id,
        )

        movie_favorites = await tracking_crud.get_favorites(
            db=clean_db, user_id=test_user.id, media_type=MediaTypeEnum.MOVIE
        )

        assert len(movie_favorites) == 1
        assert movie_favorites[0].media_type == MediaTypeEnum.MOVIE

    @pytest.mark.asyncio
    async def test_update_tracking_status(self, test_user, clean_db: AsyncSession):
        """Test updating tracking status"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=test_user.id,
        )

        update_data = TrackingUpdate(status=TrackingStatusEnum.COMPLETED)
        updated = await tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.status == TrackingStatusEnum.COMPLETED

    @pytest.mark.asyncio
    async def test_update_tracking_rating(self, test_user, clean_db: AsyncSession):
        """Test updating tracking rating"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                rating=7.0,
            ),
            user_id=test_user.id,
        )

        update_data = TrackingUpdate(rating=9.5)
        updated = await tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.rating == 9.5

    @pytest.mark.asyncio
    async def test_update_tracking_progress(self, test_user, clean_db: AsyncSession):
        """Test updating tracking progress"""
        anime = await media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Test Anime", description="Test")
        )

        tracking = await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.IN_PROGRESS,
                progress=0,
            ),
            user_id=test_user.id,
        )

        update_data = TrackingUpdate(progress=12)
        updated = await tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.progress == 12

    @pytest.mark.asyncio
    async def test_update_tracking_favorite(self, test_user, clean_db: AsyncSession):
        """Test updating favorite status"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                favorite=False,
            ),
            user_id=test_user.id,
        )

        update_data = TrackingUpdate(favorite=True)
        updated = await tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.favorite is True

    @pytest.mark.asyncio
    async def test_update_tracking_notes(self, test_user, clean_db: AsyncSession):
        """Test updating tracking notes"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=test_user.id,
        )

        update_data = TrackingUpdate(notes="Amazing film!")
        updated = await tracking_crud.update(
            db=clean_db, tracking=tracking, obj_in=update_data
        )

        assert updated.notes == "Amazing film!"

    @pytest.mark.asyncio
    async def test_delete_tracking(self, test_user, clean_db: AsyncSession):
        """Test deleting tracking entry"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Test Movie", description="Test")
        )

        tracking = await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=test_user.id,
        )

        result = await tracking_crud.delete(
            db=clean_db, user_id=test_user.id, media_id=movie.id
        )

        assert result is True

        fetched = await tracking_crud.get_by_user_and_media(
            db=clean_db, user_id=test_user.id, media_id=movie.id
        )
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tracking(self, clean_db: AsyncSession):
        """Test deleting non-existent tracking"""
        result = await tracking_crud.delete(db=clean_db, user_id=999, media_id=999)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_statistics(self, test_user, clean_db: AsyncSession):
        """Test getting user statistics"""
        statuses_with_ratings = [
            (TrackingStatusEnum.COMPLETED, 8.0),
            (TrackingStatusEnum.COMPLETED, 9.0),
            (TrackingStatusEnum.IN_PROGRESS, 7.5),
            (TrackingStatusEnum.PLANNED, None),
            (TrackingStatusEnum.DROPPED, 5.0),
        ]

        for i, (status, rating) in enumerate(statuses_with_ratings):
            movie = await media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            await tracking_crud.create(
                db=clean_db,
                obj_in=TrackingCreate(
                    media_id=movie.id,
                    media_type=MediaTypeEnum.MOVIE,
                    status=status,
                    rating=rating,
                    favorite=(i == 0),
                ),
                user_id=test_user.id,
            )

        stats = await tracking_crud.get_statistics(db=clean_db, user_id=test_user.id)

        assert stats["total"] == 5
        assert stats["completed"] == 2
        assert stats["in_progress"] == 1
        assert stats["plan_to_watch"] == 1
        assert stats["dropped"] == 1
        assert stats["on_hold"] == 0
        assert stats["favorites"] == 1
        assert stats["average_rating"] == 7.375

    @pytest.mark.asyncio
    async def test_get_statistics_filtered_by_media_type(
        self, test_user, clean_db: AsyncSession
    ):
        """Test getting statistics filtered by media type"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie", description="Test")
        )
        anime = await media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Anime", description="Test")
        )

        await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=test_user.id,
        )
        await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=anime.id,
                media_type=MediaTypeEnum.ANIME,
                status=TrackingStatusEnum.COMPLETED,
            ),
            user_id=test_user.id,
        )

        movie_stats = await tracking_crud.get_statistics(
            db=clean_db, user_id=test_user.id, media_type=MediaTypeEnum.MOVIE
        )

        assert movie_stats["total"] == 1

    @pytest.mark.asyncio
    async def test_get_statistics_no_ratings(self, test_user, clean_db: AsyncSession):
        """Test statistics with no ratings"""
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie", description="Test")
        )
        await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=test_user.id,
        )

        stats = await tracking_crud.get_statistics(db=clean_db, user_id=test_user.id)

        assert stats["average_rating"] == 0
