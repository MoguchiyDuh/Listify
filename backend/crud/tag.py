import re
from typing import List, Optional

from models import MediaTag, MediaTypeEnum, Tag
from sqlalchemy.orm import Session

from .base import CRUDBase, logger

logger = logger.getChild("tag")


class CRUDTag(CRUDBase[Tag]):
    """CRUD operations for tags"""

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to slug"""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text

    def get_by_name(self, db: Session, *, name: str) -> Optional[Tag]:
        """Get tag by name (case-insensitive)"""
        logger.debug(f"Getting tag by name: {name}")
        return db.query(Tag).filter(Tag.name.ilike(name)).first()

    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Tag]:
        """Get tag by slug"""
        logger.debug(f"Getting tag by slug: {slug}")
        return db.query(Tag).filter(Tag.slug == slug).first()

    def get_or_create(self, db: Session, *, name: str) -> Tag:
        """Get existing tag or create new one"""
        name = name.strip()

        # Check if tag exists (case-insensitive)
        existing_tag = self.get_by_name(db, name=name)
        if existing_tag:
            logger.debug(f"Found existing tag: {existing_tag.name}")
            return existing_tag

        # Create new tag
        slug = self._slugify(name)
        logger.info(f"Creating new tag: {name} (slug: {slug})")

        tag = Tag(name=name, slug=slug)
        db.add(tag)
        db.commit()
        db.refresh(tag)

        logger.debug(f"Created tag with id: {tag.id}")
        return tag

    def get_tags_for_media(self, db: Session, *, media_id: int) -> List[Tag]:
        """Get all tags for a media item"""
        logger.debug(f"Getting tags for media_id: {media_id}")
        return db.query(Tag).join(MediaTag).filter(MediaTag.media_id == media_id).all()

    def get_media_by_tag(
        self, db: Session, *, tag_id: int, media_type: Optional[MediaTypeEnum] = None
    ) -> List[int]:
        """Get all media IDs for a tag, optionally filtered by type"""
        logger.debug(f"Getting media for tag_id: {tag_id}, type: {media_type}")
        query = db.query(MediaTag.media_id).filter(MediaTag.tag_id == tag_id)

        if media_type:
            query = query.filter(MediaTag.media_type == media_type)

        return [row[0] for row in query.all()]

    def add_tags_to_media(
        self,
        db: Session,
        *,
        media_id: int,
        media_type: MediaTypeEnum,
        tag_names: List[str],
    ) -> List[Tag]:
        """Add tags to media item, creating tags if needed"""
        if not tag_names:
            return []

        logger.info(f"Adding {len(tag_names)} tags to media_id: {media_id}")

        # Remove duplicates (case-insensitive) and empty strings
        seen = set()
        unique_names = []
        for name in tag_names:
            name = name.strip()
            if name and name.lower() not in seen:
                seen.add(name.lower())
                unique_names.append(name)

        tags = []
        for tag_name in unique_names:
            # Get or create tag
            tag = self.get_or_create(db, name=tag_name)
            tags.append(tag)

            # Check if association already exists
            existing = (
                db.query(MediaTag)
                .filter(MediaTag.media_id == media_id, MediaTag.tag_id == tag.id)
                .first()
            )

            if not existing:
                # Create association
                media_tag = MediaTag(
                    media_id=media_id, tag_id=tag.id, media_type=media_type
                )
                db.add(media_tag)
                logger.debug(f"Associated tag '{tag.name}' with media_id: {media_id}")

        db.commit()
        logger.info(f"Successfully added {len(tags)} tags to media_id: {media_id}")
        return tags

    def remove_tags_from_media(
        self, db: Session, *, media_id: int, tag_ids: Optional[List[int]] = None
    ):
        """Remove tags from media item. If tag_ids is None, remove all tags"""
        logger.info(f"Removing tags from media_id: {media_id}")

        query = db.query(MediaTag).filter(MediaTag.media_id == media_id)

        if tag_ids:
            query = query.filter(MediaTag.tag_id.in_(tag_ids))

        count = query.delete(synchronize_session=False)
        db.commit()

        logger.debug(f"Removed {count} tag associations from media_id: {media_id}")

    def update_media_tags(
        self,
        db: Session,
        *,
        media_id: int,
        media_type: MediaTypeEnum,
        tag_names: List[str],
    ) -> List[Tag]:
        """Update tags for media item (remove old, add new)"""
        logger.info(f"Updating tags for media_id: {media_id}")

        # Remove all existing tags
        self.remove_tags_from_media(db, media_id=media_id)

        # Add new tags
        return self.add_tags_to_media(
            db, media_id=media_id, media_type=media_type, tag_names=tag_names
        )


tag_crud = CRUDTag(Tag)
