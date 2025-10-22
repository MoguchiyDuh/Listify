import pytest
from app.crud import MediaCRUD, MediaTagCRUD, TagCRUD
from app.models import MediaTypeEnum
from app.schemas import MediaTagCreate, MovieCreate, TagCreate, TagUpdate


@pytest.mark.crud
class TestTagCRUD:

    def test_create_tag(self, db_session):
        tag_data = TagCreate(name="Action")
        tag = TagCRUD.create(db_session, tag_data)

        assert tag.name == "Action"
        assert tag.slug == "action"
        assert tag.id is not None

    def test_create_tag_with_special_characters(self, db_session):
        tag_data = TagCreate(name="Sci-Fi & Fantasy")
        tag = TagCRUD.create(db_session, tag_data)

        assert tag.name == "Sci-Fi & Fantasy"
        assert tag.slug == "sci-fi-fantasy"

    def test_create_duplicate_slug_generates_unique(self, db_session):
        TagCRUD.create(db_session, TagCreate(name="Action"))
        duplicate = TagCRUD.create(db_session, TagCreate(name="Action"))

        assert duplicate.slug == "action-1"

    def test_get_tag_by_id(self, db_session):
        tag = TagCRUD.create(db_session, TagCreate(name="Drama"))

        fetched_tag = TagCRUD.get_by_id(db_session, tag.id)

        assert fetched_tag is not None
        assert fetched_tag.name == "Drama"

    def test_get_tag_by_slug(self, db_session):
        TagCRUD.create(db_session, TagCreate(name="Comedy"))

        fetched_tag = TagCRUD.get_by_slug(db_session, "comedy")

        assert fetched_tag is not None
        assert fetched_tag.name == "Comedy"

    def test_get_tag_by_name(self, db_session):
        TagCRUD.create(db_session, TagCreate(name="Horror"))

        fetched_tag = TagCRUD.get_by_name(db_session, "Horror")

        assert fetched_tag is not None
        assert fetched_tag.slug == "horror"

    def test_get_all_tags(self, db_session):
        TagCRUD.create(db_session, TagCreate(name="Tag1"))
        TagCRUD.create(db_session, TagCreate(name="Tag2"))
        TagCRUD.create(db_session, TagCreate(name="Tag3"))

        tags = TagCRUD.get_all(db_session)

        assert len(tags) == 3

    def test_search_tags(self, db_session):
        TagCRUD.create(db_session, TagCreate(name="Science Fiction"))
        TagCRUD.create(db_session, TagCreate(name="Historical Fiction"))
        TagCRUD.create(db_session, TagCreate(name="Drama"))

        results = TagCRUD.search(db_session, "Fiction")

        assert len(results) == 2

    def test_update_tag(self, db_session):
        tag = TagCRUD.create(db_session, TagCreate(name="Old Name"))

        update_data = TagUpdate(name="New Name")
        updated_tag = TagCRUD.update(db_session, tag.id, update_data)

        assert updated_tag.name == "New Name"
        assert updated_tag.slug == "new-name"

    def test_delete_tag(self, db_session):
        tag = TagCRUD.create(db_session, TagCreate(name="Delete Me"))

        result = TagCRUD.delete(db_session, tag.id)

        assert result is True
        assert TagCRUD.get_by_id(db_session, tag.id) is None

    def test_get_or_create_existing(self, db_session):
        original = TagCRUD.create(db_session, TagCreate(name="Existing"))

        fetched = TagCRUD.get_or_create(db_session, "Existing")

        assert fetched.id == original.id

    def test_get_or_create_new(self, db_session):
        tag = TagCRUD.get_or_create(db_session, "New Tag")

        assert tag.name == "New Tag"
        assert tag.slug == "new-tag"


@pytest.mark.crud
class TestMediaTagCRUD:

    def test_create_media_tag_association(self, db_session):
        movie = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Test", runtime=90)
        )
        tag = TagCRUD.create(db_session, TagCreate(name="Action"))

        media_tag_data = MediaTagCreate(media_id=movie.id, tag_id=tag.id)
        media_tag = MediaTagCRUD.create(db_session, media_tag_data, MediaTypeEnum.MOVIE)

        assert media_tag.media_id == movie.id
        assert media_tag.tag_id == tag.id
        assert media_tag.media_type == MediaTypeEnum.MOVIE

    def test_get_tags_for_media(self, db_session):
        movie = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Test", runtime=90)
        )
        tag1 = TagCRUD.create(db_session, TagCreate(name="Action"))
        tag2 = TagCRUD.create(db_session, TagCreate(name="Thriller"))

        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=movie.id, tag_id=tag1.id),
            MediaTypeEnum.MOVIE,
        )
        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=movie.id, tag_id=tag2.id),
            MediaTypeEnum.MOVIE,
        )

        tags = MediaTagCRUD.get_tags_for_media(db_session, movie.id)

        assert len(tags) == 2
        assert {t.name for t in tags} == {"Action", "Thriller"}

    def test_get_media_by_tag(self, db_session):
        movie1 = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Movie1", runtime=90)
        )
        movie2 = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Movie2", runtime=100)
        )
        tag = TagCRUD.create(db_session, TagCreate(name="Action"))

        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=movie1.id, tag_id=tag.id),
            MediaTypeEnum.MOVIE,
        )
        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=movie2.id, tag_id=tag.id),
            MediaTypeEnum.MOVIE,
        )

        media_ids = MediaTagCRUD.get_media_by_tag(db_session, tag.id)

        assert len(media_ids) == 2
        assert movie1.id in media_ids
        assert movie2.id in media_ids

    def test_get_media_by_tag_filtered_by_type(self, db_session):
        from app.schemas import SeriesCreate

        movie = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Movie", runtime=90)
        )
        series = MediaCRUD.create_series(
            db_session, SeriesCreate(title="Series", seasons=3)
        )
        tag = TagCRUD.create(db_session, TagCreate(name="Drama"))

        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=movie.id, tag_id=tag.id),
            MediaTypeEnum.MOVIE,
        )
        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=series.id, tag_id=tag.id),
            MediaTypeEnum.SERIES,
        )

        movie_ids = MediaTagCRUD.get_media_by_tag(
            db_session, tag.id, MediaTypeEnum.MOVIE
        )

        assert len(movie_ids) == 1
        assert movie.id in movie_ids
        assert series.id not in movie_ids

    def test_delete_media_tag_association(self, db_session):
        movie = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Test", runtime=90)
        )
        tag = TagCRUD.create(db_session, TagCreate(name="Action"))
        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=movie.id, tag_id=tag.id),
            MediaTypeEnum.MOVIE,
        )

        result = MediaTagCRUD.delete(db_session, movie.id, tag.id)

        assert result is True
        assert len(MediaTagCRUD.get_tags_for_media(db_session, movie.id)) == 0

    def test_delete_all_tags_for_media(self, db_session):
        movie = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Test", runtime=90)
        )
        tag1 = TagCRUD.create(db_session, TagCreate(name="Tag1"))
        tag2 = TagCRUD.create(db_session, TagCreate(name="Tag2"))

        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=movie.id, tag_id=tag1.id),
            MediaTypeEnum.MOVIE,
        )
        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=movie.id, tag_id=tag2.id),
            MediaTypeEnum.MOVIE,
        )

        count = MediaTagCRUD.delete_all_for_media(db_session, movie.id)

        assert count == 2
        assert len(MediaTagCRUD.get_tags_for_media(db_session, movie.id)) == 0

    def test_media_tag_exists(self, db_session):
        movie = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Test", runtime=90)
        )
        tag = TagCRUD.create(db_session, TagCreate(name="Action"))
        MediaTagCRUD.create(
            db_session,
            MediaTagCreate(media_id=movie.id, tag_id=tag.id),
            MediaTypeEnum.MOVIE,
        )

        exists = MediaTagCRUD.exists(db_session, movie.id, tag.id)
        not_exists = MediaTagCRUD.exists(db_session, movie.id, 99999)

        assert exists is True
        assert not_exists is False

    def test_set_tags_for_media(self, db_session):
        movie = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Test", runtime=90)
        )

        tags = MediaTagCRUD.set_tags_for_media(
            db_session, movie.id, MediaTypeEnum.MOVIE, ["Action", "Thriller", "Drama"]
        )

        assert len(tags) == 3
        assert {t.name for t in tags} == {"Action", "Thriller", "Drama"}

    def test_set_tags_replaces_existing(self, db_session):
        movie = MediaCRUD.create_movie(
            db_session, MovieCreate(title="Test", runtime=90)
        )

        MediaTagCRUD.set_tags_for_media(
            db_session, movie.id, MediaTypeEnum.MOVIE, ["Tag1", "Tag2"]
        )
        MediaTagCRUD.set_tags_for_media(
            db_session, movie.id, MediaTypeEnum.MOVIE, ["Tag3", "Tag4"]
        )

        tags = MediaTagCRUD.get_tags_for_media(db_session, movie.id)

        assert len(tags) == 2
        assert {t.name for t in tags} == {"Tag3", "Tag4"}
