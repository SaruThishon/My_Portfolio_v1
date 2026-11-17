# Database Schema

All tables use UUID primary keys and timezone-aware timestamps.

## Tables

### admin_users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| username | VARCHAR(50) UNIQUE | |
| email | VARCHAR(255) UNIQUE | |
| hashed_password | TEXT | Argon2id |
| is_active | BOOLEAN | |
| created_at | TIMESTAMPTZ | |
| last_login | TIMESTAMPTZ | nullable |

### admin_sessions
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → admin_users | |
| token_hash | VARCHAR(64) UNIQUE | SHA-256 of session token |
| expires_at | TIMESTAMPTZ | |
| is_valid | BOOLEAN | set false on logout |
| ip_address | VARCHAR(45) | |

### profile (singleton)
Single row storing the owner's public profile.

### projects
| Column | Type | Notes |
|--------|------|-------|
| status | VARCHAR(20) | draft / published |
| is_featured | BOOLEAN | |
| technologies | VARCHAR[] | PostgreSQL array |
| slug | VARCHAR(220) UNIQUE | URL-safe |

### enquiries
| Column | Type | Notes |
|--------|------|-------|
| status | VARCHAR(20) | new / read / replied / archived |
| enquiry_type | VARCHAR(50) | job_opportunity / freelance / collaboration / general / other |

### resumes
One row per uploaded file. `is_active=true` marks the current resume served publicly.

### site_settings
Key-value store with JSONB values. Used for site title, meta description, etc.

### activity_logs
Append-only audit trail. Never stores passwords or tokens.
