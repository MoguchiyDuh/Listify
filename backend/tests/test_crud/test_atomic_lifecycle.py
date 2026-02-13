import pytest
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from models import Media, Tracking, MediaTypeEnum, TrackingStatusEnum, User
from crud import media_crud, tracking_crud
from schemas.media import MediaCreate
from schemas.tracking import TrackingCreate

@pytest.mark.asyncio
async def test_atomic_custom_media_deletion(db: AsyncSession, test_user: User):
    """Test that deleting tracking for a custom media also deletes the media."""
    # 1. Create custom media
    movie_in = MediaCreate(
        title="Custom Movie",
        description="A custom movie",
        is_custom=True,
    )
    media = await media_crud.create_movie(db, obj_in=movie_in, user_id=test_user.id)
    
    # 2. Create tracking
    tracking_in = TrackingCreate(
        media_id=media.id,
        media_type=MediaTypeEnum.MOVIE,
        status=TrackingStatusEnum.COMPLETED,
    )
    await tracking_crud.create(db, obj_in=tracking_in, user_id=test_user.id)
    
    # Verify both exist
    assert await media_crud.get_by_id(db, id=media.id) is not None
    assert await tracking_crud.get_by_user_and_media(db, user_id=test_user.id, media_id=media.id) is not None
    
    # 3. Delete tracking
    await tracking_crud.delete(db, user_id=test_user.id, media_id=media.id)
    
    # 4. Verify both are gone
    assert await tracking_crud.get_by_user_and_media(db, user_id=test_user.id, media_id=media.id) is None
    assert await media_crud.get_by_id(db, id=media.id) is None

@pytest.mark.asyncio
async def test_api_media_preservation_on_tracking_deletion(db: AsyncSession, test_user: User):
    """Test that deleting tracking for API media does NOT delete the media."""
    # 1. Create API media (is_custom=False)
    movie_in = MediaCreate(
        title="API Movie",
        description="An API movie",
        is_custom=False,
        external_id="ext_123",
        external_source="tmdb"
    )
    media = await media_crud.create_movie(db, obj_in=movie_in)
    
    # 2. Create tracking
    tracking_in = TrackingCreate(
        media_id=media.id,
        media_type=MediaTypeEnum.MOVIE,
        status=TrackingStatusEnum.PLANNED,
    )
    await tracking_crud.create(db, obj_in=tracking_in, user_id=test_user.id)
    
    # 3. Delete tracking
    await tracking_crud.delete(db, user_id=test_user.id, media_id=media.id)
    
    # 4. Verify tracking is gone but media remains
    assert await tracking_crud.get_by_user_and_media(db, user_id=test_user.id, media_id=media.id) is None
    assert await media_crud.get_by_id(db, id=media.id) is not None

@pytest.mark.asyncio
async def test_file_cleanup_on_media_deletion(db: AsyncSession, test_user: User):
    """Test that deleting a media entry with a local image path deletes the file."""
    # Setup: Create a dummy file in the expected location
    # backend/crud/media.py is at backend/crud/media.py
    # Path(__file__).resolve().parent.parent.parent is project_root/
    
    # We'll use a unique filename to avoid collisions
    filename = "test_cleanup_12345.png"
    
    # Use the same logic as in media.py to find the base path
    import crud.media
    media_file_path = Path(crud.media.__file__).resolve()
    base_path = media_file_path.parent.parent.parent
    
    image_dir = base_path / "static" / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = image_dir / filename
    test_file.write_text("dummy content")
    
    try:
        assert test_file.exists()
        
        cover_url = f"/static/images/{filename}"
        
        # 1. Create custom media with this cover image
        movie_in = MediaCreate(
            title="File Cleanup Movie",
            description="Testing file cleanup",
            is_custom=True,
            cover_image_url=cover_url
        )
        media = await media_crud.create_movie(db, obj_in=movie_in, user_id=test_user.id)
        
        # 2. Delete media
        await media_crud.delete(db, id=media.id, user_id=test_user.id)
        
        # 3. Verify file is gone
        assert not test_file.exists()
        
    finally:
        # Cleanup if something failed
        if test_file.exists():
            test_file.unlink()
