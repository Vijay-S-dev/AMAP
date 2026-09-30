'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/shared/api/client';
import { useAccessibility } from '@/shared/theme/AccessibilityContext';

export function SupervisorManagementPanel() {
  const { announce, playAudioCue } = useAccessibility();
  const [supervisors, setSupervisors] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [departmentId, setDepartmentId] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingSupervisor, setEditingSupervisor] = useState<any | null>(null);
  const [busyUserId, setBusyUserId] = useState<string | null>(null);
  const [editFullName, setEditFullName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editDept, setEditDept] = useState('');
  const [isSavingEdit, setIsSavingEdit] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const [sups, depts] = await Promise.all([
      api.getOrgSupervisors(),
      api.getOrgDepartments(),
    ]);
    setSupervisors(sups);
    setDepartments(depts);
    if (depts.length > 0 && !departmentId) {
      setDepartmentId(depts[0].id);
    }
  };

  const openEditModal = (sup: any) => {
    setEditingSupervisor(sup);
    setEditFullName(sup.full_name || '');
    setEditEmail(sup.email || '');
    setEditDept(sup.department_id || '');
  };

  const handleUpdateSupervisor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingSupervisor) return;
    setIsSavingEdit(true);
    try {
      await api.updateOrgSupervisor(editingSupervisor.user_id, {
        full_name: editFullName.trim() || undefined,
        email: editEmail.trim() || undefined,
        department_id: editDept || undefined,
      });
      announce(`Supervisor ${editFullName || editingSupervisor.full_name} updated.`);
      playAudioCue('confirm');
      setEditingSupervisor(null);
      loadData();
    } catch (err: any) {
      announce(`Update failed: ${err?.message || 'server error'}`);
      playAudioCue('alert');
    } finally {
      setIsSavingEdit(false);
    }
  };

  const handleToggleAccountStatus = async (sup: any) => {
    const nextStatus = sup.status === 'suspended' ? 'active' : 'suspended';
    setBusyUserId(sup.user_id);
    try {
      await api.updateOrgSupervisor(sup.user_id, { status: nextStatus });
      announce(
        nextStatus === 'suspended'
          ? `Account ${sup.email} deactivated — login is now blocked.`
          : `Account ${sup.email} reactivated.`
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

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !fullName.trim()) return;

    setIsSubmitting(true);
    try {
      await api.inviteOrgSupervisor({
        email: email.trim(),
        full_name: fullName.trim(),
        department_id: departmentId || undefined,
      });
      announce(`Supervisor invitation sent to ${email}.`);
      playAudioCue('confirm');
      setEmail('');
      setFullName('');
      setShowInviteModal(false);
      loadData();
    } catch {
      announce('Failed to send supervisor invitation.');
      playAudioCue('alert');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header with Invite Action */}
      <div className="glass-panel" style={{ padding: '1.5rem', borderRadius: '18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 800 }}>👥 Supervisor & Manager Roster</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.2rem' }}>
            Authorize and assign floor supervisors to oversee assembly stations and triage worker assistance tickets.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setShowInviteModal(true)}
          style={{ minHeight: '48px', padding: '0 1.25rem', background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' }}
        >
          ➕ Invite Supervisor
        </button>
      </div>

      {/* Supervisors Table */}
      <div className="glass-panel" style={{ borderRadius: '18px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Supervisor</th>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Assigned Department</th>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Assigned Workforce</th>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Status</th>
              <th style={{ padding: '1rem 1.25rem', fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {supervisors.map((sup) => (
              <tr key={sup.user_id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <td style={{ padding: '1rem 1.25rem' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{sup.full_name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{sup.email}</div>
                </td>
                <td style={{ padding: '1rem 1.25rem', fontSize: '0.9rem' }}>
                  {sup.department_name || 'Unassigned'}
                </td>
                <td style={{ padding: '1rem 1.25rem', fontSize: '0.9rem' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{sup.assigned_workers_count ?? '—'}</span> workers
                </td>
                <td style={{ padding: '1rem 1.25rem' }}>
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      padding: '0.25rem 0.6rem',
                      borderRadius: '20px',
                      backgroundColor: sup.status === 'active' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: sup.status === 'active' ? '#10b981' : '#f59e0b',
                    }}
                  >
                    {sup.status.toUpperCase()}
                  </span>
                </td>
                <td style={{ padding: '1rem 1.25rem' }}>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => openEditModal(sup)}
                      style={{ minHeight: '40px', padding: '0 0.9rem', fontSize: '0.8rem' }}
                    >
                      ✏️ Edit
                    </button>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      disabled={busyUserId === sup.user_id}
                      onClick={() => handleToggleAccountStatus(sup)}
                      aria-label={sup.status === 'active' ? `Deactivate account ${sup.email}` : `Reactivate account ${sup.email}`}
                      style={{ minHeight: '40px', padding: '0 0.9rem', fontSize: '0.8rem' }}
                    >
                      {busyUserId === sup.user_id ? '…' : sup.status === 'active' ? '⏸️ Deactivate' : '▶️ Reactivate'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Invite Supervisor Modal Dialog */}
      {showInviteModal && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="sup-modal-title"
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
          <div className="glass-panel" style={{ width: '100%', maxWidth: '480px', padding: '2rem', borderRadius: '24px' }}>
            <h3 id="sup-modal-title" style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: '0.5rem' }}>
              ➕ Invite Supervisor
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
              Send an invitation to a floor operations manager with department management privileges.
            </p>

            <form onSubmit={handleInvite} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                  Full Name
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Elena Rostova"
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
                  placeholder="e.g. elena.rostova@amap.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  style={{ width: '100%', minHeight: '48px' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                  Department Assignment
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
                  {isSubmitting ? 'Sending...' : 'Send Invitation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Supervisor Modal Dialog */}
      {editingSupervisor && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="sup-edit-modal-title"
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
          <div className="glass-panel" style={{ width: '100%', maxWidth: '480px', padding: '2rem', borderRadius: '24px' }}>
            <h3 id="sup-edit-modal-title" style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: '0.5rem' }}>
              ✏️ Edit Supervisor
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
              Update identity and department for {editingSupervisor.full_name}. Changes persist immediately in PostgreSQL.
            </p>

            <form onSubmit={handleUpdateSupervisor} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
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

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
                  Department Assignment
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

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setEditingSupervisor(null)}
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
