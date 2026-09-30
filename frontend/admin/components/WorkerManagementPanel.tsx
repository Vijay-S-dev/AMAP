'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/shared/api/client';
import { useAccessibility } from '@/shared/theme/AccessibilityContext';

export function WorkerManagementPanel() {
  const { announce, playAudioCue } = useAccessibility();
  const [workers, setWorkers] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [editingWorker, setEditingWorker] = useState<any | null>(null);
  const [busyUserId, setBusyUserId] = useState<string | null>(null);

  // Invite Form
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [badgeNumber, setBadgeNumber] = useState('');
  const [departmentId, setDepartmentId] = useState('');
  const [preferredModality, setPreferredModality] = useState('multimodal');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Edit Form (existing worker)
  const [editFullName, setEditFullName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editBadge, setEditBadge] = useState('');
  const [editDept, setEditDept] = useState('');
  const [isSavingEdit, setIsSavingEdit] = useState(false);

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const loadData = async () => {
    const [workersData, deptsData] = await Promise.all([
      api.getOrgWorkers(statusFilter ? { status: statusFilter } : {}),
      api.getOrgDepartments(),
    ]);
    setWorkers(workersData.items || []);
    setDepartments(deptsData || []);
    if (deptsData?.length > 0 && !departmentId) {
      setDepartmentId(deptsData[0].id);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !fullName.trim()) return;

    setIsSubmitting(true);
    try {
      await api.inviteOrgWorker({
        email: email.trim(),
        full_name: fullName.trim(),
        badge_number: badgeNumber.trim() || undefined,
        department_id: departmentId || undefined,
        preferred_modality: preferredModality,
      });
      announce(`Worker invitation sent to ${email}. Onboarding link generated.`);
      playAudioCue('confirm');
      setEmail('');
      setFullName('');
      setBadgeNumber('');
      setShowInviteModal(false);
      loadData();
    } catch {
      announce('Failed to send worker invitation.');
      playAudioCue('alert');
    } finally {
      setIsSubmitting(false);
    }
  };

  const openEditModal = (w: any) => {
    setEditingWorker(w);
    setEditFullName(w.full_name || '');
    setEditEmail(w.email || '');
    setEditBadge(w.badge_number || '');
    setEditDept(w.department_id || '');
  };

  const handleUpdateWorker = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingWorker) return;
    setIsSavingEdit(true);
    try {
      await api.updateOrgWorker(editingWorker.user_id, {
        full_name: editFullName.trim() || undefined,
        email: editEmail.trim() || undefined,
        badge_number: editBadge.trim() || undefined,
        department_id: editDept || undefined,
      });
      announce(`Worker ${editFullName || editingWorker.full_name} updated.`);
      playAudioCue('confirm');
      setEditingWorker(null);
      loadData();
    } catch (err: any) {
      announce(`Update failed: ${err?.message || 'server error'}`);
      playAudioCue('alert');
    } finally {
      setIsSavingEdit(false);
    }
  };

  const handleToggleAccountStatus = async (w: any) => {
    const nextStatus = w.account_status === 'suspended' ? 'active' : 'suspended';
    setBusyUserId(w.user_id);
    try {
      await api.updateOrgWorker(w.user_id, { status: nextStatus });
      announce(
        nextStatus === 'suspended'
          ? `Account ${w.email} deactivated — login is now blocked.`
          : `Account ${w.email} reactivated.`
      );
      playAudioCue(nextStatus === 'suspended' ? 'alert' : 'confirm');
      loadData();
    } catch (err: any) {
      announce(`Status change failed: ${err?.message || 'server error'}`);
      playAudioCue('alert');
    } finally {
      setBusyUserId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    const s = status.toUpperCase();
    let bg = 'rgba(107, 114, 128, 0.2)';
    let color = '#9ca3af';

    if (s === 'WORKING') {
      bg = 'rgba(59, 130, 246, 0.2)';
      color = '#60a5fa';
    } else if (s === 'READY') {
      bg = 'rgba(16, 185, 129, 0.2)';
      color = '#34d399';
    } else if (s === 'ASSISTANCE_REQUESTED') {
      bg = 'rgba(239, 68, 68, 0.2)';
      color = '#f87171';
    } else if (s === 'ONBOARDING' || s === 'INVITED') {
      bg = 'rgba(245, 158, 11, 0.2)';
      color = '#fbbf24';
    }

    return (
      <span
        style={{
          fontSize: '0.75rem',
          fontWeight: 700,
          padding: '0.25rem 0.6rem',
          borderRadius: '20px',
          backgroundColor: bg,
          color: color,
        }}
      >
        {s}
      </span>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header with Filter and Invite Action */}
      <div className="glass-panel" style={{ padding: '1.5rem', borderRadius: '18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800 }}>👷 Enterprise Workforce Directory</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.2rem' }}>
            Monitor operational readiness, interaction modes, and invite workers with accessible first-time onboarding.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Status Filter */}
          <select
            className="input-field"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ minHeight: '48px', padding: '0 1rem' }}
            aria-label="Filter workers by status"
          >
            <option value="">All Operational Statuses</option>
            <option value="WORKING">Working (Active Task)</option>
            <option value="READY">Ready (Available)</option>
            <option value="ASSISTANCE_REQUESTED">Assistance Requested</option>
            <option value="ONBOARDING">In Onboarding</option>
            <option value="INVITED">Invited</option>
          </select>

          <button
            type="button"
            className="btn btn-primary"
            onClick={() => setShowInviteModal(true)}
            style={{ minHeight: '48px', padding: '0 1.25rem', background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' }}
          >
            ➕ Invite Worker
          </button>
        </div>
      </div>

      {/* Workers Roster Table */}
      <div className="glass-panel" style={{ borderRadius: '18px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Worker</th>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Badge / Department</th>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Interaction Modality</th>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Current Assignment</th>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Operational Status</th>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Account / Actions</th>
            </tr>
          </thead>
          <tbody>
            {workers.map((w) => (
              <tr key={w.worker_profile_id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <td style={{ padding: '1rem 1.25rem' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{w.full_name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{w.email}</div>
                </td>
                <td style={{ padding: '1rem 1.25rem', fontSize: '0.9rem' }}>
                  <div style={{ fontWeight: 600 }}>{w.badge_number || '—'}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{w.department_name || 'Unassigned'}</div>
                </td>
                <td style={{ padding: '1rem 1.25rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                    {w.interaction_mode === 'multimodal' && '🖐️ + 🎙️ Multimodal'}
                    {w.interaction_mode === 'gesture' && '🖐️ Gesture Only'}
                    {w.interaction_mode === 'voice' && '🎙️ Voice Only'}
                  </span>
                  <div style={{ fontSize: '0.75rem', color: w.training_completed ? '#10b981' : '#f59e0b', marginTop: '0.15rem' }}>
                    {w.training_completed ? '✓ Training Certified' : '⏳ In Training Onboarding'}
                  </div>
                </td>
                <td style={{ padding: '1rem 1.25rem', fontSize: '0.9rem' }}>
                  {w.current_task_name ? (
                    <span style={{ fontWeight: 600, color: '#60a5fa' }}>{w.current_task_name}</span>
                  ) : (
                    <span style={{ color: 'var(--text-secondary)' }}>— No Active Task —</span>
                  )}
                </td>
                <td style={{ padding: '1rem 1.25rem' }}>
                  {getStatusBadge(w.status)}
                </td>
                <td style={{ padding: '1rem 1.25rem' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'flex-start' }}>
                    <span
                      aria-label={`Account status: ${w.account_status || 'active'}`}
                      style={{
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        padding: '0.25rem 0.6rem',
                        borderRadius: '20px',
                        backgroundColor: w.account_status === 'active' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                        color: w.account_status === 'active' ? '#34d399' : '#f87171',
                      }}
                    >
                      {w.account_status === 'active' ? '● Active' : '⏸ Deactivated'}
                    </span>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => openEditModal(w)}
                        style={{ minHeight: '40px', padding: '0 0.9rem', fontSize: '0.8rem' }}
                      >
                        ✏️ Edit
                      </button>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        disabled={busyUserId === w.user_id}
                        onClick={() => handleToggleAccountStatus(w)}
                        aria-label={w.account_status === 'active' ? `Deactivate account ${w.email}` : `Reactivate account ${w.email}`}
                        style={{ minHeight: '40px', padding: '0 0.9rem', fontSize: '0.8rem' }}
                      >
                        {busyUserId === w.user_id ? '…' : w.account_status === 'active' ? '⏸️ Deactivate' : '▶️ Reactivate'}
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Invite Worker Modal Dialog */}
      {showInviteModal && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="worker-modal-title"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem',
          }}
        >
          <div className="glass-panel" style={{ width: '100%', maxWidth: '520px', padding: '2rem', borderRadius: '24px' }}>
            <h3 id="worker-modal-title" style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: '0.5rem' }}>
              ➕ Invite Assembly Worker
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
              Invite a new hire or returning worker. The worker will be guided through AMAP multimodal gesture & speech calibration.
            </p>

            <form onSubmit={handleInvite} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                  Full Name
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Maria Rodriguez"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  style={{ width: '100%', minHeight: '48px' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                  Email Address
                </label>
                <input
                  type="email"
                  className="input-field"
                  placeholder="e.g. maria.newhire@amap.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  style={{ width: '100%', minHeight: '48px' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                    Badge Number (Optional)
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    placeholder="e.g. WRK-1060"
                    value={badgeNumber}
                    onChange={(e) => setBadgeNumber(e.target.value)}
                    style={{ width: '100%', minHeight: '48px' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                    Department
                  </label>
                  <select
                    className="input-field"
                    value={departmentId}
                    onChange={(e) => setDepartmentId(e.target.value)}
                    style={{ width: '100%', minHeight: '48px' }}
                  >
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                  Preferred Interaction Mode
                </label>
                <select
                  className="input-field"
                  value={preferredModality}
                  onChange={(e) => setPreferredModality(e.target.value)}
                  style={{ width: '100%', minHeight: '48px' }}
                >
                  <option value="multimodal">🖐️ + 🎙️ Multimodal (Gesture + Voice)</option>
                  <option value="gesture">🖐️ Optical Gesture Only</option>
                  <option value="voice">🎙️ Speech Recognition Only</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowInviteModal(false)}
                  style={{ minHeight: '48px', padding: '0 1.25rem' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting}
                  style={{ minHeight: '48px', padding: '0 1.5rem', background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' }}
                >
                  {isSubmitting ? 'Sending...' : 'Send Onboarding Invite'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Worker Modal Dialog */}
      {editingWorker && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="worker-edit-modal-title"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem',
          }}
        >
          <div className="glass-panel" style={{ width: '100%', maxWidth: '520px', padding: '2rem', borderRadius: '24px' }}>
            <h3 id="worker-edit-modal-title" style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: '0.5rem' }}>
              ✏️ Edit Worker
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
              Update identity, badge, and department for {editingWorker.full_name}. Changes persist immediately in PostgreSQL.
            </p>

            <form onSubmit={handleUpdateWorker} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                  Full Name
                </label>
                <input
                  type="text"
                  className="input-field"
                  value={editFullName}
                  onChange={(e) => setEditFullName(e.target.value)}
                  required
                  style={{ width: '100%', minHeight: '48px' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                  Email Address
                </label>
                <input
                  type="email"
                  className="input-field"
                  value={editEmail}
                  onChange={(e) => setEditEmail(e.target.value)}
                  required
                  style={{ width: '100%', minHeight: '48px' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                    Badge Number
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    value={editBadge}
                    onChange={(e) => setEditBadge(e.target.value)}
                    style={{ width: '100%', minHeight: '48px' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                    Department
                  </label>
                  <select
                    className="input-field"
                    value={editDept}
                    onChange={(e) => setEditDept(e.target.value)}
                    style={{ width: '100%', minHeight: '48px' }}
                  >
                    <option value="">Unassigned</option>
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setEditingWorker(null)}
                  style={{ minHeight: '48px', padding: '0 1.25rem' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSavingEdit}
                  style={{ minHeight: '48px', padding: '0 1.5rem', background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' }}
                >
                  {isSavingEdit ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
