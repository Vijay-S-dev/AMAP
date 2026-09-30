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
