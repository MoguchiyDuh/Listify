import pytest

from app.crud import tag_crud
from app.models import MediaTypeEnum


@pytest.mark.crud
class TestTagCRUD:
    """Tests for tag CRUD operations"""

    def test_slugify(self):
        """Test slug generation"""
        assert tag_crud._slugify("Action") == "action"
        assert tag_crud._slugify("Sci-Fi") == "sci-fi"
        assert tag_crud._slugify("Action/Adventure") == "actionadventure"
        assert tag_crud._slugify("  Spaced Out  ") == "spaced-out"

    def test_get_or_create_new_tag(self, db_session):
        """Test creating a new tag"""
        tag = tag_crud.get_or_create(db_session, name="Action")

        assert tag.id is not None
        assert tag.name == "Action"
        assert tag.slug == "action"

    def test_get_or_create_existing_tag(self, db_session):
        """Test getting an existing tag"""
        # Create first tag
        tag1 = tag_crud.get_or_create(db_session, name="Action")

        # Try to create the same tag again
        tag2 = tag_crud.get_or_create(db_session, name="Action")

        assert tag1.id == tag2.id

    def test_get_or_create_case_insensitive(self, db_session):
        """Test that tag lookup is case-insensitive"""
        tag1 = tag_crud.get_or_create(db_session, name="Action")
        tag2 = tag_crud.get_or_create(db_session, name="action")
        tag3 = tag_crud.get_or_create(db_session, name="ACTION")

        assert tag1.id == tag2.id == tag3.id

    def test_get_by_name(self, db_session):
        """Test getting tag by name"""
        created_tag = tag_crud.get_or_create(db_session, name="Drama")

        found_tag = tag_crud.get_by_name(db_session, name="Drama")

        assert found_tag is not None
        assert found_tag.id == created_tag.id

    def test_get_by_slug(self, db_session):
        """Test getting tag by slug"""
        created_tag = tag_crud.get_or_create(db_session, name="Sci-Fi")

        found_tag = tag_crud.get_by_slug(db_session, slug="sci-fi")

        assert found_tag is not None
        assert found_tag.id == created_tag.id

    def test_add_tags_to_media(self, db_session, sample_movie):
        """Test adding tags to media"""
        tags = tag_crud.add_tags_to_media(
            db_session,
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["Thriller", "Mystery", "Drama"],
        )

        assert len(tags) == 3

        # Verify tags are associated with media
        media_tags = tag_crud.get_tags_for_media(db_session, media_id=sample_movie.id)
        assert len(media_tags) >= 3  # May include tags from fixture

    def test_add_duplicate_tags(self, db_session, sample_movie):
        """Test that duplicate tag names don't create multiple associations"""
        tags = tag_crud.add_tags_to_media(
            db_session,
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["Action", "Action", "Action"],
        )

        # Should only create one association
        media_tags = tag_crud.get_tags_for_media(db_session, media_id=sample_movie.id)
        action_tags = [t for t in media_tags if t.name == "Action"]
        assert len(action_tags) == 1

    def test_add_empty_tags(self, db_session, sample_movie):
        """Test adding empty tag list"""
        tags = tag_crud.add_tags_to_media(
            db_session,
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=[],
        )

        assert len(tags) == 0

    def test_get_tags_for_media(self, db_session, sample_movie):
        """Test getting tags for a media item"""
        # Movie fixture has tags: ["Action", "Sci-Fi"]
        tags = tag_crud.get_tags_for_media(db_session, media_id=sample_movie.id)

        tag_names = {t.name for t in tags}
        assert "Action" in tag_names
        assert "Sci-Fi" in tag_names

    def test_get_media_by_tag(self, db_session, sample_movie, sample_anime):
        """Test getting media by tag"""
        # Both fixtures have "Action" tag
        action_tag = tag_crud.get_by_name(db_session, name="Action")

        media_ids = tag_crud.get_media_by_tag(db_session, tag_id=action_tag.id)

        assert sample_movie.id in media_ids
        assert sample_anime.id in media_ids

    def test_get_media_by_tag_filtered_by_type(
        self, db_session, sample_movie, sample_anime
    ):
        """Test getting media by tag filtered by type"""
        action_tag = tag_crud.get_by_name(db_session, name="Action")

        movie_ids = tag_crud.get_media_by_tag(
            db_session, tag_id=action_tag.id, media_type=MediaTypeEnum.MOVIE
        )

        assert sample_movie.id in movie_ids
        assert sample_anime.id not in movie_ids

    def test_remove_tags_from_media(self, db_session, sample_movie):
        """Test removing specific tags from media"""
        # Get existing tags
        tags = tag_crud.get_tags_for_media(db_session, media_id=sample_movie.id)
        tag_to_remove = tags[0]

        # Remove one tag
        tag_crud.remove_tags_from_media(
            db_session, media_id=sample_movie.id, tag_ids=[tag_to_remove.id]
        )

        # Verify tag was removed
        remaining_tags = tag_crud.get_tags_for_media(
            db_session, media_id=sample_movie.id
        )
        remaining_ids = {t.id for t in remaining_tags}

        assert tag_to_remove.id not in remaining_ids

    def test_remove_all_tags_from_media(self, db_session, sample_movie):
        """Test removing all tags from media"""
        # Remove all tags
        tag_crud.remove_tags_from_media(db_session, media_id=sample_movie.id)

        # Verify all tags were removed
        tags = tag_crud.get_tags_for_media(db_session, media_id=sample_movie.id)
        assert len(tags) == 0

    def test_update_media_tags(self, db_session, sample_movie):
        """Test updating tags for media"""
        # Update with new tags
        new_tags = tag_crud.update_media_tags(
            db_session,
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["Comedy", "Romance"],
        )

        assert len(new_tags) == 2

        # Verify old tags are gone and new tags are present
        tags = tag_crud.get_tags_for_media(db_session, media_id=sample_movie.id)
        tag_names = {t.name for t in tags}

        assert "Comedy" in tag_names
        assert "Romance" in tag_names
        assert "Action" not in tag_names
        assert "Sci-Fi" not in tag_names

    def test_tags_with_special_characters(self, db_session, sample_movie):
        """Test tags with special characters"""
        tags = tag_crud.add_tags_to_media(
            db_session,
            media_id=sample_movie.id,
            media_type=MediaTypeEnum.MOVIE,
            tag_names=["80's Movies", "Action/Adventure", "Post-Apocalyptic"],
        )

        assert len(tags) == 3

        # Verify slugs are properly generated
        slugs = {t.slug for t in tags}
        assert "80s-movies" in slugs
        assert "actionadventure" in slugs
        assert "post-apocalyptic" in slugs
