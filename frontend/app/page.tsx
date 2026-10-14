'use client';

/**
 * Hybrid Control Interface — Project Overview (/)
 *
 * Polished product overview for capstone demonstration: what the platform is,
 * its capabilities, the three user roles, the end-to-end workflow, and the
 * technical foundation. No authentication required.
 */

import React from 'react';
import Link from 'next/link';

const CAPABILITIES = [
  {
    icon: '🖐️',
    title: 'Gesture Control',
    color: 'var(--worker-cyan)',
    text: 'MediaPipe hand tracking drives a real on-screen cursor — pinch to click, two fingers to scroll, fist for emergency stop.',
  },
  {
    icon: '🎙️',
    title: 'Voice Control',
    color: 'var(--worker-cyan)',
    text: 'Offline Vosk streaming recognition in English and Hindi — every interface action can be spoken.',
  },
  {
    icon: '🔀',
    title: 'Multimodal Interaction',
    color: 'var(--worker-cyan)',
    text: 'Gesture and voice inputs are fused with conflict arbitration, so both channels can work together safely.',
  },
  {
    icon: '🧭',
    title: 'Workflow Execution',
    color: 'var(--org-emerald)',
    text: 'Multi-step digital jobs with server-side authorization, per-step progress, and a final classification decision.',
  },
  {
    icon: '🗂️',
    title: 'Evidence & Dataset Interaction',
    color: 'var(--org-emerald)',
    text: 'Every job is investigated against the organization’s own PostgreSQL records — open, filter, and inspect real evidence.',
  },
  {
    icon: '🛡️',
    title: 'Role-Based Operations',
    color: 'var(--admin-purple)',
    text: 'Worker, Supervisor, and Admin capabilities are enforced server-side — navigation and routes adapt to the signed-in role.',
  },
];

const ROLES = [
  {
    icon: '👷',
    title: 'Worker',
    color: 'var(--worker-cyan)',
    points: [
      'Executes assigned multi-step investigation jobs',
      'Works hands-free with gestures and voice',
      'Inspects linked evidence records',
      'Submits the final classification decision',
    ],
  },
  {
    icon: '🏢',
    title: 'Supervisor',
    color: 'var(--org-emerald)',
    points: [
      'Monitors worker status in real time',
      'Assigns and reassigns jobs',
      'Tracks pending, in-progress and completed work',
      'Responds to assistance and emergency events',
    ],
  },
  {
    icon: '⚙️',
    title: 'Admin',
    color: 'var(--admin-purple)',
    points: [
      'Manages users, roles and departments',
      'Builds workflows and defines steps',
      'Curates organization datasets',
      'Oversees dashboards and audit trails',
    ],
  },
];

const FLOW = [
  'Login',
  'Organization',
  'Role',
  'Workflow / Assignment',
  'Multimodal Execution',
  'Classification / Decision',
  'Persisted Result',
  'Monitoring & Analytics',
];

const TECH = [
  { label: 'Frontend', value: 'Next.js · React · TypeScript' },
  { label: 'Backend', value: 'FastAPI · Python' },
  { label: 'Database', value: 'PostgreSQL / Supabase' },
  { label: 'Gesture Input', value: 'MediaPipe hand tracking' },
  { label: 'Voice Input', value: 'Vosk offline streaming' },
  { label: 'Deployment', value: 'Docker' },
  { label: 'Security', value: 'Role-based access control' },
  { label: 'Timestamps', value: 'UTC storage · IST display' },
];

export default function HomePage() {
  return (
    <main style={{ maxWidth: '1120px', margin: '0 auto', padding: '0 1.5rem 3rem 1.5rem' }}>
      {/* A. Hero */}
      <section
        className="glass-panel"
        style={{
          marginTop: '1.5rem',
          padding: '3rem 2.5rem',
          borderRadius: '24px',
          textAlign: 'center',
          background: 'linear-gradient(135deg, rgba(0, 242, 254, 0.08) 0%, rgba(139, 92, 246, 0.10) 100%)',
        }}
      >
        <span className="badge badge-cyan" style={{ marginBottom: '1rem', fontSize: '0.8rem' }}>
          Accessible Multimodal HCI Platform
        </span>
        <h1 style={{ fontSize: '3rem', fontWeight: 800, letterSpacing: '-0.03em', color: 'white', margin: 0 }}>
          Hybrid Control Interface
        </h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginTop: '0.9rem', maxWidth: '760px', marginInline: 'auto', lineHeight: 1.6 }}>
          An accessibility-oriented multimodal human–computer interface for digital industrial
          workflows — operated by hand gestures and voice, backed by real operational data.
        </p>
        <div style={{ display: 'flex', gap: '0.9rem', justifyContent: 'center', flexWrap: 'wrap', marginTop: '1.9rem' }}>
          <Link href="/login" className="btn btn-primary" style={{ padding: '0.8rem 1.9rem', minHeight: '48px' }}>
            Enter the Platform →
          </Link>
          <Link href="#capabilities" className="btn btn-secondary" style={{ padding: '0.8rem 1.9rem', minHeight: '48px' }}>
            Explore Capabilities
          </Link>
        </div>
      </section>

      {/* B. Platform Capabilities */}
      <section id="capabilities" style={{ marginTop: '2.75rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '1.1rem' }}>Platform Capabilities</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          {CAPABILITIES.map((c) => (
            <div key={c.title} className="glass-panel" style={{ padding: '1.4rem', borderRadius: '18px', borderTop: `3px solid ${c.color}` }}>
              <div style={{ fontSize: '1.7rem' }}>{c.icon}</div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 800, margin: '0.5rem 0 0.4rem 0' }}>{c.title}</h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.55 }}>{c.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* C. User Roles */}
      <section style={{ marginTop: '2.75rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '1.1rem' }}>User Roles</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {ROLES.map((r) => (
            <div key={r.title} className="glass-panel" style={{ padding: '1.4rem', borderRadius: '18px', borderLeft: `4px solid ${r.color}` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <span style={{ fontSize: '1.5rem' }}>{r.icon}</span>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 800, margin: 0, color: r.color }}>{r.title}</h3>
              </div>
              <ul style={{ margin: '0.8rem 0 0 0', padding: 0, listStyle: 'none', display: 'grid', gap: '0.45rem' }}>
                {r.points.map((p) => (
                  <li key={p} style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.5rem' }}>
                    <span aria-hidden="true" style={{ color: r.color }}>•</span>
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* D. Workflow */}
      <section style={{ marginTop: '2.75rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '1.1rem' }}>How a Job Flows</h2>
        <div className="glass-panel" style={{ padding: '1.6rem', borderRadius: '18px' }}>
          <ol
            style={{
              margin: 0,
              padding: 0,
              listStyle: 'none',
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.6rem',
              alignItems: 'center',
            }}
          >
            {FLOW.map((step, i) => (
              <React.Fragment key={step}>
                <li
                  className="badge"
                  style={{
                    fontSize: '0.82rem',
                    fontWeight: 700,
                    padding: '0.55rem 0.9rem',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.06)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                  }}
                >
                  <span style={{ color: 'var(--worker-cyan)', marginRight: '0.4rem' }}>{i + 1}</span>
                  {step}
                </li>
                {i < FLOW.length - 1 && (
                  <li aria-hidden="true" style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    →
                  </li>
                )}
              </React.Fragment>
            ))}
          </ol>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '1.1rem 0 0 0' }}>
            Every state change — assignment, step completion, decision, result, timestamps — is persisted in
            PostgreSQL and survives refresh, restart and re-login.
          </p>
        </div>
      </section>

      {/* E. Technical Summary */}
      <section style={{ marginTop: '2.75rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '1.1rem' }}>Technical Foundation</h2>
        <div className="glass-panel" style={{ padding: '1.4rem 1.6rem', borderRadius: '18px' }}>
          <dl style={{ margin: 0, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.9rem 1.5rem' }}>
            {TECH.map((t) => (
              <div key={t.label} style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                <dt style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', fontWeight: 700 }}>
                  {t.label}
                </dt>
                <dd style={{ margin: 0, fontSize: '0.92rem', color: 'var(--text-primary)', fontWeight: 600 }}>{t.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <footer style={{ marginTop: '2.75rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
        Hybrid Control Interface — accessible multimodal operation of digital industrial workflows.
        <span style={{ display: 'block', marginTop: '0.4rem', opacity: 0.8 }}>
          Build {process.env.NEXT_PUBLIC_BUILD_INFO || 'dev'}
        </span>
      </footer>
    </main>
  );
}
