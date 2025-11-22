import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from crud import media_crud, tag_crud
from models import MediaTypeEnum
from schemas import MovieCreate


@pytest.mark.crud
class TestTagCRUD:
    """Test Tag CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_tag(self, clean_db: AsyncSession):
        """Test creating a tag"""
        tag = await tag_crud.get_or_create(db=clean_db, name="Action")

        assert tag.id is not None
        assert tag.name == "Action"
        assert tag.slug == "action"

    @pytest.mark.asyncio
    async def test_slugify_tag_name(self, clean_db: AsyncSession):
        """Test tag name slugification"""
        tag = await tag_crud.get_or_create(db=clean_db, name="Sci-Fi & Fantasy")

        assert tag.slug == "sci-fi-fantasy"

    @pytest.mark.asyncio
    async def test_get_or_create_existing_tag(self, clean_db: AsyncSession):
        """Test get_or_create returns existing tag"""
        tag1 = await tag_crud.get_or_create(db=clean_db, name="Action")
        tag2 = await tag_crud.get_or_create(db=clean_db, name="Action")

        assert tag1.id == tag2.id

    @pytest.mark.asyncio
    async def test_get_or_create_case_insensitive(self, clean_db: AsyncSession):
        """Test get_or_create is case-insensitive"""
        tag1 = await tag_crud.get_or_create(db=clean_db, name="Action")
        tag2 = await tag_crud.get_or_create(db=clean_db, name="action")
        tag3 = await tag_crud.get_or_create(db=clean_db, name="ACTION")

        assert tag1.id == tag2.id == tag3.id

    @pytest.mark.asyncio
    async def test_get_tag_by_id(self, clean_db: AsyncSession):
        """Test getting tag by ID"""
        tag = await tag_crud.get_or_create(db=clean_db, name="Thriller")

        fetched = await tag_crud.get(db=clean_db, id=tag.id)

        assert fetched is not None
        assert fetched.id == tag.id
        assert fetched.name == tag.name

    @pytest.mark.asyncio
    async def test_get_tag_by_name(self, clean_db: AsyncSession):
        """Test getting tag by name"""
        tag = await tag_crud.get_or_create(db=clean_db, name="Horror")

        fetched = await tag_crud.get_by_name(db=clean_db, name="Horror")

        assert fetched is not None
        assert fetched.id == tag.id

    @pytest.mark.asyncio
    async def test_get_tag_by_name_case_insensitive(self, clean_db: AsyncSession):
        """Test getting tag by name is case-insensitive"""
        tag = await tag_crud.get_or_create(db=clean_db, name="Comedy")

        fetched = await tag_crud.get_by_name(db=clean_db, name="comedy")

        assert fetched is not None
        assert fetched.id == tag.id

    @pytest.mark.asyncio
    async def test_get_tag_by_slug(self, clean_db: AsyncSession):
        """Test getting tag by slug"""
        tag = await tag_crud.get_or_create(db=clean_db, name="Science Fiction")

        fetched = await tag_crud.get_by_slug(db=clean_db, slug="science-fiction")

        assert fetched is not None
        assert fetched.id == tag.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_tag(self, clean_db: AsyncSession):
        """Test getting non-existent tag returns None"""
        fetched = await tag_crud.get(db=clean_db, id=999)
        assert fetched is None

        fetched = await tag_crud.get_by_name(db=clean_db, name="NonExistent")
        assert fetched is None

        fetched = await tag_crud.get_by_slug(db=clean_db, slug="non-existent")
        assert fetched is None

    @pytest.mark.asyncio
    async def test_get_multi_tags(self, clean_db: AsyncSession):
        """Test getting multiple tags"""
        await tag_crud.get_or_create(db=clean_db, name="Action")
        await tag_crud.get_or_create(db=clean_db, name="Comedy")
        await tag_crud.get_or_create(db=clean_db, name="Drama")

        tags = await tag_crud.get_multi(db=clean_db, skip=0, limit=100)

        assert len(tags) == 3

    @pytest.mark.asyncio
    async def test_add_tags_to_media(self, clean_db: AsyncSession):
        """Test adding tags to media"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = await tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["action", "thriller", "sci-fi"],
        )

        assert len(tags) == 3
        tag_names = [tag.name for tag in tags]
        assert "action" in tag_names
        assert "thriller" in tag_names
        assert "sci-fi" in tag_names

    @pytest.mark.asyncio
    async def test_add_duplicate_tags_to_media(self, clean_db: AsyncSession):
        """Test adding duplicate tags to media"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        await tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["action", "thriller"],
        )

        await tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["action", "sci-fi"],
        )

        tags = await tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)

        assert len(tags) == 3

    @pytest.mark.asyncio
    async def test_add_empty_tag_list(self, clean_db: AsyncSession):
        """Test adding empty tag list"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = await tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=[],
        )

        assert len(tags) == 0

    @pytest.mark.asyncio
    async def test_add_tags_with_duplicates_in_list(self, clean_db: AsyncSession):
        """Test adding tags with duplicates in the list"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = await tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["action", "Action", "ACTION", "thriller"],
        )

        # Should deduplicate case-insensitive names
        assert len(tags) == 2

        # Verify only 2 tags were actually created in DB
        all_tags = await tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)
        assert len(all_tags) == 2

    @pytest.mark.asyncio
    async def test_add_tags_with_whitespace(self, clean_db: AsyncSession):
        """Test adding tags with whitespace"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = await tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["  action  ", " thriller", "sci-fi ", "  "],
        )

        assert len(tags) == 3
        tag_names = [tag.name for tag in tags]
        assert "action" in tag_names
        assert "thriller" in tag_names
        assert "sci-fi" in tag_names

    @pytest.mark.asyncio
    async def test_get_tags_for_media(self, clean_db: AsyncSession):
        """Test getting all tags for a media item"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller", "sci-fi"],
        )
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = await tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)

        assert len(tags) == 3
        tag_names = [tag.name for tag in tags]
        assert "action" in tag_names
        assert "thriller" in tag_names
        assert "sci-fi" in tag_names

    @pytest.mark.asyncio
    async def test_get_media_by_tag(self, clean_db: AsyncSession):
        """Test getting all media for a tag"""
        tag = await tag_crud.get_or_create(db=clean_db, name="Action")

        movie1 = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 1", description="Test", tags=["action"]),
        )
        movie2 = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 2", description="Test", tags=["action"]),
        )
        await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 3", description="Test", tags=["comedy"]),
        )

        media_ids = await tag_crud.get_media_by_tag(db=clean_db, tag_id=tag.id)

        assert len(media_ids) == 2
        assert movie1.id in media_ids
        assert movie2.id in media_ids

    @pytest.mark.asyncio
    async def test_get_media_by_tag_filtered_by_type(self, clean_db: AsyncSession):
        """Test getting media by tag filtered by type"""
        tag = await tag_crud.get_or_create(db=clean_db, name="Action")

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(
                title="Action Movie", description="Test", tags=["action"]
            ),
        )
        from schemas.anime import AnimeCreate

        await media_crud.create_anime(
            db=clean_db,
            obj_in=AnimeCreate(
                title="Action Anime", description="Test", tags=["action"]
            ),
        )

        media_ids = await tag_crud.get_media_by_tag(
            db=clean_db, tag_id=tag.id, media_type=MediaTypeEnum.MOVIE
        )

        assert len(media_ids) == 1
        assert movie.id in media_ids

    @pytest.mark.asyncio
    async def test_remove_specific_tags_from_media(self, clean_db: AsyncSession):
        """Test removing specific tags from media"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller", "sci-fi"],
        )
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        action_tag = await tag_crud.get_by_name(db=clean_db, name="action")
        thriller_tag = await tag_crud.get_by_name(db=clean_db, name="thriller")

        await tag_crud.remove_tags_from_media(
            db=clean_db, media_id=movie.id, tag_ids=[action_tag.id, thriller_tag.id]
        )

        remaining_tags = await tag_crud.get_tags_for_media(
            db=clean_db, media_id=movie.id
        )

        assert len(remaining_tags) == 1
        assert remaining_tags[0].name == "sci-fi"

    @pytest.mark.asyncio
    async def test_remove_all_tags_from_media(self, clean_db: AsyncSession):
        """Test removing all tags from media"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller", "sci-fi"],
        )
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        await tag_crud.remove_tags_from_media(db=clean_db, media_id=movie.id)

        remaining_tags = await tag_crud.get_tags_for_media(
            db=clean_db, media_id=movie.id
        )

        assert len(remaining_tags) == 0

    @pytest.mark.asyncio
    async def test_update_media_tags(self, clean_db: AsyncSession):
        """Test updating media tags"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller"],
        )
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        new_tags = await tag_crud.update_media_tags(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["comedy", "drama", "romance"],
        )

        assert len(new_tags) == 3

        all_tags = await tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)
        tag_names = [tag.name for tag in all_tags]

        assert "comedy" in tag_names
        assert "drama" in tag_names
        assert "romance" in tag_names
        assert "action" not in tag_names
        assert "thriller" not in tag_names

    @pytest.mark.asyncio
    async def test_update_media_tags_to_empty(self, clean_db: AsyncSession):
        """Test clearing all tags from media"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller"],
        )
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        await tag_crud.update_media_tags(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=[],
        )

        all_tags = await tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)

        assert len(all_tags) == 0

    @pytest.mark.asyncio
    async def test_delete_tag(self, clean_db: AsyncSession):
        """Test deleting a tag"""
        tag = await tag_crud.get_or_create(db=clean_db, name="ToDelete")

        result = await tag_crud.delete(db=clean_db, id=tag.id)

        assert result is True

        fetched = await tag_crud.get(db=clean_db, id=tag.id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tag(self, clean_db: AsyncSession):
        """Test deleting non-existent tag"""
        result = await tag_crud.delete(db=clean_db, id=999)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_tag_cascades_to_associations(self, clean_db: AsyncSession):
        """Test deleting tag removes associations"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller"],
        )
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        action_tag = await tag_crud.get_by_name(db=clean_db, name="action")

        await tag_crud.delete(db=clean_db, id=action_tag.id)

        remaining_tags = await tag_crud.get_tags_for_media(
            db=clean_db, media_id=movie.id
        )

        assert len(remaining_tags) == 1
        assert remaining_tags[0].name == "thriller"
