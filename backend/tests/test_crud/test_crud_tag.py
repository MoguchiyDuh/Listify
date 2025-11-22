import pytest
from crud.media import media_crud
from crud.tag import tag_crud
from models import MediaTypeEnum
from schemas.movie import MovieCreate
from sqlalchemy.orm import Session


@pytest.mark.crud
class TestTagCRUD:
    """Test Tag CRUD operations"""

    def test_create_tag(self, clean_db: Session):
        """Test creating a tag"""
        tag = tag_crud.get_or_create(db=clean_db, name="Action")

        assert tag.id is not None
        assert tag.name == "Action"
        assert tag.slug == "action"

    def test_slugify_tag_name(self, clean_db: Session):
        """Test tag name slugification"""
        tag = tag_crud.get_or_create(db=clean_db, name="Sci-Fi & Fantasy")

        assert tag.slug == "sci-fi-fantasy"

    def test_get_or_create_existing_tag(self, clean_db: Session):
        """Test get_or_create returns existing tag"""
        tag1 = tag_crud.get_or_create(db=clean_db, name="Action")
        tag2 = tag_crud.get_or_create(db=clean_db, name="Action")

        assert tag1.id == tag2.id

    def test_get_or_create_case_insensitive(self, clean_db: Session):
        """Test get_or_create is case-insensitive"""
        tag1 = tag_crud.get_or_create(db=clean_db, name="Action")
        tag2 = tag_crud.get_or_create(db=clean_db, name="action")
        tag3 = tag_crud.get_or_create(db=clean_db, name="ACTION")

        assert tag1.id == tag2.id == tag3.id

    def test_get_tag_by_id(self, clean_db: Session):
        """Test getting tag by ID"""
        tag = tag_crud.get_or_create(db=clean_db, name="Thriller")

        fetched = tag_crud.get(db=clean_db, id=tag.id)

        assert fetched is not None
        assert fetched.id == tag.id
        assert fetched.name == tag.name

    def test_get_tag_by_name(self, clean_db: Session):
        """Test getting tag by name"""
        tag = tag_crud.get_or_create(db=clean_db, name="Horror")

        fetched = tag_crud.get_by_name(db=clean_db, name="Horror")

        assert fetched is not None
        assert fetched.id == tag.id

    def test_get_tag_by_name_case_insensitive(self, clean_db: Session):
        """Test getting tag by name is case-insensitive"""
        tag = tag_crud.get_or_create(db=clean_db, name="Comedy")

        fetched = tag_crud.get_by_name(db=clean_db, name="comedy")

        assert fetched is not None
        assert fetched.id == tag.id

    def test_get_tag_by_slug(self, clean_db: Session):
        """Test getting tag by slug"""
        tag = tag_crud.get_or_create(db=clean_db, name="Science Fiction")

        fetched = tag_crud.get_by_slug(db=clean_db, slug="science-fiction")

        assert fetched is not None
        assert fetched.id == tag.id

    def test_get_nonexistent_tag(self, clean_db: Session):
        """Test getting non-existent tag returns None"""
        fetched = tag_crud.get(db=clean_db, id=999)
        assert fetched is None

        fetched = tag_crud.get_by_name(db=clean_db, name="NonExistent")
        assert fetched is None

        fetched = tag_crud.get_by_slug(db=clean_db, slug="non-existent")
        assert fetched is None

    def test_get_multi_tags(self, clean_db: Session):
        """Test getting multiple tags"""
        tag_crud.get_or_create(db=clean_db, name="Action")
        tag_crud.get_or_create(db=clean_db, name="Comedy")
        tag_crud.get_or_create(db=clean_db, name="Drama")

        tags = tag_crud.get_multi(db=clean_db, skip=0, limit=100)

        assert len(tags) == 3

    def test_add_tags_to_media(self, clean_db: Session):
        """Test adding tags to media"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = tag_crud.add_tags_to_media(
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

    def test_add_duplicate_tags_to_media(self, clean_db: Session):
        """Test adding duplicate tags to media"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["action", "thriller"],
        )

        tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["action", "sci-fi"],
        )

        tags = tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)

        assert len(tags) == 3

    def test_add_empty_tag_list(self, clean_db: Session):
        """Test adding empty tag list"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=[],
        )

        assert len(tags) == 0

    def test_add_tags_with_duplicates_in_list(self, clean_db: Session):
        """Test adding tags with duplicates in the list"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = tag_crud.add_tags_to_media(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["action", "Action", "ACTION", "thriller"],
        )

        # Should deduplicate case-insensitive names
        assert len(tags) == 2

        # Verify only 2 tags were actually created in DB
        all_tags = tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)
        assert len(all_tags) == 2

    def test_add_tags_with_whitespace(self, clean_db: Session):
        """Test adding tags with whitespace"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = tag_crud.add_tags_to_media(
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

    def test_get_tags_for_media(self, clean_db: Session):
        """Test getting all tags for a media item"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller", "sci-fi"],
        )
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tags = tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)

        assert len(tags) == 3
        tag_names = [tag.name for tag in tags]
        assert "action" in tag_names
        assert "thriller" in tag_names
        assert "sci-fi" in tag_names

    def test_get_media_by_tag(self, clean_db: Session):
        """Test getting all media for a tag"""
        tag = tag_crud.get_or_create(db=clean_db, name="Action")

        movie1 = media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 1", description="Test", tags=["action"]),
        )
        movie2 = media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 2", description="Test", tags=["action"]),
        )
        media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 3", description="Test", tags=["comedy"]),
        )

        media_ids = tag_crud.get_media_by_tag(db=clean_db, tag_id=tag.id)

        assert len(media_ids) == 2
        assert movie1.id in media_ids
        assert movie2.id in media_ids

    def test_get_media_by_tag_filtered_by_type(self, clean_db: Session):
        """Test getting media by tag filtered by type"""
        tag = tag_crud.get_or_create(db=clean_db, name="Action")

        movie = media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(
                title="Action Movie", description="Test", tags=["action"]
            ),
        )
        from schemas.anime import AnimeCreate

        media_crud.create_anime(
            db=clean_db,
            obj_in=AnimeCreate(
                title="Action Anime", description="Test", tags=["action"]
            ),
        )

        media_ids = tag_crud.get_media_by_tag(
            db=clean_db, tag_id=tag.id, media_type=MediaTypeEnum.MOVIE
        )

        assert len(media_ids) == 1
        assert movie.id in media_ids

    def test_remove_specific_tags_from_media(self, clean_db: Session):
        """Test removing specific tags from media"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller", "sci-fi"],
        )
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        action_tag = tag_crud.get_by_name(db=clean_db, name="action")
        thriller_tag = tag_crud.get_by_name(db=clean_db, name="thriller")

        tag_crud.remove_tags_from_media(
            db=clean_db, media_id=movie.id, tag_ids=[action_tag.id, thriller_tag.id]
        )

        remaining_tags = tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)

        assert len(remaining_tags) == 1
        assert remaining_tags[0].name == "sci-fi"

    def test_remove_all_tags_from_media(self, clean_db: Session):
        """Test removing all tags from media"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller", "sci-fi"],
        )
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tag_crud.remove_tags_from_media(db=clean_db, media_id=movie.id)

        remaining_tags = tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)

        assert len(remaining_tags) == 0

    def test_update_media_tags(self, clean_db: Session):
        """Test updating media tags"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller"],
        )
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        new_tags = tag_crud.update_media_tags(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["comedy", "drama", "romance"],
        )

        assert len(new_tags) == 3

        all_tags = tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)
        tag_names = [tag.name for tag in all_tags]

        assert "comedy" in tag_names
        assert "drama" in tag_names
        assert "romance" in tag_names
        assert "action" not in tag_names
        assert "thriller" not in tag_names

    def test_update_media_tags_to_empty(self, clean_db: Session):
        """Test clearing all tags from media"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller"],
        )
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        tag_crud.update_media_tags(
            db=clean_db,
            media_id=movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=[],
        )

        all_tags = tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)

        assert len(all_tags) == 0

    def test_delete_tag(self, clean_db: Session):
        """Test deleting a tag"""
        tag = tag_crud.get_or_create(db=clean_db, name="ToDelete")

        result = tag_crud.delete(db=clean_db, id=tag.id)

        assert result is True

        fetched = tag_crud.get(db=clean_db, id=tag.id)
        assert fetched is None

    def test_delete_nonexistent_tag(self, clean_db: Session):
        """Test deleting non-existent tag"""
        result = tag_crud.delete(db=clean_db, id=999)
        assert result is False

    def test_delete_tag_cascades_to_associations(self, clean_db: Session):
        """Test deleting tag removes associations"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test",
            tags=["action", "thriller"],
        )
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        action_tag = tag_crud.get_by_name(db=clean_db, name="action")

        tag_crud.delete(db=clean_db, id=action_tag.id)

        remaining_tags = tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)

        assert len(remaining_tags) == 1
        assert remaining_tags[0].name == "thriller"
