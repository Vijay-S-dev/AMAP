"""
Task evidence repository.

Provides database access operations for the task_evidence / dataset_records
tables (organization-scoped evidence records linked to tasks).
Business logic does not belong in this module.
"""

from typing import Any, Optional
from uuid import UUID

from psycopg.rows import dict_row

from app.database import get_db_connection


class TaskEvidenceRepository:
    """Data access operations for task → dataset record evidence links."""

    def list_by_task_id(
        self,
        task_id: UUID,
        organization_id: Optional[UUID] = None,
    ) -> list[dict[str, Any]]:
        """
        Return evidence records linked to a task.

        When organization_id is given, only records belonging to that
        organization are returned (defense-in-depth tenant scoping in
        addition to the service-level tenancy check).
        """
        query = """
            SELECT
                dr.id,
                dr.dataset_id,
                dr.organization_id,
                dr.record_type,
                dr.title,
                dr.source_ref,
                dr.payload,
                dr.occurred_at,
                dr.related_record_id,
                d.name AS dataset_name,
                te.relevance
            FROM task_evidence te
            JOIN dataset_records dr ON dr.id = te.record_id
            JOIN datasets d ON d.id = dr.dataset_id
            WHERE te.task_id = %s
        """
        params: list[Any] = [task_id]
        if organization_id is not None:
            query += " AND dr.organization_id = %s"
            params.append(organization_id)
        query += " ORDER BY dr.occurred_at DESC NULLS LAST, dr.created_at ASC"

        with get_db_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, tuple(params))
                return list(cursor.fetchall())
