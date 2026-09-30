-- ====================================================================
-- AMAP Database Seed Data
-- Product Five-Organization Scenarios:
--   1. Acme Motors — Assembly Plant 1 (Automotive / Manufacturing)
--   2. MediCare Health Systems (Healthcare)
--   3. Nexa Finance (Finance)
--   4. LogiCore Logistics (Logistics)
--   5. BrightGrid Energy (Energy / Utilities)
-- Populates: Organizations, Departments, Users, Roles, Permissions,
-- Worker Profiles, Jobs, Workflows, Steps, Tasks, Presets & Personalizations
-- ====================================================================

-- 1. Organization (Acme Motors — the original demo organization)
INSERT INTO organizations (id, name, status)
VALUES ('9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Acme Motors — Assembly Plant 1', 'active')
ON CONFLICT (id) DO NOTHING;

-- 1a. The other four product organizations. Each gets its own departments,
-- core users (admin + 2 supervisors + 3 workers), worker profiles, and one
-- interaction preset. The role->permission matrix (section 5) and the
-- gesture->action mappings (section 11b) CROSS JOIN all organizations, so
-- they propagate to these organizations automatically. Default password for
-- all seeded users: SecurePassword123! (same hash as section 6).
INSERT INTO organizations (id, name, status, organization_type, industry, location, contact_email)
VALUES
    ('aa100000-0000-0000-0000-000000000002', 'MediCare Health Systems', 'active', 'enterprise', 'Healthcare', 'Boston, MA', 'contact@medicare-health.com'),
    ('aa100000-0000-0000-0000-000000000003', 'Nexa Finance', 'active', 'enterprise', 'Financial Services', 'New York, NY', 'contact@nexafinance.com'),
    ('aa100000-0000-0000-0000-000000000004', 'LogiCore Logistics', 'active', 'enterprise', 'Logistics & Supply Chain', 'Rotterdam, NL', 'contact@logicore-logistics.com'),
    ('aa100000-0000-0000-0000-000000000005', 'BrightGrid Energy', 'active', 'enterprise', 'Energy & Utilities', 'Austin, TX', 'contact@brightgrid-energy.com')
ON CONFLICT (id) DO NOTHING;

-- 1b. Industry-specific departments (business terminology per organization)
INSERT INTO departments (id, organization_id, name, status)
VALUES
    -- MediCare Health Systems (Healthcare)
    ('ab200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'Patient Records & Documentation', 'active'),
    ('ab200000-0000-0000-0000-000000000002', 'aa100000-0000-0000-0000-000000000002', 'Compliance & Verification', 'active'),
    ('ab200000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000002', 'Clinical Operations Support', 'active'),
    -- Nexa Finance (Financial Services)
    ('ab300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'Transaction Monitoring', 'active'),
    ('ab300000-0000-0000-0000-000000000002', 'aa100000-0000-0000-0000-000000000003', 'Risk & Compliance', 'active'),
    ('ab300000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000003', 'Customer Case Management', 'active'),
    -- LogiCore Logistics (Logistics & Supply Chain)
    ('ab400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'Shipment Operations', 'active'),
    ('ab400000-0000-0000-0000-000000000002', 'aa100000-0000-0000-0000-000000000004', 'Exception Management', 'active'),
    ('ab400000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000004', 'Tracking & Customer Service', 'active'),
    -- BrightGrid Energy (Energy & Utilities)
    ('ab500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'Grid Operations', 'active'),
    ('ab500000-0000-0000-0000-000000000002', 'aa100000-0000-0000-0000-000000000005', 'Field Service & Maintenance', 'active'),
    ('ab500000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000005', 'Incident Management', 'active')
ON CONFLICT (id) DO NOTHING;

-- 1c. Core users per organization (1 admin, 2 supervisors, 3 workers each).
-- Full populations (5-10 supervisors, 15-20 workers) are grown in Phase 6.
INSERT INTO users (id, organization_id, email, full_name, password_hash, status)
VALUES
    -- MediCare Health Systems
    ('ac200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'admin@medicare-health.com', 'Elena Vasquez (Admin)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac200000-0000-0000-0000-000000000002', 'aa100000-0000-0000-0000-000000000002', 'supervisor1@medicare-health.com', 'Rachel Kim (Supervisor)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac200000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000002', 'supervisor2@medicare-health.com', 'Tom Nguyen (Supervisor)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac200000-0000-0000-0000-000000000004', 'aa100000-0000-0000-0000-000000000002', 'worker1@medicare-health.com', 'Ava Patel (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac200000-0000-0000-0000-000000000005', 'aa100000-0000-0000-0000-000000000002', 'worker2@medicare-health.com', 'Ben Carter (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac200000-0000-0000-0000-000000000006', 'aa100000-0000-0000-0000-000000000002', 'worker3@medicare-health.com', 'Grace Liu (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    -- Nexa Finance
    ('ac300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'admin@nexafinance.com', 'Marcus Chen (Admin)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac300000-0000-0000-0000-000000000002', 'aa100000-0000-0000-0000-000000000003', 'supervisor1@nexafinance.com', 'Diana Ruiz (Supervisor)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac300000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000003', 'supervisor2@nexafinance.com', 'Omar Farouk (Supervisor)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac300000-0000-0000-0000-000000000004', 'aa100000-0000-0000-0000-000000000003', 'worker1@nexafinance.com', 'Lily Zhang (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac300000-0000-0000-0000-000000000005', 'aa100000-0000-0000-0000-000000000003', 'worker2@nexafinance.com', 'Noah Brooks (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac300000-0000-0000-0000-000000000006', 'aa100000-0000-0000-0000-000000000003', 'worker3@nexafinance.com', 'Maya Iyer (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    -- LogiCore Logistics
    ('ac400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'admin@logicore-logistics.com', 'Sofia Rossi (Admin)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac400000-0000-0000-0000-000000000002', 'aa100000-0000-0000-0000-000000000004', 'supervisor1@logicore-logistics.com', 'James Park (Supervisor)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac400000-0000-0000-0000-000000000004', 'aa100000-0000-0000-0000-000000000004', 'worker1@logicore-logistics.com', 'Ethan Walsh (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac400000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000004', 'supervisor2@logicore-logistics.com', 'Fatima Ali (Supervisor)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac400000-0000-0000-0000-000000000005', 'aa100000-0000-0000-0000-000000000004', 'worker2@logicore-logistics.com', 'Zoe Adams (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac400000-0000-0000-0000-000000000006', 'aa100000-0000-0000-0000-000000000004', 'worker3@logicore-logistics.com', 'Karan Mehta (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    -- BrightGrid Energy
    ('ac500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'admin@brightgrid-energy.com', 'David Okafor (Admin)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac500000-0000-0000-0000-000000000002', 'aa100000-0000-0000-0000-000000000005', 'supervisor1@brightgrid-energy.com', 'Hannah Schmidt (Supervisor)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac500000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000005', 'supervisor2@brightgrid-energy.com', 'Raj Patel (Supervisor)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac500000-0000-0000-0000-000000000004', 'aa100000-0000-0000-0000-000000000005', 'worker1@brightgrid-energy.com', 'Chloe Dubois (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac500000-0000-0000-0000-000000000005', 'aa100000-0000-0000-0000-000000000005', 'worker2@brightgrid-energy.com', 'Sam Rivera (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('ac500000-0000-0000-0000-000000000006', 'aa100000-0000-0000-0000-000000000005', 'worker3@brightgrid-energy.com', 'Ana Kowalski (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active')
ON CONFLICT (id) DO NOTHING;

-- 1e. Worker profiles for the new organizations' workers
INSERT INTO worker_profiles (id, user_id)
VALUES
    ('ad200000-0000-0000-0000-000000000001', 'ac200000-0000-0000-0000-000000000004'),
    ('ad200000-0000-0000-0000-000000000002', 'ac200000-0000-0000-0000-000000000005'),
    ('ad200000-0000-0000-0000-000000000003', 'ac200000-0000-0000-0000-000000000006'),
    ('ad300000-0000-0000-0000-000000000001', 'ac300000-0000-0000-0000-000000000004'),
    ('ad300000-0000-0000-0000-000000000002', 'ac300000-0000-0000-0000-000000000005'),
    ('ad300000-0000-0000-0000-000000000003', 'ac300000-0000-0000-0000-000000000006'),
    ('ad400000-0000-0000-0000-000000000001', 'ac400000-0000-0000-0000-000000000004'),
    ('ad400000-0000-0000-0000-000000000002', 'ac400000-0000-0000-0000-000000000005'),
    ('ad400000-0000-0000-0000-000000000003', 'ac400000-0000-0000-0000-000000000006'),
    ('ad500000-0000-0000-0000-000000000001', 'ac500000-0000-0000-0000-000000000004'),
    ('ad500000-0000-0000-0000-000000000002', 'ac500000-0000-0000-0000-000000000005'),
    ('ad500000-0000-0000-0000-000000000003', 'ac500000-0000-0000-0000-000000000006')
ON CONFLICT (id) DO NOTHING;

-- 1f. One interaction preset per new organization. Section 11b CROSS JOINs
-- every preset, so the full gesture->action mapping is attached automatically.
INSERT INTO interaction_configurations (id, organization_id, name, description, status)
VALUES
    ('80000000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000002', 'MediCare Standard Accessibility Preset', 'Default multimodal configuration for healthcare documentation work', 'active'),
    ('80000000-0000-0000-0000-000000000004', 'aa100000-0000-0000-0000-000000000003', 'Nexa Standard Accessibility Preset', 'Default multimodal configuration for financial case analysis', 'active'),
    ('80000000-0000-0000-0000-000000000005', 'aa100000-0000-0000-0000-000000000004', 'LogiCore Standard Accessibility Preset', 'Default multimodal configuration for shipment exception handling', 'active'),
    ('80000000-0000-0000-0000-000000000006', 'aa100000-0000-0000-0000-000000000005', 'BrightGrid Standard Accessibility Preset', 'Default multimodal configuration for grid incident analysis', 'active')
ON CONFLICT (id) DO NOTHING;

-- 1g. Capability + personalization profiles for the new workers (same shape
-- as the Acme workers, so every seeded worker behaves identically).
INSERT INTO worker_capability_profiles (worker_profile_id, capability_data, status)
VALUES
    ('ad200000-0000-0000-0000-000000000001', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad200000-0000-0000-0000-000000000002', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad200000-0000-0000-0000-000000000003', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad300000-0000-0000-0000-000000000001', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad300000-0000-0000-0000-000000000002', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad300000-0000-0000-0000-000000000003', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad400000-0000-0000-0000-000000000001', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad400000-0000-0000-0000-000000000002', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad400000-0000-0000-0000-000000000003', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad500000-0000-0000-0000-000000000001', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad500000-0000-0000-0000-000000000002', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active'),
    ('ad500000-0000-0000-0000-000000000003', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active')
ON CONFLICT (worker_profile_id) DO NOTHING;

INSERT INTO worker_personalizations (worker_profile_id, interaction_configuration_id, personalization_data, status)
VALUES
    ('ad200000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000003', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad200000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000003', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad200000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000003', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad300000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000004', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad300000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000004', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad300000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000004', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad400000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000005', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad400000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000005', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad400000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000005', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad500000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000006', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad500000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000006', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('ad500000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000006', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active')
ON CONFLICT (worker_profile_id) DO NOTHING;


-- 2. Departments
INSERT INTO departments (id, organization_id, name, status)
VALUES
    ('11111111-1111-1111-1111-111111111111', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Powertrain & Gearbox Integration', 'active'),
    ('22222222-2222-2222-2222-222222222222', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Chassis & Structural Welding', 'active'),
    ('33333333-3333-3333-3333-333333333333', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Quality Control & Diagnostics', 'active')
ON CONFLICT (id) DO NOTHING;

-- 3. Roles
INSERT INTO roles (id, name, description)
VALUES
    ('a0000000-0000-0000-0000-000000000001', 'admin', 'System administrator with full organizational governance'),
    ('a0000000-0000-0000-0000-000000000002', 'supervisor', 'Floor supervisor managing line workers and assistance queue'),
    ('a0000000-0000-0000-0000-000000000003', 'worker', 'Assembly line technician operating accessible multimodal workstations'),
    ('a0000000-0000-0000-0000-000000000004', 'organization_admin', 'Organization administrator governing users, departments, and workflows within their organization')
ON CONFLICT (id) DO NOTHING;

-- 4. Permissions
INSERT INTO permissions (id, name, description)
VALUES
    ('b0000000-0000-0000-0000-000000000001', 'session:read', 'Read active session telemetry'),
    ('b0000000-0000-0000-0000-000000000002', 'session:write', 'Start, pause, and advance work sessions'),
    ('b0000000-0000-0000-0000-000000000003', 'multimodal:input', 'Submit gesture and voice multimodal frames'),
    ('b0000000-0000-0000-0000-000000000004', 'assistance:request', 'Trigger supervisor assistance calls'),
    ('b0000000-0000-0000-0000-000000000005', 'assistance:resolve', 'Claim and resolve assistance tickets'),
    ('b0000000-0000-0000-0000-000000000006', 'admin:config', 'Configure station interaction presets and audit logs')
ON CONFLICT (id) DO NOTHING;

-- 5. Role Permissions (organization-scoped since migration 047)
INSERT INTO role_permissions (organization_id, role_id, permission_id)
SELECT org.id, v.role_id, v.permission_id
FROM (
    VALUES
        ('a0000000-0000-0000-0000-000000000001'::uuid, 'b0000000-0000-0000-0000-000000000001'::uuid),
        ('a0000000-0000-0000-0000-000000000001'::uuid, 'b0000000-0000-0000-0000-000000000006'::uuid),
        ('a0000000-0000-0000-0000-000000000002'::uuid, 'b0000000-0000-0000-0000-000000000001'::uuid),
        ('a0000000-0000-0000-0000-000000000002'::uuid, 'b0000000-0000-0000-0000-000000000005'::uuid),
        ('a0000000-0000-0000-0000-000000000003'::uuid, 'b0000000-0000-0000-0000-000000000001'::uuid),
        ('a0000000-0000-0000-0000-000000000003'::uuid, 'b0000000-0000-0000-0000-000000000002'::uuid),
        ('a0000000-0000-0000-0000-000000000003'::uuid, 'b0000000-0000-0000-0000-000000000003'::uuid),
        ('a0000000-0000-0000-0000-000000000003'::uuid, 'b0000000-0000-0000-0000-000000000004'::uuid),
        ('a0000000-0000-0000-0000-000000000004'::uuid, 'b0000000-0000-0000-0000-000000000001'::uuid),
        ('a0000000-0000-0000-0000-000000000004'::uuid, 'b0000000-0000-0000-0000-000000000005'::uuid),
        ('a0000000-0000-0000-0000-000000000004'::uuid, 'b0000000-0000-0000-0000-000000000006'::uuid)
) AS v(role_id, permission_id)
CROSS JOIN organizations AS org
ON CONFLICT DO NOTHING;

-- 6. Users (Default Password for all: SecurePassword123!)
-- Hash: pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9
-- NOTE: maria.newhire@amap.com is the Fresher (new hire) demo account
-- referenced by the login screen. It MUST exist for fresher login to work.
INSERT INTO users (id, organization_id, email, full_name, password_hash, status)
VALUES
    ('c0000000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'admin@amap.com', 'Sarah Jenkins (Admin)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('c0000000-0000-0000-0000-000000000002', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'supervisor@amap.com', 'Marcus Vance (Supervisor)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('c0000000-0000-0000-0000-000000000003', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'alex.worker@amap.com', 'Alex Morgan (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('c0000000-0000-0000-0000-000000000004', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'jordan.worker@amap.com', 'Jordan Lee (Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active'),
    ('c0000000-0000-0000-0000-000000000005', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'maria.newhire@amap.com', 'Maria Rodriguez (Fresher Worker)', 'pbkdf2_sha256$600000$bc5ab92aba13d70295b07ec1b9619ccc$10df13a62e551e5879a3d5829abbd57ba89f49d25c78d936f2a426309971e3d9', 'active')
ON CONFLICT (id) DO NOTHING;

-- 7. User Roles Assignments
INSERT INTO user_roles (user_id, role_id)
VALUES
    ('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001'),
    ('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000004'),
    ('c0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002'),
    ('c0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000003'),
    ('c0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000003'),
    ('c0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000003')
ON CONFLICT DO NOTHING;

-- 7a. Role assignments for the additional organizations (roles from section 3) (admins carry both admin and
-- organization_admin, mirroring the Acme admin; supervisors/workers likewise).
INSERT INTO user_roles (user_id, role_id)
VALUES
    ('ac200000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001'),
    ('ac200000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000004'),
    ('ac200000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002'),
    ('ac200000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000002'),
    ('ac200000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000003'),
    ('ac200000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000003'),
    ('ac200000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000003'),
    ('ac300000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001'),
    ('ac300000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000004'),
    ('ac300000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002'),
    ('ac300000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000002'),
    ('ac300000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000003'),
    ('ac300000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000003'),
    ('ac300000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000003'),
    ('ac400000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001'),
    ('ac400000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000004'),
    ('ac400000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002'),
    ('ac400000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000002'),
    ('ac400000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000003'),
    ('ac400000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000003'),
    ('ac400000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000003'),
    ('ac500000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001'),
    ('ac500000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000004'),
    ('ac500000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002'),
    ('ac500000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000002'),
    ('ac500000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000003'),
    ('ac500000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000003'),
    ('ac500000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000003')
ON CONFLICT DO NOTHING;

-- 8. Worker Profiles
INSERT INTO worker_profiles (id, user_id)
VALUES
    ('d0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000003'),
    ('d0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000004'),
    ('d0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000005')
ON CONFLICT (id) DO NOTHING;

-- 11. Interaction Configurations
INSERT INTO interaction_configurations (id, organization_id, name, description, status)
VALUES
    ('80000000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Powertrain High-Noise Preset', 'Default configuration for noisy industrial floors', 'active'),
    ('80000000-0000-0000-0000-000000000002', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Motor Diversity Enhanced Dwell Preset', 'Configuration with extended dwell times for motor accessibility', 'active')
ON CONFLICT (id) DO NOTHING;

-- 11a. Canonical Actions (MUST precede 11b: the gesture mappings reference
-- these action rows by id; on a fresh database they do not exist yet,
-- which aborted the whole seed and left zero users -> broken logins.)
INSERT INTO actions (id, name, display_name, description, category, status)
VALUES
    ('40000000-0000-0000-0000-000000000001', 'next_step', 'Next Step', 'Advance to the next workflow step', 'workflow', 'active'),
    ('40000000-0000-0000-0000-000000000002', 'confirm_action', 'Confirm Step Action', 'Confirm and complete current step action', 'workflow', 'active'),
    ('40000000-0000-0000-0000-000000000003', 'previous_step', 'Previous Step', 'Navigate back to the previous workflow step', 'navigation', 'active'),
    ('40000000-0000-0000-0000-000000000004', 'pause_session', 'Pause Work Session', 'Temporarily pause active workstation assembly', 'system', 'active'),
    ('40000000-0000-0000-0000-000000000005', 'resume_session', 'Resume Work Session', 'Resume paused workstation assembly', 'system', 'active'),
    ('40000000-0000-0000-0000-000000000006', 'emergency_stop', 'Emergency Stop', 'Software safety stop interlock and supervisor dispatch', 'system', 'active'),
    ('40000000-0000-0000-0000-000000000007', 'request_assistance', 'Request Assistance', 'Request floor supervisor assistance ticket', 'assistance', 'active')
ON CONFLICT (name) DO NOTHING;

-- 11b. Default gesture -> action mappings for the seeded interaction presets
-- (migration 052 seeds these too, but on a fresh database it runs before the
-- presets exist, so the seed guarantees them once presets are created).
-- gesture_configurations is preset-scoped; worker-level overrides live in
-- worker_personalizations.personalization_data.gesture_action_map.
INSERT INTO gesture_configurations (interaction_configuration_id, gesture_name, action_id, is_enabled, confidence_threshold)
SELECT preset.id, g.gesture_name, g.action_id, TRUE, g.confidence
FROM (
    VALUES
        ('pinch',           '40000000-0000-0000-0000-000000000011'::uuid, 0.75),
        ('pinch_hold',      '40000000-0000-0000-0000-000000000022'::uuid, 0.75),
        ('two_finger',      '40000000-0000-0000-0000-000000000012'::uuid, 0.80),
        ('two_finger_move', '40000000-0000-0000-0000-000000000019'::uuid, 0.75),
        ('swipe_up',        '40000000-0000-0000-0000-000000000017'::uuid, 0.80),
        ('swipe_down',      '40000000-0000-0000-0000-000000000018'::uuid, 0.80),
        ('swipe_left',      '40000000-0000-0000-0000-000000000003'::uuid, 0.80),
        ('swipe_right',     '40000000-0000-0000-0000-000000000001'::uuid, 0.80),
        ('thumbs_up',       '40000000-0000-0000-0000-000000000002'::uuid, 0.78),
        ('thumbs_down',     '40000000-0000-0000-0000-000000000026'::uuid, 0.78),
        ('open_palm',       '40000000-0000-0000-0000-000000000004'::uuid, 0.82),
        ('fist',            '40000000-0000-0000-0000-000000000006'::uuid, 0.75)
) AS g(gesture_name, action_id, confidence)
CROSS JOIN interaction_configurations AS preset
ON CONFLICT (interaction_configuration_id, gesture_name) DO NOTHING;

-- 9. Worker Personalization & Capability Profiles
INSERT INTO worker_capability_profiles (worker_profile_id, capability_data, status)
VALUES
    ('d0000000-0000-0000-0000-000000000001', '{"preferred_modality": "multimodal", "has_motor_tremor": true, "has_speech_diversity": false}'::jsonb, 'active'),
    ('d0000000-0000-0000-0000-000000000002', '{"preferred_modality": "gesture", "has_motor_tremor": false, "has_speech_diversity": true}'::jsonb, 'active'),
    ('d0000000-0000-0000-0000-000000000003', '{"preferred_modality": "multimodal", "has_motor_tremor": false, "has_speech_diversity": false}'::jsonb, 'active')
ON CONFLICT (worker_profile_id) DO NOTHING;

INSERT INTO worker_personalizations (worker_profile_id, interaction_configuration_id, personalization_data, status)
VALUES
    ('d0000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', '{"dwell_time_ms": 650, "hitbox_scaling_factor": 1.25, "voice_noise_gate_db": 14.0, "is_auto_adapted": true}'::jsonb, 'active'),
    ('d0000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000002', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 18.0, "is_auto_adapted": false}'::jsonb, 'active'),
    ('d0000000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000002', '{"dwell_time_ms": 500, "hitbox_scaling_factor": 1.00, "voice_noise_gate_db": 16.0, "is_auto_adapted": false}'::jsonb, 'active')
ON CONFLICT (worker_profile_id) DO NOTHING;

-- 10. Workflows & Assembly Steps
INSERT INTO workflows (id, organization_id, name, description, status)
VALUES
    ('e0000000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Inverter Sub-Assembly Alpha', 'Precision power electronics mounting and high-voltage busbar torque sequence', 'active')
ON CONFLICT (id) DO NOTHING;

INSERT INTO workflow_steps (id, workflow_id, step_order, name, description, status)
VALUES
    ('f0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 1, 'Optical Component Inspection', 'Verify thermal paste application and capacitor polarity on PCB bed.', 'active'),
    ('f0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000001', 2, 'Primary Busbar Torquing', 'Align copper busbar and torque M6 fasteners to 9.2 Nm in star pattern.', 'active'),
    ('f0000000-0000-0000-0000-000000000003', 'e0000000-0000-0000-0000-000000000001', 3, 'High Voltage Isolation Check', 'Connect dielectric probe to safety terminal and engage automated 500V test.', 'active')
ON CONFLICT (id) DO NOTHING;

-- 12. Active Work Session & Open Assistance Ticket
INSERT INTO work_sessions (id, organization_id, worker_profile_id, status, started_at)
VALUES
    ('90000000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'd0000000-0000-0000-0000-000000000001', 'active', CURRENT_TIMESTAMP)
ON CONFLICT (id) DO NOTHING;

INSERT INTO assistance_requests (id, organization_id, worker_profile_id, status, priority, reason)
VALUES
    ('70000000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'd0000000-0000-0000-0000-000000000001', 'open', 'high', 'Dielectric probe calibration error on step 3.')
ON CONFLICT (id) DO NOTHING;

-- 14. Assembly Task & Workflow Link
INSERT INTO tasks (id, organization_id, name, description, status)
VALUES
    ('50000000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Inverter Alpha Assembly', 'Power inverter electronics mounting and busbar torque sequence', 'active')
ON CONFLICT (id) DO NOTHING;

INSERT INTO task_workflows (task_id, workflow_id)
VALUES
    ('50000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001')
ON CONFLICT (task_id, workflow_id) DO NOTHING;

-- 15. Initial Worker Task Assignment & Workflow Assignment
INSERT INTO worker_task_assignments (id, task_id, worker_profile_id, status)
VALUES
    ('61000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'assigned'),
    ('61000000-0000-0000-0000-000000000002', '50000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000003', 'assigned')
ON CONFLICT (id) DO NOTHING;

INSERT INTO workflow_assignments (id, workflow_id, worker_profile_id, status)
VALUES
    ('60000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'assigned')
ON CONFLICT (id) DO NOTHING;

-- 16. Worker Readiness (persisted onboarding lifecycle state)
INSERT INTO worker_readiness (
    worker_profile_id, is_fresher, onboarding_completed, readiness_status,
    interaction_mode, gesture_ready, voice_ready, multimodal_ready,
    task_training_complete, overall_ready, completed_stages, active_preferences
)
VALUES
    (
        'd0000000-0000-0000-0000-000000000001', FALSE, TRUE, 'ready',
        'multimodal', TRUE, TRUE, TRUE,
        TRUE, TRUE,
        '["language", "accessibility", "gesture_calibration", "voice_setup", "training"]'::jsonb,
        '{"language": "en", "modality": "multimodal", "dwell_time_ms": 500, "high_contrast": false, "text_scale": 1.0}'::jsonb
    ),
    (
        'd0000000-0000-0000-0000-000000000002', TRUE, FALSE, 'incomplete',
        'multimodal', FALSE, FALSE, FALSE,
        FALSE, FALSE,
        '[]'::jsonb,
        '{"language": "en", "modality": "multimodal", "dwell_time_ms": 500, "high_contrast": false, "text_scale": 1.0}'::jsonb
    ),
    (
        'd0000000-0000-0000-0000-000000000003', TRUE, FALSE, 'incomplete',
        'multimodal', FALSE, FALSE, FALSE,
        FALSE, FALSE,
        '[]'::jsonb,
        '{"language": "en", "modality": "multimodal", "dwell_time_ms": 500, "high_contrast": false, "text_scale": 1.0}'::jsonb
    )
ON CONFLICT (worker_profile_id) DO NOTHING;

-- ============================================================================
-- 17. Sample Datasets, Evidence Records & Data-Backed Investigation Tasks
-- (synthetic sample data — NOT real company data; deterministic IDs, safe to
--  re-run: every statement is ON CONFLICT DO NOTHING)
-- ============================================================================

-- 17a. Datasets (one per organization, organization-scoped)
INSERT INTO datasets (id, organization_id, name, description, domain, status)
VALUES
    ('ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Powertrain Quality Tracer — Line 3', 'Synthetic sample dataset: production, inspection, maintenance and incident records for gearbox housing batches on Line 3.', 'manufacturing_quality', 'active'),
    ('ba200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'Ward 4 Post-Operative Monitoring File', 'Synthetic sample dataset: post-operative vitals, medication, lab and nursing records for Ward 4.', 'healthcare', 'active'),
    ('ba300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'Card Dispute & Fraud Alert File — NXC-4471', 'Synthetic sample dataset: card transactions, fraud alerts and customer profile for account NXC-4471.', 'financial_services', 'active'),
    ('ba400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'Route 7 Exception File — Rotterdam Hub', 'Synthetic sample dataset: shipments, scans, incidents and driver reports for Route 7.', 'logistics', 'active'),
    ('ba500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'Substation F-12 Feeder Monitoring File', 'Synthetic sample dataset: sensor readings, outage tickets, maintenance logs and SCADA alarms for feeder F-12.', 'energy_utilities', 'active')
ON CONFLICT (id) DO NOTHING;

-- 17b. Dataset records — Acme Motors (interconnected: inspections/incidents
--      reference their production batch or maintenance record)
INSERT INTO dataset_records (id, dataset_id, organization_id, record_type, title, source_ref, payload, occurred_at, related_record_id)
VALUES
    ('bb100000-0000-0000-0000-000000000001', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'production', 'Production Run BR-2026-0917 — Gearbox Housing Batch', 'BR-2026-0917',
     '{"line": "Line 3", "machine": "CNC-7", "units_produced": 480, "shift": "B", "material_lot": "AL-6061-Lot-77", "bearing_lot": "SL-8821", "program": "GH-2000-rev4", "operator_note": "Spindle load spikes flagged at 03:10"}'::jsonb,
     '2026-09-26 02:00:00+00', NULL),
    ('bb100000-0000-0000-0000-000000000002', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'production', 'Production Run BR-2026-0916 — Baseline Batch', 'BR-2026-0916',
     '{"line": "Line 3", "machine": "CNC-7", "units_produced": 480, "shift": "B", "material_lot": "AL-6061-Lot-77", "bearing_lot": "SL-8814", "program": "GH-2000-rev4", "result": "passed_all_gates"}'::jsonb,
     '2026-09-25 02:00:00+00', NULL),
    ('bb100000-0000-0000-0000-000000000003', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'inspection', 'Final Noise & Vibration Gate — BR-2026-0917', 'INSP-NV-0917',
     '{"result": "fail", "units_tested": 60, "units_failed": 38, "spec_limit_db": 72.0, "measured_avg_db": 84.4, "noise_excess_db": 12.4, "failure_mode": "gear whine, 2nd order"}'::jsonb,
     '2026-09-26 22:00:00+00', 'bb100000-0000-0000-0000-000000000001'),
    ('bb100000-0000-0000-0000-000000000004', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'inspection', 'In-Process Dimensional Check — Bearing Bores', 'INSP-DIM-0917',
     '{"result": "fail", "sample_size": 12, "out_of_tolerance": 5, "bore_diameter_mm": {"nominal": 62.000, "tolerance": 0.015, "measured_max": 62.052}}'::jsonb,
     '2026-09-26 10:00:00+00', 'bb100000-0000-0000-0000-000000000001'),
    ('bb100000-0000-0000-0000-000000000005', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'inspection', 'Final Noise & Vibration Gate — BR-2026-0916 (Baseline)', 'INSP-NV-0916',
     '{"result": "pass", "units_tested": 60, "units_failed": 0, "spec_limit_db": 72.0, "measured_avg_db": 69.8}'::jsonb,
     '2026-09-25 22:00:00+00', 'bb100000-0000-0000-0000-000000000002'),
    ('bb100000-0000-0000-0000-000000000006', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'maintenance', 'CNC-7 Spindle Service — Vibration Warning', 'WO-3391',
     '{"equipment": "CNC-7", "finding": "spindle bearing wear; vibration 4.8 mm/s (alarm at 4.5)", "action": "bearings replaced, 2h run-in completed", "status": "closed"}'::jsonb,
     '2026-09-22 08:00:00+00', NULL),
    ('bb100000-0000-0000-0000-000000000007', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'maintenance', 'Torque Tool T-14 Calibration Audit', 'CAL-T14-2026-09',
     '{"equipment": "T-14", "finding": "calibration 6 weeks overdue", "torque_deviation_pct": 4.2, "status": "corrective_action_open"}'::jsonb,
     '2026-09-20 13:00:00+00', NULL),
    ('bb100000-0000-0000-0000-000000000008', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'supply_chain', 'Incoming Inspection — Bearing Lot SL-8821', 'INSP-SUP-8821',
     '{"supplier": "Sample Bearing Supplier Co. (synthetic)", "lot": "SL-8821", "sampled": 20, "hardness_check": "marginal_low_on_3_samples", "disposition": "accepted_with_deviation"}'::jsonb,
     '2026-09-24 11:00:00+00', 'bb100000-0000-0000-0000-000000000001'),
    ('bb100000-0000-0000-0000-000000000009', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'incident', 'End-of-Line Test Bench Noise Complaint', 'INC-2026-0451',
     '{"source": "test bench operator", "complaint": "gear whine on 9 of 12 units sampled from BR-2026-0917", "severity": "high", "state": "open"}'::jsonb,
     '2026-09-27 09:15:00+00', 'bb100000-0000-0000-0000-000000000003'),
    ('bb100000-0000-0000-0000-000000000010', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'incident', 'Line 3 Unplanned Stoppage', 'INC-2026-0452',
     '{"equipment": "CNC-7", "duration_min": 47, "cause_code": "mechanical_fault", "note": "alarm cluster four days after spindle service"}'::jsonb,
     '2026-09-27 14:40:00+00', 'bb100000-0000-0000-0000-000000000006'),
    ('bb100000-0000-0000-0000-000000000011', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'production', 'Paint Shop Run PA-2026-0830 — Housing Batch', 'PA-2026-0830',
     '{"booth": "PB-2", "units": 300, "pretreatment_bath": "PT-04", "cure_oven": "OV-3", "paint_lot": "PL-1188"}'::jsonb,
     '2026-08-30 06:00:00+00', NULL),
    ('bb100000-0000-0000-0000-000000000012', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'inspection', 'Paint Adhesion Cross-Cut Test — PA-2026-0830', 'INSP-PA-0830',
     '{"result": "fail", "samples": 8, "failed": 6, "cross_cut_rating": "1 (spec: >= 3)"}'::jsonb,
     '2026-08-31 10:00:00+00', 'bb100000-0000-0000-0000-000000000011'),
    ('bb100000-0000-0000-0000-000000000013', 'ba100000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'incident', 'Paint Booth PT-04 Filter Alarm', 'INC-2026-0431',
     '{"alarm": "low airflow", "action": "filter change deferred to next maintenance window"}'::jsonb,
     '2026-08-29 21:30:00+00', 'bb100000-0000-0000-0000-000000000011')
ON CONFLICT (id) DO NOTHING;

-- 17c. Dataset records — MediCare Health Systems
INSERT INTO dataset_records (id, dataset_id, organization_id, record_type, title, source_ref, payload, occurred_at, related_record_id)
VALUES
    ('bb200000-0000-0000-0000-000000000001', 'ba200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'patient_vitals', 'Vitals Trend — Bed 7 (Post-Op Day 2)', 'VITALS-BED7',
     '{"heart_rate_bpm_trend": [88, 94, 101, 108], "bp_mmhg": "138/86 rising to 152/94", "temp_c": 37.9, "spo2_pct": 94, "trend": "worsening"}'::jsonb,
     '2026-09-29 05:00:00+00', NULL),
    ('bb200000-0000-0000-0000-000000000002', 'ba200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'medication_administration', 'Medication Administration Record — Bed 7', 'MAR-BED7',
     '{"medications": [{"name": "Sample-Abx-500", "time": "04:30"}, {"name": "Sample-Analgesic", "time": "02:15"}], "administered_by": "Nurse R-2 (sample)"}'::jsonb,
     '2026-09-29 04:30:00+00', NULL),
    ('bb200000-0000-0000-0000-000000000003', 'ba200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'lab_result', 'Morning Lab Panel — Bed 7', 'LAB-2026-0929-B7',
     '{"wbc_10_9_per_l": 13.8, "crp_mg_l": 48, "lactate_mmol_l": 2.1, "flag": "elevated_wbc"}'::jsonb,
     '2026-09-29 06:10:00+00', NULL),
    ('bb200000-0000-0000-0000-000000000004', 'ba200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'nursing_note', 'Nursing Observation Note — Bed 7', 'NOTE-BED7-0929',
     '{"note": "Patient reports dizziness on standing; surgical dressing site slightly red"}'::jsonb,
     '2026-09-29 03:50:00+00', NULL),
    ('bb200000-0000-0000-0000-000000000005', 'ba200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'shift_handover', 'Night-to-Day Shift Handover — Ward 4', 'HANDOVER-040',
     '{"summary": "Bed 7 vitals trending up; surgeon informed; monitoring frequency increased"}'::jsonb,
     '2026-09-29 07:00:00+00', NULL)
ON CONFLICT (id) DO NOTHING;

-- 17d. Dataset records — Nexa Finance
INSERT INTO dataset_records (id, dataset_id, organization_id, record_type, title, source_ref, payload, occurred_at, related_record_id)
VALUES
    ('bb300000-0000-0000-0000-000000000001', 'ba300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'transaction', 'Transaction T-99182 — Online Electronics Purchase', 'T-99182',
     '{"amount_usd": 1849.00, "merchant": "Sample Electronics Retailer", "channel": "online", "geo": "Frankfurt, DE", "status": "settled"}'::jsonb,
     '2026-09-28 21:14:00+00', NULL),
    ('bb300000-0000-0000-0000-000000000002', 'ba300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'transaction', 'Transaction T-99204 — Online Luxury Goods Purchase', 'T-99204',
     '{"amount_usd": 2650.00, "merchant": "Sample Luxury Outlet", "channel": "online", "geo": "Bucharest, RO", "status": "declined_3ds"}'::jsonb,
     '2026-09-28 21:47:00+00', NULL),
    ('bb300000-0000-0000-0000-000000000003', 'ba300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'fraud_alert', 'Velocity Rule V-217 Triggered', 'ALERT-V-217',
     '{"rule": "velocity_geo_mismatch", "details": "2 transactions / 33 minutes / 2 countries; home geo Austin, TX", "severity": "high"}'::jsonb,
     '2026-09-28 21:48:00+00', NULL),
    ('bb300000-0000-0000-0000-000000000004', 'ba300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'customer_profile', 'Customer Profile — NXC-4471', 'NXC-4471',
     '{"home_geo": "Austin, TX", "travel_notice": "none_on_file", "avg_monthly_spend_usd": 620, "prior_disputes": 0}'::jsonb,
     '2026-09-01 00:00:00+00', NULL),
    ('bb300000-0000-0000-0000-000000000005', 'ba300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'merchant_note', 'Chargeback History Note — Sample Electronics Retailer', 'MERCH-NOTE-221',
     '{"note": "merchant listed in network bulletin for weak 3-D Secure enrollment"}'::jsonb,
     '2026-09-20 00:00:00+00', NULL)
ON CONFLICT (id) DO NOTHING;

-- 17e. Dataset records — LogiCore Logistics
INSERT INTO dataset_records (id, dataset_id, organization_id, record_type, title, source_ref, payload, occurred_at, related_record_id)
VALUES
    ('bb400000-0000-0000-0000-000000000001', 'ba400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'shipment', 'Shipment RTM-77412 — Düsseldorf Consignment', 'RTM-77412',
     '{"origin": "Rotterdam, NL", "destination": "Düsseldorf, DE", "promised_eta": "2026-09-29 08:00", "status": "delayed", "contents": "industrial bearings"}'::jsonb,
     '2026-09-29 03:20:00+00', NULL),
    ('bb400000-0000-0000-0000-000000000002', 'ba400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'shipment', 'Shipment RTM-77398 — Baseline Consignment', 'RTM-77398',
     '{"origin": "Rotterdam, NL", "destination": "Antwerp, BE", "status": "delivered_on_time"}'::jsonb,
     '2026-09-29 03:25:00+00', NULL),
    ('bb400000-0000-0000-0000-000000000003', 'ba400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'scan_event', 'Missed Departure Scan — Dock 4', 'SCAN-D4-0929',
     '{"expected_scan": "departure_dock_4", "actual": "none", "trailer": "TRL-91", "delay_min": 55}'::jsonb,
     '2026-09-29 04:00:00+00', 'bb400000-0000-0000-0000-000000000001'),
    ('bb400000-0000-0000-0000-000000000004', 'ba400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'delay_incident', 'Customs Hold — Documentation Mismatch', 'INC-RTM-0929',
     '{"authority": "NL Customs (sample)", "reason": "invoice value mismatch on 2 pallets", "released_after_min": 130}'::jsonb,
     '2026-09-29 05:10:00+00', 'bb400000-0000-0000-0000-000000000001'),
    ('bb400000-0000-0000-0000-000000000005', 'ba400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'driver_report', 'Driver Report — Trailer TRL-91', 'DR-RPT-K7',
     '{"driver": "Driver K-7 (sample)", "note": "dock 4 congestion; three loads resequenced"}'::jsonb,
     '2026-09-29 06:30:00+00', NULL)
ON CONFLICT (id) DO NOTHING;

-- 17f. Dataset records — BrightGrid Energy
INSERT INTO dataset_records (id, dataset_id, organization_id, record_type, title, source_ref, payload, occurred_at, related_record_id)
VALUES
    ('bb500000-0000-0000-0000-000000000001', 'ba500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'sensor_reading', 'Feeder F-12 Voltage Sag — 04:42', 'SENS-F12-0929',
     '{"phase": "B", "voltage_kv": {"nominal": 11.0, "measured": 9.6}, "duration_s": 42}'::jsonb,
     '2026-09-29 04:42:00+00', NULL),
    ('bb500000-0000-0000-0000-000000000002', 'ba500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'sensor_reading', 'Feeder F-12 Load Trend — 24h', 'SENS-F12-24H',
     '{"phase_loads_a": {"A": 310, "B": 495, "C": 322}, "imbalance_pct": 27.4}'::jsonb,
     '2026-09-29 05:00:00+00', NULL),
    ('bb500000-0000-0000-0000-000000000003', 'ba500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'outage_ticket', 'Outage Ticket OG-2210 — F-12 Segment', 'OG-2210',
     '{"customers_affected": 1140, "duration_min": 18, "state": "restored_investigating"}'::jsonb,
     '2026-09-29 04:55:00+00', 'bb500000-0000-0000-0000-000000000001'),
    ('bb500000-0000-0000-0000-000000000004', 'ba500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'maintenance_log', 'Transformer T-F12 Tap Changer Service', 'WO-8812',
     '{"work_order": "WO-8812", "finding": "tap changer contact resistance high on steps 5-7", "action": "contacts cleaned; re-test scheduled"}'::jsonb,
     '2026-09-15 09:00:00+00', NULL),
    ('bb500000-0000-0000-0000-000000000005', 'ba500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'scada_alarm', 'SCADA Alarm Cluster — F-12', 'SCADA-F12-0929',
     '{"alarms": ["undervoltage_B", "tap_position_change_failed", "load_imbalance_high"], "count": 3}'::jsonb,
     '2026-09-29 04:41:00+00', 'bb500000-0000-0000-0000-000000000004')
ON CONFLICT (id) DO NOTHING;

-- 17g. Investigation tasks (decision-backed; existing task/assignment models)
INSERT INTO tasks (id, organization_id, name, description, status, decision_prompt, decision_options)
VALUES
    ('51000000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Gearbox Noise Investigation — Batch BR-2026-0917', 'Investigate the elevated gearbox noise in batch BR-2026-0917 using the linked production, inspection, maintenance, supply-chain and incident records, then classify the root cause. (Synthetic sample data.)', 'active',
     'Classify the root cause of the elevated gearbox noise in batch BR-2026-0917.',
     '["machining_tolerance_deviation", "bearing_lot_defect", "lubrication_underfill", "assembly_torque_error", "no_fault_found"]'::jsonb),
    ('51000000-0000-0000-0000-000000000002', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Paint Adhesion Investigation — Batch PA-2026-0830', 'Investigate the paint adhesion test failures in batch PA-2026-0830 using the linked paint shop, test and incident records, then classify the root cause. (Synthetic sample data. Completed example.)', 'active',
     'Classify the root cause of the paint adhesion failures in batch PA-2026-0830.',
     '["pretreatment_contamination", "paint_mix_ratio_error", "curing_oven_temperature", "substrate_surface_defect", "no_fault_found"]'::jsonb),
    ('51200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'Post-Op Vitals Anomaly Review — Bed 7', 'Review the post-operative vitals trend for Bed 7 against medication, lab, nursing and handover records, then classify the response. (Synthetic sample data.)', 'active',
     'Classify the clinical response for the Bed 7 vitals anomaly.',
     '["surgical_site_infection_escalation", "adverse_medication_reaction", "monitoring_device_artifact", "pain_induced_response", "stable_monitor_only"]'::jsonb),
    ('51300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'Suspicious Transaction Review — NXC-4471', 'Investigate the flagged transactions on account NXC-4471 using the linked transaction, alert, profile and merchant records, then classify the case. (Synthetic sample data.)', 'active',
     'Classify the suspicious activity on account NXC-4471.',
     '["confirm_fraud_block_card", "escalate_to_compliance", "legitimate_customer_activity", "customer_verification_required"]'::jsonb),
    ('51400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'Shipment Delay Root Cause — RTM-77412', 'Investigate the delayed Düsseldorf consignment using the linked shipment, scan, customs-incident and driver records, then classify the root cause. (Synthetic sample data.)', 'active',
     'Classify the root cause of the RTM-77412 delivery delay.',
     '["warehouse_dock_congestion", "customs_documentation_error", "carrier_equipment_failure", "consignee_address_issue", "weather_disruption"]'::jsonb),
    ('51500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'Feeder Voltage Anomaly Investigation — F-12', 'Investigate the F-12 voltage sag and outage using the linked sensor, ticket, maintenance and SCADA records, then classify the root cause. (Synthetic sample data.)', 'active',
     'Classify the root cause of the F-12 feeder voltage anomaly.',
     '["transformer_tap_changer_fault", "load_imbalance_phase_b", "upstream_transmission_fault", "sensor_calibration_drift"]'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- 17h. Investigation workflows
INSERT INTO workflows (id, organization_id, name, description, status)
VALUES
    ('e1000000-0000-0000-0000-000000000001', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Gearbox Noise Investigation Workflow', 'Evidence review and root-cause classification for batch BR-2026-0917', 'active'),
    ('e1000000-0000-0000-0000-000000000002', '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'Paint Adhesion Investigation Workflow', 'Evidence review and root-cause classification for batch PA-2026-0830', 'active'),
    ('e1200000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000002', 'Post-Op Vitals Review Workflow', 'Vitals, medication and lab evidence review for Bed 7', 'active'),
    ('e1300000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000003', 'Suspicious Transaction Review Workflow', 'Transaction and alert evidence review for NXC-4471', 'active'),
    ('e1400000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000004', 'Shipment Delay Investigation Workflow', 'Shipment and exception evidence review for RTM-77412', 'active'),
    ('e1500000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000005', 'Feeder Voltage Investigation Workflow', 'Sensor, ticket and maintenance evidence review for F-12', 'active')
ON CONFLICT (id) DO NOTHING;

-- 17i. Investigation workflow steps
INSERT INTO workflow_steps (id, workflow_id, step_order, name, description, status)
VALUES
    ('f1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', 1, 'Review Production Batch Records', 'Compare production records for batch BR-2026-0917 against the baseline batch BR-2026-0916: machine, material and bearing lots, and operator notes.', 'active'),
    ('f1000000-0000-0000-0000-000000000002', 'e1000000-0000-0000-0000-000000000001', 2, 'Review Quality Inspection Results', 'Examine the final noise/vibration gate failures and the in-process dimensional checks for the bearing bores.', 'active'),
    ('f1000000-0000-0000-0000-000000000003', 'e1000000-0000-0000-0000-000000000001', 3, 'Review Maintenance History', 'Check the CNC-7 spindle service record and the torque tool calibration status before the batch ran.', 'active'),
    ('f1000000-0000-0000-0000-000000000004', 'e1000000-0000-0000-0000-000000000001', 4, 'Review Incident Reports', 'Review the end-of-line test bench noise complaint and the Line 3 unplanned stoppage linked to this batch.', 'active'),
    ('f1000000-0000-0000-0000-000000000005', 'e1000000-0000-0000-0000-000000000001', 5, 'Classify Root Cause & Submit Decision', 'Weigh all evidence and classify the root cause. A decision is required to complete this task.', 'active'),
    ('f1000000-0000-0000-0000-000000000011', 'e1000000-0000-0000-0000-000000000002', 1, 'Review Paint Shop Records', 'Review the paint shop run PA-2026-0830: booth, pretreatment bath, cure oven and paint lot.', 'active'),
    ('f1000000-0000-0000-0000-000000000012', 'e1000000-0000-0000-0000-000000000002', 2, 'Review Adhesion Test Results', 'Examine the cross-cut test failures against specification.', 'active'),
    ('f1000000-0000-0000-0000-000000000013', 'e1000000-0000-0000-0000-000000000002', 3, 'Review Incident Reports', 'Review the PT-04 pretreatment bath filter alarm raised before the run.', 'active'),
    ('f1000000-0000-0000-0000-000000000014', 'e1000000-0000-0000-0000-000000000002', 4, 'Classify Root Cause & Submit Decision', 'Weigh all evidence and classify the root cause. A decision is required to complete this task.', 'active'),
    ('f1200000-0000-0000-0000-000000000001', 'e1200000-0000-0000-0000-000000000001', 1, 'Review Vitals Trend', 'Examine the heart-rate, blood-pressure, temperature and SpO2 trend for Bed 7.', 'active'),
    ('f1200000-0000-0000-0000-000000000002', 'e1200000-0000-0000-0000-000000000001', 2, 'Review Medications & Lab Panel', 'Check administered medications and the morning lab panel for explanatory patterns.', 'active'),
    ('f1200000-0000-0000-0000-000000000003', 'e1200000-0000-0000-0000-000000000001', 3, 'Review Notes & Handover', 'Read the nursing observation note and the shift handover summary.', 'active'),
    ('f1200000-0000-0000-0000-000000000004', 'e1200000-0000-0000-0000-000000000001', 4, 'Classify & Decide', 'Weigh all evidence and classify the clinical response. A decision is required to complete this task.', 'active'),
    ('f1300000-0000-0000-0000-000000000001', 'e1300000-0000-0000-0000-000000000001', 1, 'Review Flagged Transactions', 'Examine transactions T-99182 and T-99204: amounts, merchants, geos and 3-D Secure outcomes.', 'active'),
    ('f1300000-0000-0000-0000-000000000002', 'e1300000-0000-0000-0000-000000000001', 2, 'Review Fraud Alert & Profile', 'Check the velocity rule trigger against the customer profile and travel history.', 'active'),
    ('f1300000-0000-0000-0000-000000000003', 'e1300000-0000-0000-0000-000000000001', 3, 'Review Merchant Notes', 'Consider the merchant chargeback history note.', 'active'),
    ('f1300000-0000-0000-0000-000000000004', 'e1300000-0000-0000-0000-000000000001', 4, 'Classify & Decide', 'Weigh all evidence and classify the case. A decision is required to complete this task.', 'active'),
    ('f1400000-0000-0000-0000-000000000001', 'e1400000-0000-0000-0000-000000000001', 1, 'Review Shipment Records', 'Compare the delayed consignment RTM-77412 with the on-time baseline RTM-77398.', 'active'),
    ('f1400000-0000-0000-0000-000000000002', 'e1400000-0000-0000-0000-000000000001', 2, 'Review Scan Events', 'Examine the missed departure scan on dock 4 and the trailer assignment.', 'active'),
    ('f1400000-0000-0000-0000-000000000003', 'e1400000-0000-0000-0000-000000000001', 3, 'Review Customs & Driver Reports', 'Read the customs hold incident and the driver report.', 'active'),
    ('f1400000-0000-0000-0000-000000000004', 'e1400000-0000-0000-0000-000000000001', 4, 'Classify & Decide', 'Weigh all evidence and classify the root cause. A decision is required to complete this task.', 'active'),
    ('f1500000-0000-0000-0000-000000000001', 'e1500000-0000-0000-0000-000000000001', 1, 'Review Sensor Readings', 'Examine the phase-B voltage sag and the 24-hour load trend.', 'active'),
    ('f1500000-0000-0000-0000-000000000002', 'e1500000-0000-0000-0000-000000000001', 2, 'Review Outage Ticket & SCADA Alarms', 'Check the outage ticket and the SCADA alarm cluster timing.', 'active'),
    ('f1500000-0000-0000-0000-000000000003', 'e1500000-0000-0000-0000-000000000001', 3, 'Review Maintenance History', 'Read the transformer T-F12 tap changer service record.', 'active'),
    ('f1500000-0000-0000-0000-000000000004', 'e1500000-0000-0000-0000-000000000001', 4, 'Classify & Decide', 'Weigh all evidence and classify the root cause. A decision is required to complete this task.', 'active')
ON CONFLICT (id) DO NOTHING;

-- 17j. Task → workflow links
INSERT INTO task_workflows (task_id, workflow_id)
VALUES
    ('51000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001'),
    ('51000000-0000-0000-0000-000000000002', 'e1000000-0000-0000-0000-000000000002'),
    ('51200000-0000-0000-0000-000000000001', 'e1200000-0000-0000-0000-000000000001'),
    ('51300000-0000-0000-0000-000000000001', 'e1300000-0000-0000-0000-000000000001'),
    ('51400000-0000-0000-0000-000000000001', 'e1400000-0000-0000-0000-000000000001'),
    ('51500000-0000-0000-0000-000000000001', 'e1500000-0000-0000-0000-000000000001')
ON CONFLICT (task_id, workflow_id) DO NOTHING;

-- 17k. Task → evidence record links (the task → dataset relationships)
INSERT INTO task_evidence (task_id, record_id, relevance)
VALUES
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000001', 'Batch under investigation: bearing lot SL-8821 and CNC-7 used.'),
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000002', 'Baseline batch for comparison: same machine and material lot.'),
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000003', 'Failed noise gate that triggered the investigation.'),
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000004', 'Dimensional deviation on bearing bores in the same batch.'),
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000005', 'Baseline noise gate passed one day earlier.'),
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000006', 'CNC-7 spindle service four days before the batch.'),
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000007', 'Torque tool calibration overdue during the batch window.'),
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000008', 'Incoming inspection of bearing lot SL-8821 used in the batch.'),
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000009', 'Independent test bench confirmation of the noise complaint.'),
    ('51000000-0000-0000-0000-000000000001', 'bb100000-0000-0000-0000-000000000010', 'Line stoppage on the same machine after the batch.'),
    ('51000000-0000-0000-0000-000000000002', 'bb100000-0000-0000-0000-000000000011', 'Paint shop run under investigation.'),
    ('51000000-0000-0000-0000-000000000002', 'bb100000-0000-0000-0000-000000000012', 'Cross-cut adhesion test failures.'),
    ('51000000-0000-0000-0000-000000000002', 'bb100000-0000-0000-0000-000000000013', 'Pretreatment bath filter alarm before the run.'),
    ('51200000-0000-0000-0000-000000000001', 'bb200000-0000-0000-0000-000000000001', 'Vitals trend driving the review.'),
    ('51200000-0000-0000-0000-000000000001', 'bb200000-0000-0000-0000-000000000002', 'Medications administered before the trend change.'),
    ('51200000-0000-0000-0000-000000000001', 'bb200000-0000-0000-0000-000000000003', 'Morning lab panel with elevated WBC/CRP.'),
    ('51200000-0000-0000-0000-000000000001', 'bb200000-0000-0000-0000-000000000004', 'Nursing observation: dizziness and redness at the site.'),
    ('51200000-0000-0000-0000-000000000001', 'bb200000-0000-0000-0000-000000000005', 'Shift handover summary and escalation status.'),
    ('51300000-0000-0000-0000-000000000001', 'bb300000-0000-0000-0000-000000000001', 'First flagged transaction (settled).'),
    ('51300000-0000-0000-0000-000000000001', 'bb300000-0000-0000-0000-000000000002', 'Second transaction (declined by 3-D Secure).'),
    ('51300000-0000-0000-0000-000000000001', 'bb300000-0000-0000-0000-000000000003', 'Velocity rule alert that opened the case.'),
    ('51300000-0000-0000-0000-000000000001', 'bb300000-0000-0000-0000-000000000004', 'Customer profile and travel history.'),
    ('51300000-0000-0000-0000-000000000001', 'bb300000-0000-0000-0000-000000000005', 'Merchant risk note.'),
    ('51400000-0000-0000-0000-000000000001', 'bb400000-0000-0000-0000-000000000001', 'Delayed consignment under investigation.'),
    ('51400000-0000-0000-0000-000000000001', 'bb400000-0000-0000-0000-000000000002', 'On-time baseline consignment.'),
    ('51400000-0000-0000-0000-000000000001', 'bb400000-0000-0000-0000-000000000003', 'Missed departure scan for the same trailer.'),
    ('51400000-0000-0000-0000-000000000001', 'bb400000-0000-0000-0000-000000000004', 'Customs hold with documentation mismatch.'),
    ('51400000-0000-0000-0000-000000000001', 'bb400000-0000-0000-0000-000000000005', 'Driver report on dock congestion.'),
    ('51500000-0000-0000-0000-000000000001', 'bb500000-0000-0000-0000-000000000001', 'Phase-B voltage sag measurement.'),
    ('51500000-0000-0000-0000-000000000001', 'bb500000-0000-0000-0000-000000000002', '24-hour load trend showing phase imbalance.'),
    ('51500000-0000-0000-0000-000000000001', 'bb500000-0000-0000-0000-000000000003', 'Outage ticket tied to the sag.'),
    ('51500000-0000-0000-0000-000000000001', 'bb500000-0000-0000-0000-000000000004', 'Tap changer service history.'),
    ('51500000-0000-0000-0000-000000000001', 'bb500000-0000-0000-0000-000000000005', 'SCADA alarm cluster at sag onset.')
ON CONFLICT (task_id, record_id) DO NOTHING;

-- 17l. Worker task assignments (existing worker_task_assignments model)
--      Acme: one in-progress investigation (the live demo) + one completed
--      investigation with a persisted result. Other orgs: one assigned task
--      each for their first worker.
INSERT INTO worker_task_assignments (id, task_id, worker_profile_id, status, assigned_at, started_at, completed_at)
VALUES
    ('62000000-0000-0000-0000-000000000001', '51000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'in_progress', '2026-09-29 06:30:00+00', '2026-09-29 06:41:00+00', NULL),
    ('62000000-0000-0000-0000-000000000002', '51000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-000000000001', 'completed', '2026-09-28 03:30:00+00', '2026-09-28 03:41:00+00', '2026-09-28 04:27:30+00'),
    ('62200000-0000-0000-0000-000000000001', '51200000-0000-0000-0000-000000000001', 'ad200000-0000-0000-0000-000000000001', 'assigned', '2026-09-29 08:00:00+00', NULL, NULL),
    ('62300000-0000-0000-0000-000000000001', '51300000-0000-0000-0000-000000000001', 'ad300000-0000-0000-0000-000000000001', 'assigned', '2026-09-29 08:00:00+00', NULL, NULL),
    ('62400000-0000-0000-0000-000000000001', '51400000-0000-0000-0000-000000000001', 'ad400000-0000-0000-0000-000000000001', 'assigned', '2026-09-29 08:00:00+00', NULL, NULL),
    ('62500000-0000-0000-0000-000000000001', '51500000-0000-0000-0000-000000000001', 'ad500000-0000-0000-0000-000000000001', 'assigned', '2026-09-29 08:00:00+00', NULL, NULL)
ON CONFLICT (id) DO NOTHING;

-- 17m. Workflow assignments (existing model) — Acme only: the in-progress
--      cycle for the live demo and the completed cycle for the seeded result.
INSERT INTO workflow_assignments (id, workflow_id, worker_profile_id, status, assigned_at, started_at, completed_at)
VALUES
    ('63000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'in_progress', '2026-09-29 06:30:00+00', '2026-09-29 06:41:00+00', NULL),
    ('63000000-0000-0000-0000-000000000002', 'e1000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-000000000001', 'completed', '2026-09-28 03:30:00+00', '2026-09-28 03:41:00+00', '2026-09-28 04:27:30+00')
ON CONFLICT (id) DO NOTHING;

-- 17n. Step executions for the completed investigation cycle (persisted
--      progress of the seeded example)
INSERT INTO workflow_step_executions (id, workflow_assignment_id, workflow_step_id, status, started_at, completed_at, notes)
VALUES
    ('64000000-0000-0000-0000-000000000001', '63000000-0000-0000-0000-000000000002', 'f1000000-0000-0000-0000-000000000011', 'completed', '2026-09-28 03:45:00+00', '2026-09-28 03:58:00+00', 'Reviewed paint shop run parameters.'),
    ('64000000-0000-0000-0000-000000000002', '63000000-0000-0000-0000-000000000002', 'f1000000-0000-0000-0000-000000000012', 'completed', '2026-09-28 03:58:00+00', '2026-09-28 04:12:00+00', 'Cross-cut failures confirmed against spec.'),
    ('64000000-0000-0000-0000-000000000003', '63000000-0000-0000-0000-000000000002', 'f1000000-0000-0000-0000-000000000013', 'completed', '2026-09-28 04:12:00+00', '2026-09-28 04:20:00+00', 'PT-04 filter alarm noted before the run.'),
    ('64000000-0000-0000-0000-000000000004', '63000000-0000-0000-0000-000000000002', 'f1000000-0000-0000-0000-000000000014', 'completed', '2026-09-28 04:20:00+00', '2026-09-28 04:27:30+00', 'Classified as pretreatment contamination.')
ON CONFLICT (id) DO NOTHING;

-- 17o. Persisted worker result for the completed investigation (existing
--      task_results model; server-style computed stats included)
INSERT INTO task_results (id, worker_task_assignment_id, outcome, result_data, notes, recorded_at)
VALUES
    ('65000000-0000-0000-0000-000000000001', '62000000-0000-0000-0000-000000000002', 'completed',
     '{"classification": "pretreatment_contamination", "decision_notes": "Cross-cut failures align with the PT-04 pretreatment bath contamination flagged by the filter alarm before the run.", "completed_steps": 4, "total_steps": 4, "outcome": "completed", "duration_seconds": 2790.0}'::jsonb,
     'Investigation completed through accessible multimodal workstation (seeded example).',
     '2026-09-28 04:27:30+00')
ON CONFLICT (id) DO NOTHING;
