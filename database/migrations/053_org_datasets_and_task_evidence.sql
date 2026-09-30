-- AMAP Database Migration 053
-- Organization-scoped datasets, typed evidence records, and task→evidence
-- links for data-backed worker investigations.
--
-- dataset_records stores interconnected, typed sample records (production,
-- inspection, maintenance, incident, and organization-specific types) with
-- JSONB payloads. task_evidence links a task to the records a worker must
-- investigate. tasks gains an optional decision prompt/options so an
-- investigation task can capture a worker classification through the
-- existing task completion flow (result_data.classification).

CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_id UUID NOT NULL,

    name TEXT NOT NULL,
    description TEXT,
    domain TEXT NOT NULL DEFAULT 'general',

    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('draft', 'active', 'inactive', 'archived')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT datasets_organization_id_fkey
        FOREIGN KEY (organization_id)
        REFERENCES organizations(id)
        ON DELETE RESTRICT,

    CONSTRAINT datasets_organization_name_key
        UNIQUE (organization_id, name)
);

CREATE INDEX idx_datasets_organization_id
    ON datasets(organization_id);

CREATE TABLE dataset_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    dataset_id UUID NOT NULL,
    organization_id UUID NOT NULL,

    record_type TEXT NOT NULL,
    title TEXT NOT NULL,
    source_ref TEXT,

    payload JSONB NOT NULL DEFAULT '{}'::jsonb,

    occurred_at TIMESTAMPTZ,

    related_record_id UUID,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT dataset_records_dataset_id_fkey
        FOREIGN KEY (dataset_id)
        REFERENCES datasets(id)
        ON DELETE RESTRICT,

    CONSTRAINT dataset_records_organization_id_fkey
        FOREIGN KEY (organization_id)
        REFERENCES organizations(id)
        ON DELETE RESTRICT,

    CONSTRAINT dataset_records_related_record_id_fkey
        FOREIGN KEY (related_record_id)
        REFERENCES dataset_records(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_dataset_records_dataset_id
    ON dataset_records(dataset_id);

CREATE INDEX idx_dataset_records_organization_id
    ON dataset_records(organization_id);

CREATE INDEX idx_dataset_records_record_type
    ON dataset_records(record_type);

CREATE TABLE task_evidence (
    task_id UUID NOT NULL,
    record_id UUID NOT NULL,

    relevance TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT task_evidence_pk
        PRIMARY KEY (task_id, record_id),

    CONSTRAINT task_evidence_task_id_fkey
        FOREIGN KEY (task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE,

    CONSTRAINT task_evidence_record_id_fkey
        FOREIGN KEY (record_id)
        REFERENCES dataset_records(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_task_evidence_record_id
    ON task_evidence(record_id);

-- Optional decision capture for investigation tasks (NULL for plain
-- assembly tasks — backward compatible, no backfill required).
ALTER TABLE tasks ADD COLUMN decision_prompt TEXT;
ALTER TABLE tasks ADD COLUMN decision_options JSONB;
