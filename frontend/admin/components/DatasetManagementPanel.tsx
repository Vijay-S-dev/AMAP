'use client';

/**
 * Dataset Management Panel (frontend/admin/components/DatasetManagementPanel.tsx)
 *
 * Phase 7 — Organization-owned datasets. Lists the organization's datasets
 * with real record statistics from PostgreSQL and lets an admin browse the
 * typed records inside each dataset (with a record-type filter). All data
 * comes from GET /organizations/manage/datasets and
 * GET /organizations/manage/datasets/{id}/records — no hardcoded datasets.
 * Timestamps are displayed in IST (UTC+05:30).
 */

import React, { useEffect, useState } from 'react';
import { api } from '@/shared/api/client';
import { useAccessibility } from '@/shared/theme/AccessibilityContext';
import { formatIST } from '@/shared/utils/istTime';

const PAGE_SIZE = 25;

export function DatasetManagementPanel() {
  const { announce, playAudioCue } = useAccessibility();
  const [datasets, setDatasets] = useState<any[]>([]);
  const [loadingError, setLoadingError] = useState<string | null>(null);

  const [selectedDataset, setSelectedDataset] = useState<any | null>(null);
  const [records, setRecords] = useState<any[]>([]);
  const [recordTotal, setRecordTotal] = useState(0);
  const [recordPage, setRecordPage] = useState(1);
  const [recordTypeFilter, setRecordTypeFilter] = useState('');
  const [isLoadingRecords, setIsLoadingRecords] = useState(false);
  const [expandedRecord, setExpandedRecord] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoadingError(null);
    try {
      const data = await api.getOrgDatasets();
      setDatasets(data || []);
      if (!data || data.length === 0) {
        announce('No datasets are registered for your organization yet.');
      }
    } catch (err: any) {
      setLoadingError(`Failed to load datasets: ${err?.message || 'server error'}`);
      playAudioCue('alert');
    }
  };

  const openDataset = async (dataset: any, page = 1, recordType = recordTypeFilter) => {
    setSelectedDataset(dataset);
    setIsLoadingRecords(true);
    setRecordPage(page);
    try {
      const result = await api.getOrgDatasetRecords(dataset.id, {
        record_type: recordType || undefined,
        page,
        page_size: PAGE_SIZE,
      });
      setRecords(result.items || []);
      setRecordTotal(result.total_count || 0);
    } catch (err: any) {
      setRecords([]);
      setRecordTotal(0);
      announce(`Failed to load records: ${err?.message || 'server error'}`);
      playAudioCue('alert');
    } finally {
      setIsLoadingRecords(false);
    }
  };

  const applyTypeFilter = async (recordType: string) => {
    setRecordTypeFilter(recordType);
    if (selectedDataset) {
      await openDataset(selectedDataset, 1, recordType);
    }
  };

  const domainLabel = (domain: string) =>
    domain.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '1.5rem', borderRadius: '18px' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800 }}>🗄️ Organization Datasets</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.2rem' }}>
            Organization-owned datasets and their records, stored in PostgreSQL and scoped to your
            organization server-side. All data is synthetic sample data. Timestamps shown in IST.
          </p>
        </div>
      </div>

      {loadingError && (
        <div role="alert" className="glass-panel" style={{ padding: '1rem 1.25rem', borderRadius: '12px', borderLeft: '4px solid #f87171' }}>
          {loadingError}
        </div>
      )}

      {/* Dataset cards */}
      {datasets.length === 0 && !loadingError ? (
        <div className="glass-panel" style={{ padding: '2rem', borderRadius: '18px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          No datasets are registered for your organization yet.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {datasets.map((d) => {
            const isSelected = selectedDataset?.id === d.id;
            return (
              <button
                key={d.id}
                type="button"
                onClick={() => openDataset(d)}
                aria-pressed={isSelected}
                className="glass-panel"
                style={{
                  padding: '1.25rem',
                  borderRadius: '16px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  border: isSelected ? '2px solid var(--admin-purple, #8b5cf6)' : '1px solid var(--border-color)',
                  background: isSelected ? 'rgba(139, 92, 246, 0.08)' : undefined,
                }}
              >
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {domainLabel(d.domain || 'general')}
                </div>
                <div style={{ fontSize: '1.05rem', fontWeight: 800, marginTop: '0.25rem' }}>{d.name}</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.35rem' }}>{d.description || '—'}</div>
                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--worker-cyan)' }}>
                    {d.record_count} records
                  </span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {d.status.toUpperCase()}
                  </span>
                </div>
                {(d.record_types || []).length > 0 && (
                  <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginTop: '0.6rem' }}>
                    {(d.record_types || []).map((t: string) => (
                      <span
                        key={t}
                        style={{
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          padding: '0.15rem 0.5rem',
                          borderRadius: '12px',
                          background: 'rgba(255, 255, 255, 0.06)',
                          color: 'var(--text-secondary)',
                        }}
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Records of the selected dataset */}
      {selectedDataset && (
        <div className="glass-panel" style={{ borderRadius: '18px', overflow: 'hidden' }}>
          <div
            style={{
              padding: '1.25rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: '1rem',
              flexWrap: 'wrap',
              borderBottom: '1px solid var(--border-color)',
            }}
          >
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800 }}>{selectedDataset.name} — Records</h3>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                {recordTotal} record{recordTotal === 1 ? '' : 's'}
                {recordTypeFilter ? ` · filtered by '${recordTypeFilter}'` : ''}
              </span>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <select
                className="input-field"
                value={recordTypeFilter}
                onChange={(e) => applyTypeFilter(e.target.value)}
                aria-label="Filter records by type"
                style={{ minHeight: '44px', padding: '0 0.75rem' }}
              >
                <option value="">All record types</option>
                {(selectedDataset.record_types || []).map((t: string) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setSelectedDataset(null);
                  setRecordTypeFilter('');
                  setRecords([]);
                }}
                style={{ minHeight: '44px', padding: '0 1rem' }}
              >
                ✕ Close
              </button>
            </div>
          </div>

          {isLoadingRecords ? (
            <div style={{ padding: '2rem', color: 'var(--text-secondary)', textAlign: 'center' }}>Loading records…</div>
          ) : records.length === 0 ? (
            <div style={{ padding: '2rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
              No records{recordTypeFilter ? ` of type '${recordTypeFilter}'` : ''} in this dataset.
            </div>
          ) : (
            <>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', borderBottom: '1px solid var(--border-color)' }}>
                    <th style={{ padding: '0.9rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Record</th>
                    <th style={{ padding: '0.9rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Type / Source</th>
                    <th style={{ padding: '0.9rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Occurred (IST)</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((r) => (
                    <React.Fragment key={r.id}>
                      <tr
                        style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', cursor: 'pointer' }}
                        onClick={() => setExpandedRecord(expandedRecord === r.id ? null : r.id)}
                        aria-expanded={expandedRecord === r.id}
                      >
                        <td style={{ padding: '0.9rem 1.25rem' }}>
                          <div style={{ fontWeight: 700, fontSize: '0.92rem' }}>{r.title}</div>
                          {r.related_record_id && (
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                              🔗 linked record
                            </div>
                          )}
                        </td>
                        <td style={{ padding: '0.9rem 1.25rem', fontSize: '0.85rem' }}>
                          <span style={{ fontWeight: 700, color: 'var(--worker-cyan)' }}>{r.record_type}</span>
                          {r.source_ref && (
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.1rem' }}>{r.source_ref}</div>
                          )}
                        </td>
                        <td style={{ padding: '0.9rem 1.25rem', fontSize: '0.85rem' }}>{formatIST(r.occurred_at)}</td>
                      </tr>
                      {expandedRecord === r.id && (
                        <tr style={{ background: 'rgba(255, 255, 255, 0.02)' }}>
                          <td colSpan={3} style={{ padding: '0.75rem 1.25rem 1.25rem 1.25rem' }}>
                            <pre
                              style={{
                                fontSize: '0.78rem',
                                whiteSpace: 'pre-wrap',
                                margin: 0,
                                color: 'var(--text-secondary)',
                              }}
                            >
                              {JSON.stringify(r.payload, null, 2)}
                            </pre>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
              {recordTotal > PAGE_SIZE && (
                <div style={{ padding: '1rem 1.25rem', display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', borderTop: '1px solid var(--border-color)' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    disabled={recordPage <= 1}
                    onClick={() => openDataset(selectedDataset, recordPage - 1)}
                    style={{ minHeight: '40px', padding: '0 0.9rem' }}
                  >
                    ← Previous
                  </button>
                  <span style={{ alignSelf: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Page {recordPage} of {Math.max(1, Math.ceil(recordTotal / PAGE_SIZE))}
                  </span>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    disabled={recordPage >= Math.ceil(recordTotal / PAGE_SIZE)}
                    onClick={() => openDataset(selectedDataset, recordPage + 1)}
                    style={{ minHeight: '40px', padding: '0 0.9rem' }}
                  >
                    Next →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default DatasetManagementPanel;
