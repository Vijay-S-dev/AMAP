"""
Admin configuration and management schemas for AMAP.
"""

from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import Field

from models.base import AMAPBaseModel, StrictInputModel


class UserStatusUpdatePayload(StrictInputModel):
    """Payload to activate, suspend, or archive a user account."""
    status: str = Field(..., pattern="^(active|suspended|archived)$", description="New account status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")


class UserDetailUpdatePayload(StrictInputModel):
    """Payload to update a user's identity details (full name / email)."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="New full name")
    email: Optional[str] = Field(None, min_length=3, max_length=255, description="New email address (organization-unique)")


class UserRoleAssignPayload(StrictInputModel):
    """Payload to assign a role to an organization user."""
    role_name: str = Field(..., min_length=1, max_length=100, description="Name of role to assign")


class AuditLogQueryFilter(StrictInputModel):
    """Filter parameters for querying audit trails."""
    event_type: Optional[str] = Field(None, max_length=100)
    actor_user_id: Optional[UUID] = None
    resource_type: Optional[str] = Field(None, max_length=100)
    limit: int = Field(50, ge=1, le=200)
