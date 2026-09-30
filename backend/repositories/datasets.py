"""
Datasets repository.

Provides database access operations for the datasets / dataset_records
tables (organization-owned datasets with typed evidence records).
Business logic does not belong in this module.
"""

from typing import Any, Optional
from uuid import UUID

from psycopg.rows import dict_row

from app.database import get_db_connection


class DatasetsRepository:
    """Data access operations for organization-owned datasets."""

    def get_by_id(
        self,
        dataset_id: UUID,
    ) -> Optional[dict[str, Any]]:
        """Return a dataset by its ID, or None if it does not exist."""
        with get_db_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT id, organization_id, name, description, domain,
                           status, created_at, updated_at
                    FROM datasets
                    WHERE id = %s
                    """,
                    (dataset_id,),
                )
                return cursor.fetchone()

    def list_by_organization(
        self,
        organization_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Return all datasets owned by an organization with aggregate record
        counts and the distinct record types present in each dataset.
        """
        with get_db_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        d.id,
                        d.organization_id,
                        d.name,
                        d.description,
                        d.domain,
                        d.status,
                        d.created_at,
                        d.updated_at,
                        COUNT(r.id) AS record_count,
                        COALESCE(
                            ARRAY_AGG(DISTINCT r.record_type)
                                FILTER (WHERE r.record_type IS NOT NULL),
                            ARRAY[]::TEXT[]
                        ) AS record_types
                    FROM datasets d
                    LEFT JOIN dataset_records r ON r.dataset_id = d.id
                    WHERE d.organization_id = %s
                    GROUP BY d.id
                    ORDER BY d.created_at, d.name
                    """,
                    (organization_id,),
                )
                return list(cursor.fetchall())

    def list_records(
        self,
        dataset_id: UUID,
        limit: int = 25,
        offset: int = 0,
        record_type: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Return (records, total count) for a dataset, optionally filtered by
        record type. The caller is responsible for verifying the dataset
        belongs to the requesting organization BEFORE calling this method.
        """
        filters = ["dataset_id = %s"]
        params: list[Any] = [dataset_id]
        if record_type:
            filters.append("record_type = %s")
            params.append(record_type)
        where_sql = " AND ".join(filters)

        with get_db_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    f"""
                    SELECT COUNT(*) AS total
                    FROM dataset_records
                    WHERE {where_sql}
                    """,
                    tuple(params),
                )
                total = int(cursor.fetchone()["total"])

                cursor.execute(
                    f"""
                    SELECT
                        id,
                        dataset_id,
                        organization_id,
                        record_type,
                        title,
                        source_ref,
                        payload,
                        occurred_at,
                        related_record_id,
                        created_at,
                        updated_at
                    FROM dataset_records
                    WHERE {where_sql}
                    ORDER BY occurred_at DESC NULLS LAST, created_at ASC
                    LIMIT %s OFFSET %s
                    """,
                    tuple(params) + (limit, offset),
                )
                rows = list(cursor.fetchall())
                return rows, total
