import pytest
from httpx import AsyncClient

from crud import media_crud, tracking_crud
from models import MediaTypeEnum, TrackingStatusEnum
from schemas import MovieCreate, TrackingCreate


@pytest.mark.routes
class TestTrackingRoutes:
    """Test tracking routes"""

    async def get_auth_token(self, client: AsyncClient, test_user) -> str:
        """Helper to get auth token"""
        response = await client.post(
            "/api/auth/login",
            json={"username": test_user.username, "password": "testpass123"},
        )
        return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_create_tracking(self, client: AsyncClient, test_user, clean_db):
        """Test creating a tracking entry"""
        token = await self.get_auth_token(client, test_user)

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Test Movie", description="Test"),
        )

        response = await client.post(
            "/api/tracking/",
            json={
                "media_id": movie.id,
                "media_type": "movie",
                "status": "planned",
                "rating": 8.5,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["media_id"] == movie.id
        assert data["status"] == "planned"
        assert data["rating"] is None

    @pytest.mark.asyncio
    async def test_create_duplicate_tracking(
        self, client: AsyncClient, test_user, clean_db
    ):
        """Test creating duplicate tracking fails"""
        token = await self.get_auth_token(client, test_user)

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Test Movie", description="Test"),
        )

        # Create first tracking
        await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
            ),
            user_id=test_user.id,
        )

        # Try to create duplicate
        response = await client.post(
            "/api/tracking/",
            json={
                "media_id": movie.id,
                "media_type": "movie",
                "status": "planned",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_get_user_tracking(self, client: AsyncClient, test_user, clean_db):
        """Test getting all user tracking"""
        token = await self.get_auth_token(client, test_user)

        # Create test tracking entries
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
                    status=TrackingStatusEnum.PLANNED,
                ),
                user_id=test_user.id,
            )

        response = await client.get(
            "/api/tracking/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_get_tracking_filtered_by_status(
        self, client: AsyncClient, test_user, clean_db
    ):
        """Test filtering tracking by status"""
        token = await self.get_auth_token(client, test_user)

        # Create entries with different statuses
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
            await tracking_crud.create(
                db=clean_db,
                obj_in=TrackingCreate(
                    media_id=movie.id,
                    media_type=MediaTypeEnum.MOVIE,
                    status=status,
                ),
                user_id=test_user.id,
            )

        response = await client.get(
            "/api/tracking/?status=completed",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_favorites(self, client: AsyncClient, test_user, clean_db):
        """Test getting user favorites"""
        token = await self.get_auth_token(client, test_user)

        # Create favorite and non-favorite entries
        for i in range(3):
            movie = await media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Movie {i}", description="Test"),
            )
            tracking = await tracking_crud.create(
                db=clean_db,
                obj_in=TrackingCreate(
                    media_id=movie.id,
                    media_type=MediaTypeEnum.MOVIE,
                    status=TrackingStatusEnum.COMPLETED,
                    favorite=(i < 2),  # First 2 are favorites
                ),
                user_id=test_user.id,
            )
        print(await tracking_crud.get_by_user(db=clean_db, user_id=test_user.id))

        response = await client.get(
            "/api/tracking/favorites",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(entry["favorite"] for entry in data)

    @pytest.mark.asyncio
    async def test_get_statistics(self, client: AsyncClient, test_user, clean_db):
        """Test getting tracking statistics"""
        token = await self.get_auth_token(client, test_user)

        # Create tracking with different statuses
        statuses_with_ratings = [
            (TrackingStatusEnum.COMPLETED, 8.0),
            (TrackingStatusEnum.COMPLETED, 9.0),
            (TrackingStatusEnum.IN_PROGRESS, 7.5),
            (TrackingStatusEnum.PLANNED, None),
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
                ),
                user_id=test_user.id,
            )

        response = await client.get(
            "/api/tracking/statistics",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert data["completed"] == 2
        assert data["in_progress"] == 1
        assert data["plan_to_watch"] == 1

    @pytest.mark.asyncio
    async def test_get_tracking_by_media(
        self, client: AsyncClient, test_user, clean_db
    ):
        """Test getting tracking for specific media"""
        token = await self.get_auth_token(client, test_user)

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Test Movie", description="Test"),
        )

        tracking = await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.COMPLETED,
                rating=9.5,
            ),
            user_id=test_user.id,
        )

        response = await client.get(
            f"/api/tracking/{movie.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["media_id"] == movie.id
        assert data["rating"] == 9.5

    @pytest.mark.asyncio
    async def test_update_tracking(self, client: AsyncClient, test_user, clean_db):
        """Test updating tracking entry"""
        token = await self.get_auth_token(client, test_user)

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Test Movie", description="Test"),
        )

        await tracking_crud.create(
            db=clean_db,
            obj_in=TrackingCreate(
                media_id=movie.id,
                media_type=MediaTypeEnum.MOVIE,
                status=TrackingStatusEnum.PLANNED,
                rating=7.0,
            ),
            user_id=test_user.id,
        )

        response = await client.put(
            f"/api/tracking/{movie.id}",
            json={"status": "completed", "rating": 9.5},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["rating"] == 9.5

    @pytest.mark.asyncio
    async def test_delete_tracking(self, client: AsyncClient, test_user, clean_db):
        """Test deleting tracking entry"""
        token = await self.get_auth_token(client, test_user)

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Test Movie", description="Test"),
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

        response = await client.delete(
            f"/api/tracking/{movie.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tracking(self, client: AsyncClient, test_user):
        """Test deleting nonexistent tracking"""
        token = await self.get_auth_token(client, test_user)

        response = await client.delete(
            "/api/tracking/99999",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test accessing tracking without authentication"""
        response = await client.get("/api/tracking/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_tracking_data_integrity(
        self, client: AsyncClient, test_user, clean_db
    ):
        """Test status-based data integrity and auto-dates"""
        token = await self.get_auth_token(client, test_user)

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Integrity Movie", description="Test"),
        )

        # 1. Create as PLANNED - should nullify rating/dates/progress
        response = await client.post(
            "/api/tracking/",
            json={
                "media_id": movie.id,
                "media_type": "movie",
                "status": "planned",
                "rating": 10,
                "progress": 5,
                "priority": "high",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "planned"
        assert data["rating"] is None
        assert data["progress"] == 0
        assert data["priority"] == "high"
        assert data["start_date"] is None

        # 2. Update to IN_PROGRESS - should set start_date, clear priority
        response = await client.patch(
            f"/api/tracking/{movie.id}",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["start_date"] is not None
        assert data["priority"] is None

        # 3. Update to COMPLETED - should set end_date
        response = await client.patch(
            f"/api/tracking/{movie.id}",
            json={"status": "completed", "rating": 9},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["end_date"] is not None
        assert data["rating"] == 9

        # 4. Update back to PLANNED - should nullify everything
        response = await client.patch(
            f"/api/tracking/{movie.id}",
            json={"status": "planned"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "planned"
        assert data["rating"] is None
        assert data["end_date"] is None
        assert data["start_date"] is None

    @pytest.mark.asyncio
    async def test_priority_sorting(self, client: AsyncClient, test_user, clean_db):
        """Test sorting by priority"""
        token = await self.get_auth_token(client, test_user)

        # Create 3 items with different priorities
        priorities = ["low", "high", "mid"]
        for i, p in enumerate(priorities):
            movie = await media_crud.create_movie(
                db=clean_db,
                obj_in=MovieCreate(title=f"Sort Movie {i}", description="Test"),
            )
            await client.post(
                "/api/tracking/",
                json={
                    "media_id": movie.id,
                    "media_type": "movie",
                    "status": "planned",
                    "priority": p,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        # Get sorted by priority
        response = await client.get(
            "/api/tracking/?status=planned&sort_by=priority",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["priority"] == "high"
        assert data[1]["priority"] == "mid"
        assert data[2]["priority"] == "low"
