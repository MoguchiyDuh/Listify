import re
from typing import List, Optional

from app.core import setup_logger
from app.models import MediaTypeEnum
from app.models.tag import MediaTag, Tag
from app.schemas import MediaTagCreate, TagCreate, TagUpdate
from sqlalchemy import and_
from sqlalchemy.orm import Session

logger = setup_logger(__name__)


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text


class TagCRUD:
    @staticmethod
    def create(db: Session, tag_data: TagCreate) -> Tag:
        logger.debug(f"Creating tag: {tag_data.name}")

        slug = slugify(tag_data.name)

        # Ensure unique slug
        base_slug = slug
        counter = 1
        while db.query(Tag).filter(Tag.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        tag = Tag(name=tag_data.name, slug=slug)

        db.add(tag)
        db.commit()
        db.refresh(tag)

        logger.debug(f"Tag created successfully: {tag.id}, slug: {tag.slug}")
        return tag

    @staticmethod
    def get_by_id(db: Session, tag_id: int) -> Optional[Tag]:
        logger.debug(f"Fetching tag by ID: {tag_id}")

        tag = db.query(Tag).filter(Tag.id == tag_id).first()

        if tag:
            logger.debug(f"Tag found: {tag.name}")
        else:
            logger.debug(f"Tag not found: {tag_id}")

        return tag

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Tag]:
        logger.debug(f"Fetching tag by slug: {slug}")

        tag = db.query(Tag).filter(Tag.slug == slug).first()

        if tag:
            logger.debug(f"Tag found: {tag.name}")
        else:
            logger.debug(f"Tag not found: {slug}")

        return tag

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Tag]:
        logger.debug(f"Fetching tag by name: {name}")

        tag = db.query(Tag).filter(Tag.name.ilike(name)).first()

        if tag:
            logger.debug(f"Tag found: {tag.id}")
        else:
            logger.debug(f"Tag not found: {name}")

        return tag

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
        logger.debug(f"Fetching all tags - skip: {skip}, limit: {limit}")

        tags = db.query(Tag).offset(skip).limit(limit).all()

        logger.debug(f"Found {len(tags)} tags")
        return tags

    @staticmethod
    def search(db: Session, query: str, limit: int = 20) -> List[Tag]:
        logger.debug(f"Searching tags - query: {query}, limit: {limit}")

        tags = db.query(Tag).filter(Tag.name.ilike(f"%{query}%")).limit(limit).all()

        logger.debug(f"Found {len(tags)} tags matching search")
        return tags

    @staticmethod
    def update(db: Session, tag_id: int, tag_data: TagUpdate) -> Optional[Tag]:
        logger.debug(f"Updating tag: {tag_id}")

        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            logger.debug(f"Tag not found for update: {tag_id}")
            return None

        update_data = tag_data.model_dump(exclude_unset=True)

        if "name" in update_data:
            tag.name = update_data["name"]
            tag.slug = slugify(update_data["name"])

            # Ensure unique slug
            base_slug = tag.slug
            counter = 1
            while (
                db.query(Tag)
                .filter(and_(Tag.slug == tag.slug, Tag.id != tag_id))
                .first()
            ):
                tag.slug = f"{base_slug}-{counter}"
                counter += 1

        db.commit()
        db.refresh(tag)

        logger.debug(f"Tag updated successfully: {tag.id}")
        return tag

    @staticmethod
    def delete(db: Session, tag_id: int) -> bool:
        logger.debug(f"Deleting tag: {tag_id}")

        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            logger.debug(f"Tag not found for deletion: {tag_id}")
            return False

        db.delete(tag)
        db.commit()

        logger.debug(f"Tag deleted successfully: {tag_id}")
        return True

    @staticmethod
    def get_or_create(db: Session, name: str) -> Tag:
        logger.debug(f"Get or create tag: {name}")

        tag = TagCRUD.get_by_name(db, name)
        if tag:
            logger.debug(f"Tag already exists: {tag.id}")
            return tag

        return TagCRUD.create(db, TagCreate(name=name))


class MediaTagCRUD:
    @staticmethod
    def create(
        db: Session, media_tag_data: MediaTagCreate, media_type: MediaTypeEnum
    ) -> MediaTag:
        logger.debug(
            f"Creating media-tag association - media: {media_tag_data.media_id}, "
            f"tag: {media_tag_data.tag_id}, type: {media_type}"
        )

        media_tag = MediaTag(
            media_id=media_tag_data.media_id,
            tag_id=media_tag_data.tag_id,
            media_type=media_type,
        )

        db.add(media_tag)
        db.commit()
        db.refresh(media_tag)

        logger.debug(f"Media-tag association created successfully: {media_tag.id}")
        return media_tag

    @staticmethod
    def get_tags_for_media(db: Session, media_id: int) -> List[Tag]:
        logger.debug(f"Fetching tags for media: {media_id}")

        tags = db.query(Tag).join(MediaTag).filter(MediaTag.media_id == media_id).all()

        logger.debug(f"Found {len(tags)} tags for media")
        return tags

    @staticmethod
    def get_media_by_tag(
        db: Session, tag_id: int, media_type: Optional[MediaTypeEnum] = None
    ) -> List[int]:
        logger.debug(f"Fetching media IDs for tag: {tag_id}, type: {media_type}")

        query = db.query(MediaTag.media_id).filter(MediaTag.tag_id == tag_id)

        if media_type:
            query = query.filter(MediaTag.media_type == media_type)

        media_ids = [row[0] for row in query.all()]

        logger.debug(f"Found {len(media_ids)} media items for tag")
        return media_ids

    @staticmethod
    def delete(db: Session, media_id: int, tag_id: int) -> bool:
        logger.debug(
            f"Deleting media-tag association - media: {media_id}, tag: {tag_id}"
        )

        media_tag = (
            db.query(MediaTag)
            .filter(and_(MediaTag.media_id == media_id, MediaTag.tag_id == tag_id))
            .first()
        )

        if not media_tag:
            logger.debug(f"Media-tag association not found for deletion")
            return False

        db.delete(media_tag)
        db.commit()

        logger.debug(f"Media-tag association deleted successfully")
        return True

    @staticmethod
    def delete_all_for_media(db: Session, media_id: int) -> int:
        logger.debug(f"Deleting all tags for media: {media_id}")

        count = db.query(MediaTag).filter(MediaTag.media_id == media_id).delete()
        db.commit()

        logger.debug(f"Deleted {count} media-tag associations")
        return count

    @staticmethod
    def exists(db: Session, media_id: int, tag_id: int) -> bool:
        logger.debug(f"Checking media-tag existence - media: {media_id}, tag: {tag_id}")

        exists = (
            db.query(MediaTag)
            .filter(and_(MediaTag.media_id == media_id, MediaTag.tag_id == tag_id))
            .first()
            is not None
        )

        logger.debug(f"Media-tag association exists: {exists}")
        return exists

    @staticmethod
    def set_tags_for_media(
        db: Session, media_id: int, media_type: MediaTypeEnum, tag_names: List[str]
    ) -> List[Tag]:
        logger.debug(f"Setting tags for media: {media_id}, tags: {tag_names}")

        # Delete existing associations
        MediaTagCRUD.delete_all_for_media(db, media_id)

        # Create new associations
        tags = []
        for tag_name in tag_names:
            tag = TagCRUD.get_or_create(db, tag_name.strip())
            MediaTagCRUD.create(
                db, MediaTagCreate(media_id=media_id, tag_id=tag.id), media_type
            )
            tags.append(tag)

        logger.debug(f"Set {len(tags)} tags for media")
        return tags
