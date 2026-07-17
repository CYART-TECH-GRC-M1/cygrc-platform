-- ==========================================
-- CyGRC Seed Data
-- ==========================================

-- ===========================
-- Default Roles
-- ===========================

INSERT INTO roles (role_name, description)
VALUES
('Super Admin', 'Full platform access'),
('Tenant Admin', 'Manages tenant users and settings'),
('Compliance Manager', 'Manages compliance activities'),
('Auditor', 'Performs audits and reviews'),
('Employee', 'Standard platform user');


-- ===========================
-- Default Permissions
-- ===========================

INSERT INTO permissions (permission_name, description)
VALUES
('CREATE_USER', 'Create new users'),
('UPDATE_USER', 'Update user details'),
('DELETE_USER', 'Delete users'),
('VIEW_USERS', 'View user list'),

('CREATE_ROLE', 'Create roles'),
('UPDATE_ROLE', 'Update roles'),
('DELETE_ROLE', 'Delete roles'),

('CREATE_FRAMEWORK', 'Create compliance frameworks'),
('UPDATE_FRAMEWORK', 'Update compliance frameworks'),
('DELETE_FRAMEWORK', 'Delete compliance frameworks'),

('CREATE_CONTROL', 'Create controls'),
('UPDATE_CONTROL', 'Update controls'),
('DELETE_CONTROL', 'Delete controls'),

('CREATE_RISK', 'Create risks'),
('UPDATE_RISK', 'Update risks'),
('DELETE_RISK', 'Delete risks'),

('UPLOAD_EVIDENCE', 'Upload evidence'),
('REVIEW_EVIDENCE', 'Review evidence'),

('CREATE_AUDIT', 'Create audits'),
('UPDATE_AUDIT', 'Update audits'),
('CLOSE_AUDIT', 'Close audits'),

('VIEW_DASHBOARD', 'View dashboard'),

('MANAGE_POLICIES', 'Manage policies'),

('MANAGE_ASSETS', 'Manage assets'),

('MANAGE_VENDORS', 'Manage vendors');

-- ===========================
-- Role → Permission Mapping
-- ===========================

-- Super Admin gets ALL permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT
    r.role_id,
    p.permission_id
FROM roles r
CROSS JOIN permissions p
WHERE r.role_name = 'Super Admin';

-- ===========================
-- Tenant Admin Permissions
-- ===========================

INSERT INTO role_permissions (role_id, permission_id)
SELECT
    r.role_id,
    p.permission_id
FROM roles r
JOIN permissions p
ON p.permission_name IN (
    'CREATE_USER',
    'UPDATE_USER',
    'VIEW_USERS',

    'CREATE_RISK',
    'UPDATE_RISK',

    'UPLOAD_EVIDENCE',
    'REVIEW_EVIDENCE',

    'CREATE_AUDIT',
    'UPDATE_AUDIT',

    'VIEW_DASHBOARD',

    'MANAGE_POLICIES',

    'MANAGE_ASSETS',

    'MANAGE_VENDORS'
)
WHERE r.role_name = 'Tenant Admin';

-- ===========================
-- Compliance Manager Permissions
-- ===========================

INSERT INTO role_permissions (role_id, permission_id)
SELECT
    r.role_id,
    p.permission_id
FROM roles r
JOIN permissions p
ON p.permission_name IN (
    'CREATE_FRAMEWORK',
    'UPDATE_FRAMEWORK',

    'CREATE_CONTROL',
    'UPDATE_CONTROL',

    'UPLOAD_EVIDENCE',
    'REVIEW_EVIDENCE',

    'CREATE_AUDIT',
    'UPDATE_AUDIT',

    'VIEW_DASHBOARD',

    'MANAGE_POLICIES'
)
WHERE r.role_name = 'Compliance Manager';

-- ===========================
-- Auditor Permissions
-- ===========================

INSERT INTO role_permissions (role_id, permission_id)
SELECT
    r.role_id,
    p.permission_id
FROM roles r
JOIN permissions p
ON p.permission_name IN (
    'VIEW_DASHBOARD',

    'REVIEW_EVIDENCE',

    'CREATE_AUDIT',
    'UPDATE_AUDIT',
    'CLOSE_AUDIT'
)
WHERE r.role_name = 'Auditor';

-- ===========================
-- Employee Permissions
-- ===========================

INSERT INTO role_permissions (role_id, permission_id)
SELECT
    r.role_id,
    p.permission_id
FROM roles r
JOIN permissions p
ON p.permission_name IN (
    'VIEW_DASHBOARD',

    'UPLOAD_EVIDENCE'
)
WHERE r.role_name = 'Employee';

-- ==========================================
-- Default Compliance Frameworks
-- ==========================================

INSERT INTO frameworks (
    framework_name,
    version,
    description
)
VALUES
(
    'ISO/IEC 27001',
    '2022',
    'International standard for Information Security Management Systems (ISMS).'
),
(
    'NIST Cybersecurity Framework',
    '2.0',
    'Framework developed by the National Institute of Standards and Technology.'
),
(
    'SOC 2',
    '2017',
    'Service Organization Control Type 2 framework.'
),
(
    'PCI DSS',
    '4.0',
    'Payment Card Industry Data Security Standard.'
),
(
    'HIPAA',
    '2013',
    'Health Insurance Portability and Accountability Act.'
),
(
    'GDPR',
    '2018',
    'General Data Protection Regulation.'
);

-- ==========================================
-- Default Framework Versions
-- ==========================================

INSERT INTO framework_versions (
    framework_id,
    version,
    release_date
)
SELECT framework_id, '2022', '2022-10-25'
FROM frameworks
WHERE framework_name = 'ISO/IEC 27001';

INSERT INTO framework_versions (
    framework_id,
    version,
    release_date
)
SELECT framework_id, '2.0', '2024-02-26'
FROM frameworks
WHERE framework_name = 'NIST Cybersecurity Framework';

INSERT INTO framework_versions (
    framework_id,
    version,
    release_date
)
SELECT framework_id, '2017', '2017-04-01'
FROM frameworks
WHERE framework_name = 'SOC 2';

INSERT INTO framework_versions (
    framework_id,
    version,
    release_date
)
SELECT framework_id, '4.0', '2022-03-31'
FROM frameworks
WHERE framework_name = 'PCI DSS';

INSERT INTO framework_versions (
    framework_id,
    version,
    release_date
)
SELECT framework_id, '2013', '2013-09-23'
FROM frameworks
WHERE framework_name = 'HIPAA';

INSERT INTO framework_versions (
    framework_id,
    version,
    release_date
)
SELECT framework_id, '2018', '2018-05-25'
FROM frameworks
WHERE framework_name = 'GDPR';

-- ==========================================
-- ISO/IEC 27001 Control Families
-- ==========================================

INSERT INTO control_families (
    framework_id,
    family_name,
    description
)
SELECT
    framework_id,
    'Organizational',
    'Organizational controls covering governance, policies, and risk management.'
FROM frameworks
WHERE framework_name = 'ISO/IEC 27001';

INSERT INTO control_families (
    framework_id,
    family_name,
    description
)
SELECT
    framework_id,
    'People',
    'Controls related to personnel security, awareness, and responsibilities.'
FROM frameworks
WHERE framework_name = 'ISO/IEC 27001';

INSERT INTO control_families (
    framework_id,
    family_name,
    description
)
SELECT
    framework_id,
    'Physical',
    'Controls protecting physical locations, facilities, and equipment.'
FROM frameworks
WHERE framework_name = 'ISO/IEC 27001';

INSERT INTO control_families (
    framework_id,
    family_name,
    description
)
SELECT
    framework_id,
    'Technological',
    'Controls related to technology, networks, applications, and systems.'
FROM frameworks
WHERE framework_name = 'ISO/IEC 27001';

-- ==========================================
-- ISO/IEC 27001 Controls
-- ==========================================

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.5.1',
    'Policies for Information Security',
    'Information security policies shall be defined, approved, published and communicated.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'Organizational';

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.5.2',
    'Information Security Roles and Responsibilities',
    'Information security responsibilities shall be assigned and communicated.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'Organizational';

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.5.7',
    'Threat Intelligence',
    'Collect and analyze information relating to information security threats.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'Organizational';

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.6.1',
    'Screening',
    'Background verification checks should be performed before employment.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'People';

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.6.3',
    'Information Security Awareness',
    'Personnel shall receive appropriate information security awareness training.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'People';

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.7.1',
    'Physical Security Perimeters',
    'Security perimeters shall be defined and protected.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'Physical';

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.8.1',
    'User Endpoint Devices',
    'Endpoint devices shall be appropriately secured.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'Technological';

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.8.5',
    'Secure Authentication',
    'Secure authentication technologies shall be implemented.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'Technological';

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.8.15',
    'Logging',
    'Event logs shall be produced, protected and regularly reviewed.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'Technological';

INSERT INTO controls (
    framework_id,
    control_family_id,
    control_code,
    control_name,
    description
)
SELECT
    f.framework_id,
    cf.control_family_id,
    'A.8.16',
    'Monitoring Activities',
    'Networks, systems and applications shall be monitored for security events.'
FROM frameworks f
JOIN control_families cf
ON f.framework_id = cf.framework_id
WHERE f.framework_name = 'ISO/IEC 27001'
AND cf.family_name = 'Technological';

-- ==========================================
-- Default Tenant
-- ==========================================

INSERT INTO tenants (
    name,
    domain,
    subscription_plan,
    status
)
VALUES (
    'CyGRC Demo Organization',
    'demo.cygrc.local',
    'ENTERPRISE',
    'ACTIVE'
);

-- ==========================================
-- Default Administrator User
-- ==========================================

INSERT INTO users (
    tenant_id,
    first_name,
    last_name,
    email,
    keycloak_id,
    status
)
SELECT
    tenant_id,
    'System',
    'Administrator',
    'admin@demo.cygrc.local',
    NULL,
    'ACTIVE'
FROM tenants
WHERE domain = 'demo.cygrc.local';

-- ==========================================
-- Assign Super Admin Role
-- ==========================================

INSERT INTO user_roles (
    user_id,
    role_id
)
SELECT
    u.user_id,
    r.role_id
FROM users u
JOIN roles r
ON r.role_name = 'Super Admin'
WHERE u.email = 'admin@demo.cygrc.local';

-- ==========================================
-- Demo Risks
-- ==========================================

INSERT INTO risks (
    tenant_id,
    control_id,
    title,
    description,
    likelihood,
    impact,
    risk_score,
    status,
    created_by
)
SELECT
    t.tenant_id,
    c.control_id,
    'Weak Password Policy',
    "Users are creating passwords that do not meet the organization's complexity requirements.",
    4,
    5,
    20,
    'ACTIVE',
    u.user_id
FROM tenants t
JOIN users u
ON u.tenant_id = t.tenant_id
JOIN controls c
ON c.control_code = 'A.8.5'
WHERE t.domain = 'demo.cygrc.local'
AND u.email = 'admin@demo.cygrc.local'
LIMIT 1;

-- ==========================================
-- Demo Risk Assessment
-- ==========================================

INSERT INTO risk_assessments (
    risk_id,
    assessor_id,
    assessment_date,
    likelihood,
    impact,
    risk_score,
    comments
)
SELECT
    r.risk_id,
    u.user_id,
    CURRENT_DATE,
    4,
    5,
    20,
    'Initial risk assessment completed by the Compliance Team.'
FROM risks r
JOIN users u
ON u.email = 'admin@demo.cygrc.local'
WHERE r.title = 'Weak Password Policy'
LIMIT 1;

-- ==========================================
-- Demo Risk Treatment
-- ==========================================

INSERT INTO risk_treatments (
    risk_id,
    owner_id,
    treatment_plan,
    target_date,
    status
)
SELECT
    r.risk_id,
    u.user_id,
    'Implement strong password policy, enforce MFA, and conduct user awareness training.',
    CURRENT_DATE + INTERVAL '30 days',
    'OPEN'
FROM risks r
JOIN users u
ON u.email = 'admin@demo.cygrc.local'
WHERE r.title = 'Weak Password Policy'
LIMIT 1;

-- ==========================================
-- Demo Evidence
-- ==========================================

INSERT INTO evidence (
    tenant_id,
    control_id,
    uploaded_by,
    title,
    description,
    status
)
SELECT
    t.tenant_id,
    c.control_id,
    u.user_id,
    'Password Policy Document',
    'Approved password policy defining password complexity, expiration, and MFA requirements.',
    'ACTIVE'
FROM tenants t
JOIN users u
ON u.tenant_id = t.tenant_id
JOIN controls c
ON c.control_code = 'A.8.5'
WHERE t.domain = 'demo.cygrc.local'
AND u.email = 'admin@demo.cygrc.local'
LIMIT 1;

-- ==========================================
-- Demo Evidence File
-- ==========================================

INSERT INTO evidence_files (
    evidence_id,
    file_name,
    file_path,
    file_size,
    file_type
)
SELECT
    e.evidence_id,
    'Password_Policy_v1.pdf',
    '/uploads/policies/Password_Policy_v1.pdf',
    524288,
    'application/pdf'
FROM evidence e
WHERE e.title = 'Password Policy Document'
LIMIT 1;

-- ==========================================
-- Demo Evidence Review
-- ==========================================

INSERT INTO evidence_reviews (
    evidence_id,
    reviewer_id,
    review_status,
    comments
)
SELECT
    e.evidence_id,
    u.user_id,
    'APPROVED',
    'Evidence reviewed and approved. Password policy meets ISO/IEC 27001 requirements.'
FROM evidence e
JOIN users u
ON u.email = 'admin@demo.cygrc.local'
WHERE e.title = 'Password Policy Document'
LIMIT 1;

-- ==========================================
-- Demo Audit
-- ==========================================

INSERT INTO audits (
    tenant_id,
    framework_id,
    audit_name,
    start_date,
    end_date,
    status,
    created_by
)
SELECT
    t.tenant_id,
    f.framework_id,
    'ISO 27001 Internal Audit 2026',
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '14 days',
    'IN_PROGRESS',
    u.user_id
FROM tenants t
JOIN users u
ON u.tenant_id = t.tenant_id
JOIN frameworks f
ON f.framework_name = 'ISO/IEC 27001'
WHERE
    t.domain = 'demo.cygrc.local'
    AND u.email = 'admin@demo.cygrc.local'
LIMIT 1;

-- ==========================================
-- Demo Audit Finding
-- ==========================================

INSERT INTO audit_findings (
    audit_id,
    control_id,
    title,
    description,
    severity,
    status
)
SELECT
    a.audit_id,
    c.control_id,
    'Weak Password Enforcement',
    'The audit identified that password complexity requirements are not consistently enforced across all user accounts.',
    'HIGH',
    'OPEN'
FROM audits a
JOIN controls c
ON c.control_code = 'A.8.5'
WHERE a.audit_name = 'ISO 27001 Internal Audit 2026'
LIMIT 1;

-- ==========================================
-- Demo Audit Evidence
-- ==========================================

INSERT INTO audit_evidence (
    finding_id,
    evidence_id
)
SELECT
    af.finding_id,
    e.evidence_id
FROM audit_findings af
JOIN evidence e
ON e.title = 'Password Policy Document'
WHERE af.title = 'Weak Password Enforcement'
LIMIT 1;

-- ==========================================
-- Demo Policy
-- ==========================================

INSERT INTO policies (
    tenant_id,
    policy_name,
    version,
    owner_id,
    effective_date,
    review_date,
    status
)
SELECT
    t.tenant_id,
    'Information Security Policy',
    '1.0',
    u.user_id,
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '365 days',
    'ACTIVE'
FROM tenants t
JOIN users u
ON u.tenant_id = t.tenant_id
WHERE
    t.domain = 'demo.cygrc.local'
    AND u.email = 'admin@demo.cygrc.local'
LIMIT 1;

-- ==========================================
-- Demo Policy Acknowledgement
-- ==========================================

INSERT INTO policy_acknowledgements (
    policy_id,
    user_id
)
SELECT
    p.policy_id,
    u.user_id
FROM policies p
JOIN users u
ON u.email = 'admin@demo.cygrc.local'
WHERE p.policy_name = 'Information Security Policy'
LIMIT 1;

-- ==========================================
-- Demo Asset
-- ==========================================

INSERT INTO assets (
    tenant_id,
    asset_name,
    asset_type,
    owner_id,
    location,
    status
)
SELECT
    t.tenant_id,
    'Employee Laptop - Dell Latitude 7440',
    'Laptop',
    u.user_id,
    'Hyderabad Office',
    'ACTIVE'
FROM tenants t
JOIN users u
ON u.tenant_id = t.tenant_id
WHERE
    t.domain = 'demo.cygrc.local'
    AND u.email = 'admin@demo.cygrc.local'
LIMIT 1;

-- ==========================================
-- Demo Vendor
-- ==========================================

INSERT INTO vendors (
    tenant_id,
    vendor_name,
    contact_email,
    risk_level
)
SELECT
    t.tenant_id,
    'Microsoft',
    'security@microsoft.com',
    'LOW'
FROM tenants t
WHERE t.domain = 'demo.cygrc.local'
LIMIT 1;

-- ==========================================
-- Demo Task
-- ==========================================

INSERT INTO tasks (
    tenant_id,
    assigned_to,
    title,
    description,
    due_date,
    status
)
SELECT
    t.tenant_id,
    u.user_id,
    'Implement Multi-Factor Authentication',
    'Deploy MFA for all employee accounts to reduce the risk of unauthorized access.',
    CURRENT_DATE + INTERVAL '15 days',
    'OPEN'
FROM tenants t
JOIN users u
ON u.tenant_id = t.tenant_id
WHERE
    t.domain = 'demo.cygrc.local'
    AND u.email = 'admin@demo.cygrc.local'
LIMIT 1;

-- ==========================================
-- Demo Comment
-- ==========================================

INSERT INTO comments (
    task_id,
    user_id,
    comment
)
SELECT
    t.task_id,
    u.user_id,
    'MFA rollout has started. Pilot testing will begin this week.'
FROM tasks t
JOIN users u
ON u.email = 'admin@demo.cygrc.local'
WHERE t.title = 'Implement Multi-Factor Authentication'
LIMIT 1;

-- ==========================================
-- Demo Attachment
-- ==========================================

INSERT INTO attachments (
    task_id,
    uploaded_by,
    file_name,
    file_path
)
SELECT
    t.task_id,
    u.user_id,
    'MFA_Implementation_Plan.pdf',
    '/uploads/tasks/MFA_Implementation_Plan.pdf'
FROM tasks t
JOIN users u
ON u.email = 'admin@demo.cygrc.local'
WHERE t.title = 'Implement Multi-Factor Authentication'
LIMIT 1;

-- ==========================================
-- Demo Notification
-- ==========================================

INSERT INTO notifications (
    user_id,
    title,
    message,
    is_read
)
SELECT
    u.user_id,
    'Task Assigned',
    'You have been assigned the task: Implement Multi-Factor Authentication.',
    FALSE
FROM users u
WHERE u.email = 'admin@demo.cygrc.local'
LIMIT 1;

-- ==========================================
-- Demo Activity Log
-- ==========================================

INSERT INTO activity_logs (
    tenant_id,
    user_id,
    action,
    entity_name,
    entity_id
)
SELECT
    t.tenant_id,
    u.user_id,
    'CREATE_TASK',
    'Task',
    task.task_id
FROM tenants t
JOIN users u
    ON u.tenant_id = t.tenant_id
JOIN tasks task
    ON task.assigned_to = u.user_id
WHERE
    t.domain = 'demo.cygrc.local'
    AND u.email = 'admin@demo.cygrc.local'
    AND task.title = 'Implement Multi-Factor Authentication'
LIMIT 1;

-- ==========================================
-- Demo API Key
-- ==========================================

INSERT INTO api_keys (
    tenant_id,
    key_name,
    api_key,
    expires_at
)
SELECT
    t.tenant_id,
    'CyGRC Demo API Key',
    'cygrc_demo_api_key_2026_abcdefghijklmnopqrstuvwxyz',
    CURRENT_TIMESTAMP + INTERVAL '365 days'
FROM tenants t
WHERE t.domain = 'demo.cygrc.local'
LIMIT 1;