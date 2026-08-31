CREATE EXTENSION IF NOT EXISTS "uuid-ossp";                                 --It allows PostgreSQL to generate UUIDs automatically.

CREATE TYPE tenant_status AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'SUSPENDED'
);

CREATE TYPE audit_status AS ENUM (
    'PLANNED',
    'IN_PROGRESS',
    'COMPLETED'
);

CREATE TYPE task_status AS ENUM (
    'OPEN',
    'IN_PROGRESS',
    'COMPLETED'
);

CREATE TYPE review_status AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED'
);

CREATE TYPE risk_status AS ENUM (
    'OPEN',
    'MITIGATED',
    'CLOSED'
);

CREATE TABLE tenants (                                                      --Create a table called tenants.

    tenant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),                  --Every company gets a unique ID automatically.

    name VARCHAR(255) NOT NULL,                                             --Store the company name.

    domain VARCHAR(255) UNIQUE,

    subscription_plan VARCHAR(100)
    CHECK (subscription_plan IN ('FREE','BASIC','ENTERPRISE')),

    status tenant_status DEFAULT 'ACTIVE',                                  --Store the status of the company. It can be ACTIVE, INACTIVE, or SUSPENDED.

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                         --Store the timestamp when the company was created.

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                          --When was this company last updated?

);

CREATE TABLE users (                                                        --Create a table called users.

    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),                    --Every user gets a unique ID automatically.

    tenant_id UUID NOT NULL,                                                --It tells PostgreSQL that every user must belong to one company (tenant).

    first_name VARCHAR(100) NOT NULL,

    last_name VARCHAR(100),

    email VARCHAR(255) UNIQUE NOT NULL,                                     --Store the user's email address. It must be unique and cannot be null.

    keycloak_id VARCHAR(255),
    --Store the user's Keycloak ID. It is used for authentication and authorization.
    --When a user logs in using Keycloak, Keycloak creates its own unique ID.
    --We store that ID here so our application knows which Keycloak account belongs to which user.

    status tenant_status DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    --This creates a relationship between the tables.
    CONSTRAINT fk_users_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)

);

CREATE TABLE roles (                                                        --Create a table called roles.

    role_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),                    --Every role gets a unique ID automatically.

    role_name VARCHAR(100) UNIQUE NOT NULL,                                 --Stores the role name.

    description TEXT,                                                       --Stores details about the role.

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                          --Stores when the role was created.

);
/*
| role_name          | description           |
| ------------------ | --------------------- |
| Super Admin        | Can manage everything |
| Tenant Admin       | Manages one company   |
| Compliance Manager | Manages compliance    |
| Auditor            | Performs audits       |
| Employee           | Normal user           |

*/

CREATE TABLE permissions (                                                  --Create a table called permissions.

    permission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),              --Every permission gets a unique ID automatically.

    permission_name VARCHAR(100) UNIQUE NOT NULL,                          --Stores the permission name.

    description TEXT,                                                      --Stores what the permission does.

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE user_roles (                                                  --Create a table called user_roles.

    user_role_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),              --Every user_role gets a unique ID automatically.

    user_id UUID NOT NULL,

    role_id UUID NOT NULL,

    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                        --Stores when the role was assigned to the user.

    CONSTRAINT fk_user_roles_user
        FOREIGN KEY (user_id)                                               --You cannot assign a role to a user that doesn't exist.
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user_roles_role
        FOREIGN KEY (role_id)                                               --You cannot assign a role that doesn't exist.
        REFERENCES roles(role_id)
        ON DELETE CASCADE,

    CONSTRAINT unique_user_role
        UNIQUE (user_id, role_id)

);

CREATE TABLE role_permissions (                                                  --Creates a bridge table.

    role_permission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),              --Every role_permission gets a unique ID automatically.

    role_id UUID NOT NULL,                                                       --Which role?

    permission_id UUID NOT NULL,                                                 --Which permission?

    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_role_permissions_role
        FOREIGN KEY (role_id)
        REFERENCES roles(role_id)                                                --The role must already exist.
        ON DELETE CASCADE,

    CONSTRAINT fk_role_permissions_permission
        FOREIGN KEY (permission_id)
        REFERENCES permissions(permission_id)                                    --The permission must already exist.
        ON DELETE CASCADE,

    CONSTRAINT unique_role_permission
        UNIQUE (role_id, permission_id)

);

CREATE TABLE frameworks (

    framework_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    framework_name VARCHAR(255) UNIQUE NOT NULL,

    version VARCHAR(50),

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE framework_versions (

    framework_version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),---Every framework version gets a unique ID automatically.

    framework_id UUID NOT NULL,---Which framework does this version belong to?

    version VARCHAR(50) NOT NULL,---Store the version of the framework.

    release_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_framework_versions_framework
        FOREIGN KEY (framework_id)
        REFERENCES frameworks(framework_id)
        ON DELETE CASCADE

);

CREATE TABLE control_families (

    control_family_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    framework_id UUID NOT NULL,

    family_name VARCHAR(255) NOT NULL,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_control_family_framework
        FOREIGN KEY (framework_id)
        REFERENCES frameworks(framework_id)
        ON DELETE CASCADE

);

CREATE TABLE controls (

    control_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    framework_id UUID NOT NULL,

    control_family_id UUID NOT NULL,

    control_code VARCHAR(50) NOT NULL,

    control_name VARCHAR(255) NOT NULL,

    description TEXT,

    status tenant_status DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_controls_framework
        FOREIGN KEY (framework_id)
        REFERENCES frameworks(framework_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_controls_family
        FOREIGN KEY (control_family_id)
        REFERENCES control_families(control_family_id)
        ON DELETE CASCADE

);

CREATE TABLE control_mappings (

    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    source_control_id UUID NOT NULL,

    target_control_id UUID NOT NULL,

    mapping_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_source_control
        FOREIGN KEY (source_control_id)
        REFERENCES controls(control_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_target_control
        FOREIGN KEY (target_control_id)
        REFERENCES controls(control_id)
        ON DELETE CASCADE

);

CREATE TABLE risks (

    risk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    tenant_id UUID NOT NULL,

    control_id UUID,

    title VARCHAR(255) NOT NULL,

    description TEXT,

    likelihood INTEGER CHECK (likelihood BETWEEN 1 AND 5),

    impact INTEGER CHECK (impact BETWEEN 1 AND 5),

    risk_score INTEGER,

    status tenant_status DEFAULT 'ACTIVE',

    created_by UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_risk_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_risk_control
        FOREIGN KEY (control_id)
        REFERENCES controls(control_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_risk_user
        FOREIGN KEY (created_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);

CREATE TABLE risk_assessments (

    assessment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    risk_id UUID NOT NULL,

    assessor_id UUID NOT NULL,

    assessment_date DATE NOT NULL,

    likelihood INTEGER CHECK (likelihood BETWEEN 1 AND 5),

    impact INTEGER CHECK (impact BETWEEN 1 AND 5),

    risk_score INTEGER,

    comments TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_assessment_risk
        FOREIGN KEY (risk_id)
        REFERENCES risks(risk_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_assessment_user
        FOREIGN KEY (assessor_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE

);

CREATE TABLE risk_treatments (

    treatment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    risk_id UUID NOT NULL,

    owner_id UUID,

    treatment_plan TEXT NOT NULL,

    target_date DATE,

    status risk_status DEFAULT 'OPEN',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_treatment_risk
        FOREIGN KEY (risk_id)
        REFERENCES risks(risk_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_treatment_owner
        FOREIGN KEY (owner_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);

CREATE TABLE evidence (

    evidence_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    tenant_id UUID NOT NULL,

    control_id UUID NOT NULL,

    uploaded_by UUID NOT NULL,

    title VARCHAR(255) NOT NULL,

    description TEXT,

    status tenant_status DEFAULT 'ACTIVE',

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_evidence_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_evidence_control
        FOREIGN KEY (control_id)
        REFERENCES controls(control_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_evidence_user
        FOREIGN KEY (uploaded_by)
        REFERENCES users(user_id)
        ON DELETE CASCADE

);

CREATE TABLE evidence_files (

    file_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    evidence_id UUID NOT NULL,

    file_name VARCHAR(255) NOT NULL,

    file_path TEXT NOT NULL,

    file_size BIGINT,

    file_type VARCHAR(100),

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_file_evidence
        FOREIGN KEY (evidence_id)
        REFERENCES evidence(evidence_id)
        ON DELETE CASCADE

);

CREATE TABLE evidence_reviews (

    review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    evidence_id UUID NOT NULL,

    reviewer_id UUID NOT NULL,

    review_status review_status DEFAULT 'PENDING',

    comments TEXT,

    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_review_evidence
        FOREIGN KEY (evidence_id)
        REFERENCES evidence(evidence_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_review_user
        FOREIGN KEY (reviewer_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE

);

CREATE TABLE audits (

    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    tenant_id UUID NOT NULL,

    framework_id UUID NOT NULL,

    audit_name VARCHAR(255) NOT NULL,

    start_date DATE,

    end_date DATE,

    status audit_status DEFAULT 'PLANNED',

    created_by UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_audit_framework
        FOREIGN KEY (framework_id)
        REFERENCES frameworks(framework_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (created_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);

CREATE TABLE audit_findings (

    finding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    audit_id UUID NOT NULL,

    control_id UUID,

    title VARCHAR(255) NOT NULL,

    description TEXT,

    severity VARCHAR(50)
    CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),

    status VARCHAR(50)
    CHECK (status IN ('OPEN','IN_PROGRESS','CLOSED')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_finding_audit
        FOREIGN KEY (audit_id)
        REFERENCES audits(audit_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_finding_control
        FOREIGN KEY (control_id)
        REFERENCES controls(control_id)
        ON DELETE SET NULL

);

CREATE TABLE audit_evidence (

    audit_evidence_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    finding_id UUID NOT NULL,

    evidence_id UUID NOT NULL,

    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_evidence_finding
        FOREIGN KEY (finding_id)
        REFERENCES audit_findings(finding_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_audit_evidence_evidence
        FOREIGN KEY (evidence_id)
        REFERENCES evidence(evidence_id)
        ON DELETE CASCADE,

    CONSTRAINT unique_finding_evidence
        UNIQUE (finding_id, evidence_id)

);

CREATE TABLE policies (

    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    tenant_id UUID NOT NULL,

    policy_name VARCHAR(255) NOT NULL,

    version VARCHAR(50),

    owner_id UUID,

    effective_date DATE,

    review_date DATE,

    status VARCHAR(50)
    CHECK (status IN ('DRAFT','ACTIVE','ARCHIVED')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_policy_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_policy_owner
        FOREIGN KEY (owner_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);

CREATE TABLE policy_acknowledgements (

    acknowledgement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    policy_id UUID NOT NULL,

    user_id UUID NOT NULL,

    acknowledged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ack_policy
        FOREIGN KEY (policy_id)
        REFERENCES policies(policy_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_ack_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT unique_policy_user
        UNIQUE (policy_id, user_id)

);

CREATE TABLE assets (

    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    tenant_id UUID NOT NULL,

    asset_name VARCHAR(255) NOT NULL,

    asset_type VARCHAR(100),

    owner_id UUID,

    location VARCHAR(255),

    status VARCHAR(50)
    CHECK (status IN ('ACTIVE','INACTIVE','RETIRED')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_asset_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_asset_owner
        FOREIGN KEY (owner_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);

CREATE TABLE vendors (

    vendor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    tenant_id UUID NOT NULL,

    vendor_name VARCHAR(255) NOT NULL,

    contact_email VARCHAR(255),

    risk_level VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_vendor_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE

);

CREATE TABLE tasks (

    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    tenant_id UUID NOT NULL,

    assigned_to UUID,

    title VARCHAR(255) NOT NULL,

    description TEXT,

    due_date DATE,

    status task_status DEFAULT 'OPEN',


    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_task_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_task_user
        FOREIGN KEY (assigned_to)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);  

CREATE TABLE comments (

    comment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    task_id UUID NOT NULL,

    user_id UUID NOT NULL,

    comment TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_comment_task
        FOREIGN KEY (task_id)
        REFERENCES tasks(task_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_comment_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE

);

CREATE TABLE attachments (

    attachment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    task_id UUID NOT NULL,

    uploaded_by UUID,

    file_name VARCHAR(255),

    file_path TEXT,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_attachment_task
        FOREIGN KEY (task_id)
        REFERENCES tasks(task_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_attachment_user
        FOREIGN KEY (uploaded_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);

CREATE TABLE notifications (

    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID NOT NULL,

    title VARCHAR(255),

    message TEXT,

    is_read BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notification_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE

);

CREATE TABLE activity_logs (

    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    tenant_id UUID NOT NULL,

    user_id UUID,

    action VARCHAR(255),

    entity_name VARCHAR(100),

    entity_id UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_log_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_log_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);

CREATE TABLE api_keys (

    api_key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    tenant_id UUID NOT NULL,

    key_name VARCHAR(255),

    api_key TEXT NOT NULL,

    expires_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_api_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON DELETE CASCADE

);


/*
Tenant
│
├── Users
│     ├── Roles
│     ├── Tasks
│     ├── Notifications
│     └── Activity Logs
│
├── Frameworks
│     ├── Versions
│     ├── Control Families
│     └── Controls
│
├── Risks
│     ├── Assessments
│     └── Treatments
│
├── Evidence
│     ├── Files
│     └── Reviews
│
├── Audits
│     ├── Findings
│     └── Audit Evidence
│
├── Policies
├── Assets
└── Vendors
*/

-- USERS
CREATE INDEX idx_users_tenant_id ON users(tenant_id);


-- CONTROLS
CREATE INDEX idx_controls_framework_id ON controls(framework_id);

-- RISKS
CREATE INDEX idx_risks_tenant_id ON risks(tenant_id);
CREATE INDEX idx_risks_control_id ON risks(control_id);

-- EVIDENCE
CREATE INDEX idx_evidence_control_id ON evidence(control_id);

-- AUDITS
CREATE INDEX idx_audits_framework_id ON audits(framework_id);

-- TASKS
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);

-- NOTIFICATIONS
CREATE INDEX idx_notifications_user_id ON notifications(user_id);

-- ACTIVITY LOGS
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_tenant_id ON activity_logs(tenant_id);

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tenants_updated
BEFORE UPDATE ON tenants
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_users_updated
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();



/*==============================================================
=            ROW LEVEL SECURITY (RLS)
==============================================================*/

-- Enable Row Level Security

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE risks ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_treatments ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE audits ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE policy_acknowledgements ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

---------------------------------------------------------------
-- Tenant Isolation Policies
---------------------------------------------------------------

CREATE POLICY tenant_isolation_users
ON users
FOR ALL
USING (
    tenant_id = current_setting('app.current_tenant')::uuid
);

CREATE POLICY tenant_isolation_risks
ON risks
FOR ALL
USING (
    tenant_id = current_setting('app.current_tenant')::uuid
);

CREATE POLICY tenant_isolation_evidence
ON evidence
FOR ALL
USING (
    tenant_id = current_setting('app.current_tenant')::uuid
);

CREATE POLICY tenant_isolation_audits
ON audits
FOR ALL
USING (
    tenant_id = current_setting('app.current_tenant')::uuid
);

CREATE POLICY tenant_isolation_assets
ON assets
FOR ALL
USING (
    tenant_id = current_setting('app.current_tenant')::uuid
);

CREATE POLICY tenant_isolation_vendors
ON vendors
FOR ALL
USING (
    tenant_id = current_setting('app.current_tenant')::uuid
);

CREATE POLICY tenant_isolation_tasks
ON tasks
FOR ALL
USING (
    tenant_id = current_setting('app.current_tenant')::uuid
);
---------------------------------------------------------------
-- FORCE Row Level Security (applies even to table owner)
---------------------------------------------------------------

ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE risks FORCE ROW LEVEL SECURITY;
ALTER TABLE risk_assessments FORCE ROW LEVEL SECURITY;
ALTER TABLE risk_treatments FORCE ROW LEVEL SECURITY;
ALTER TABLE evidence FORCE ROW LEVEL SECURITY;
ALTER TABLE evidence_files FORCE ROW LEVEL SECURITY;
ALTER TABLE evidence_reviews FORCE ROW LEVEL SECURITY;
ALTER TABLE audits FORCE ROW LEVEL SECURITY;
ALTER TABLE audit_findings FORCE ROW LEVEL SECURITY;
ALTER TABLE audit_evidence FORCE ROW LEVEL SECURITY;
ALTER TABLE policies FORCE ROW LEVEL SECURITY;
ALTER TABLE policy_acknowledgements FORCE ROW LEVEL SECURITY;
ALTER TABLE assets FORCE ROW LEVEL SECURITY;
ALTER TABLE vendors FORCE ROW LEVEL SECURITY;
ALTER TABLE tasks FORCE ROW LEVEL SECURITY;
ALTER TABLE comments FORCE ROW LEVEL SECURITY;
ALTER TABLE attachments FORCE ROW LEVEL SECURITY;
ALTER TABLE notifications FORCE ROW LEVEL SECURITY;
ALTER TABLE activity_logs FORCE ROW LEVEL SECURITY;
ALTER TABLE api_keys FORCE ROW LEVEL SECURITY;

---------------------------------------------------------------
-- Missing Tenant Isolation Policies (indirect via parent table)
---------------------------------------------------------------

CREATE POLICY tenant_isolation_risk_assessments ON risk_assessments FOR ALL
USING (risk_id IN (SELECT risk_id FROM risks WHERE tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_risk_treatments ON risk_treatments FOR ALL
USING (risk_id IN (SELECT risk_id FROM risks WHERE tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_evidence_files ON evidence_files FOR ALL
USING (evidence_id IN (SELECT evidence_id FROM evidence WHERE tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_evidence_reviews ON evidence_reviews FOR ALL
USING (evidence_id IN (SELECT evidence_id FROM evidence WHERE tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_audit_findings ON audit_findings FOR ALL
USING (audit_id IN (SELECT audit_id FROM audits WHERE tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_audit_evidence ON audit_evidence FOR ALL
USING (finding_id IN (SELECT finding_id FROM audit_findings af JOIN audits a ON af.audit_id = a.audit_id WHERE a.tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_policies ON policies FOR ALL
USING (tenant_id = current_setting('app.current_tenant')::uuid);

CREATE POLICY tenant_isolation_policy_ack ON policy_acknowledgements FOR ALL
USING (policy_id IN (SELECT policy_id FROM policies WHERE tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_comments ON comments FOR ALL
USING (task_id IN (SELECT task_id FROM tasks WHERE tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_attachments ON attachments FOR ALL
USING (task_id IN (SELECT task_id FROM tasks WHERE tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_notifications ON notifications FOR ALL
USING (user_id IN (SELECT user_id FROM users WHERE tenant_id = current_setting('app.current_tenant')::uuid));

CREATE POLICY tenant_isolation_activity_logs ON activity_logs FOR ALL
USING (tenant_id = current_setting('app.current_tenant')::uuid);

CREATE POLICY tenant_isolation_api_keys ON api_keys FOR ALL
USING (tenant_id = current_setting('app.current_tenant')::uuid);