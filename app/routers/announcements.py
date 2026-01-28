"""Announcement routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.post("/", response_model=schemas.AnnouncementResponse)
def create_announcement(
    announcement: schemas.AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Create a new announcement (admin only)."""
    new_announcement = models.Announcement(
        title=announcement.title,
        content=announcement.content,
        priority=announcement.priority,
        posted_by=current_user.email
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return {
        "id": new_announcement.id,
        "title": new_announcement.title,
        "content": new_announcement.content,
        "priority": new_announcement.priority,
        "posted_by": new_announcement.posted_by,
        "created_at": new_announcement.created_at.isoformat() if new_announcement.created_at else ""
    }


@router.get("/")
def get_announcements(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all announcements."""
    announcements = db.query(models.Announcement).order_by(
        models.Announcement.created_at.desc()
    ).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "priority": a.priority,
            "posted_by": a.posted_by,
            "created_at": a.created_at.isoformat() if a.created_at else ""
        }
        for a in announcements
    ]


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    """Delete an announcement (admin only)."""
    announcement = db.query(models.Announcement).filter(
        models.Announcement.id == announcement_id
    ).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(announcement)
    db.commit()
    return {"message": "Announcement deleted successfully"}
