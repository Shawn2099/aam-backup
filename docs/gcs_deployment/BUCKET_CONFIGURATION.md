# Bucket Configuration - Google Cloud Storage

**Level**: Beginner to Intermediate  
**Prerequisites**: None  
**Time to Master**: 1-2 weeks of hands-on practice

---

## Table of Contents

1. [Bucket Fundamentals](#bucket-fundamentals)
2. [Storage Classes Deep Dive](#storage-classes-deep-dive)
3. [Location Selection](#location-selection)
4. [Bucket Creation](#bucket-creation)
5. [Versioning Strategies](#versioning-strategies)
6. [Lifecycle Management](#lifecycle-management)
7. [Retention Policies](#retention-policies)
8. [Object Holds](#object-holds)
9. [Soft Delete](#soft-delete)
10. [Naming Conventions](#naming-conventions)
11. [Bucket Lock & Compliance](#bucket-lock--compliance)
12. [Configuration Examples](#configuration-examples)

---

## Bucket Fundamentals

### What is a GCS Bucket?

A GCS bucket is a **logical container** for storing objects (files). Unlike traditional file systems, buckets:
- Have a flat namespace (no true folders, only prefixes)
- Are globally unique within Google Cloud
- Belong to a single project
- Have a defined location and storage class
- Support unlimited objects

### Bucket vs Object

```
Bucket: my-app-data
├── uploads/
│   ├── 2026/04/11/image1.jpg    ← Object (key = "uploads/2026/04/11/image1.jpg")
│   └── 2026/04/11/image2.png    ← Object (key = "uploads/2026/04/11/image2.png")
├── logs/
│   └── app-2026-04-11.log       ← Object (key = "logs/app-2026-04-11.log")
└── config.json                   ← Object (key = "config.json")
```

**Key Insight**: "Folders" are just prefixes in object names. GCS is fundamentally flat.

---

## Storage Classes Deep Dive

### Storage Class Comparison

| Feature | Standard | Nearline | Coldline | Archive |
|---------|----------|----------|----------|---------|
| **Best For** | Hot data, frequent access | Monthly access | Quarterly access | Yearly access |
| **Availability SLA** | 99.99% | 99.9% | 99.85% | 99.8% |
| **Minimum Storage Duration** | None | 30 days | 90 days | 365 days |
| **Retrieval Fees** | None | Per GB | Per GB | Per GB (highest) |
| **Early Deletion Fee** | None | Prorated for <30 days | Prorated for <90 days | Prorated for <365 days |
| **Storage Cost (US-Central1)** | $0.020/GB/mo | $0.010/GB/mo | $0.004/GB/mo | $0.0012/GB/mo |
| **Operation Cost** | Standard | Higher | Higher | Highest |

### When to Use Each Class

#### Standard
```
✅ Active application data
✅ Website content, CDN origin
✅ Analytics data (frequently queried)
✅ Mobile app assets
✅ IoT data ingestion
```

#### Nearline
```
✅ Daily/weekly backups
✅ Data processed monthly
✅ Log archives
✅ Disaster recovery (warm)
✅ Media assets used occasionally
```

#### Coldline
```
✅ Quarterly backups
✅ Data for regulatory review
✅ Long-term log archives
✅ Disaster recovery (cold)
✅ Historical data accessed rarely
```

#### Archive
```
✅ Annual compliance data
✅ Legal hold documents
✅ Historical records
✅ Cold disaster recovery
✅ Data retained for audits
```

### Autoclass

**Autoclass** automatically transitions objects between storage classes based on access patterns.

```bash
# Enable Autoclass
gcloud storage buckets update gs://my-bucket --enable-autoclass

# Disable Autoclass
gcloud storage buckets update gs://my-bucket --disable-autoclass
```

**Terraform**:
```hcl
resource "google_storage_bucket" "with_autoclass" {
  name     = "my-bucket"
  location = "US-CENTRAL1"
  
  autoclass {
    enabled = true
  }
}
```

**When to Use Autoclass**:
- Unpredictable access patterns
- Data with unknown future usage
- Teams without capacity to manage lifecycle rules
- Cost optimization without manual intervention

**When NOT to Use Autoclass**:
- Predictable access patterns (use explicit lifecycle rules)
- Compliance requirements mandate specific storage class
- Need to guarantee minimum storage duration

---

## Location Selection

### Location Types

| Type | Examples | Durability | Use Case | Cost |
|------|----------|------------|----------|------|
| **Multi-region** | `US`, `EU`, `ASIA` | 99.999999999% | Global access, CDN, HA | Highest |
| **Dual-region** | `NAM4`, `EUR4`, `ASIA1` | 99.999999999% | Continental HA, DR | High |
| **Region** | `us-central1`, `europe-west1` | 99.999999999% | Single-region workloads | Standard |
| **Zone** | `us-central1-a`, `europe-west1-b` | 99.999999999% | AI/ML, collocated compute | Lowest |

### Multi-Region Details

```
US: Covers us-central1, us-east1, us-east4, us-west1, us-west2, us-west3, us-west4
EU: Covers europe-north1, europe-southwest1, europe-west1, europe-west2, europe-west3, europe-west4, europe-west6, europe-west8, europe-west9, europe-west12
ASIA: Covers asia-east1, asia-east2, asia-northeast1, asia-northeast2, asia-northeast3, asia-south1, asia-south2, asia-southeast1, asia-southeast2, australia-southeast1
```

**Data Residency**: Multi-region stores data across multiple regions within the geography. Google manages replication.

### Dual-Region Details

```
NAM4: us-east1 + us-west4
NAM7: us-east5 + us-south1
EUR4: europe-west4 + europe-north1
ASIA1: asia-northeast1 + asia-northeast2
```

**Use Cases**:
- HA across regions
- DR with RPO ≈ 0
- Compliance requiring geographic redundancy

### Region Selection Decision Tree

```
Where is your compute?
├── Multiple regions → Multi-region or Dual-region
├── Single region → Same region as compute
└── On-premises → Choose closest region

Do you have data residency requirements?
├── Yes → Choose compliant region (EU for GDPR)
└── No → Optimize for latency/cost

What's your budget?
├── Minimize cost → Zone or Region
├── Balance cost/HA → Dual-region
└── Maximize availability → Multi-region
```

### Critical Rule: Colocate Compute & Storage

**NEVER** place compute and storage in different regions unless required. Cross-region egress costs add up quickly:

```
Example: 10 TB monthly egress from us-central1 to us-east1
- Cross-region egress: $0.01/GB = $100/month
- Same-region egress: FREE
- Annual savings: $1,200
```

---

## Bucket Creation

### Via Cloud Console

1. Navigate to Cloud Storage > Buckets
2. Click "Create Bucket"
3. Configure:
   - Name (globally unique)
   - Location type and region
   - Storage class
   - Access control (uniform vs fine-grained)
4. Click "Create"

### Via gcloud

```bash
# Basic bucket
gsutil mb gs://my-unique-bucket-name

# With location
gsutil mb -l US-CENTRAL1 gs://my-bucket

# With storage class
gsutil mb -c NEARLINE gs://my-backup-bucket

# With location and class
gsutil mb -l US-CENTRAL1 -c STANDARD gs://my-app-data

# Multi-region
gsutil mb -l US gs://my-multi-region-bucket

# Dual-region
gsutil mb -l NAM4 gs://my-dual-region-bucket
```

### Via Terraform

```hcl
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "google_storage_bucket" "main" {
  # Name must be globally unique
  name = "my-app-data-${random_id.bucket_suffix.hex}"
  
  location      = "US-CENTRAL1"
  storage_class = "STANDARD"
  
  # CRITICAL: Enable uniform bucket-level access
  uniform_bucket_level_access = true
  
  # CRITICAL: Prevent public access
  public_access_prevention = "enforced"
  
  # Enable versioning for critical data
  versioning {
    enabled = true
  }
  
  # Optional: Enable autoclass
  # autoclass {
  #   enabled = true
  # }
  
  # Labels for cost tracking
  labels = {
    environment = "production"
    team        = "platform"
    cost-center = "eng-123"
  }
  
  lifecycle {
    prevent_destroy = true  # Prevent accidental deletion
  }
}

output "bucket_name" {
  value = google_storage_bucket.main.name
}
```

### Via Python

```python
from google.cloud import storage

def create_bucket_with_config(bucket_name, location="US-CENTRAL1", storage_class="STANDARD"):
    """Create a bucket with production-ready configuration."""
    storage_client = storage.Client()
    
    bucket = storage_client.create_bucket(
        bucket_name,
        location=location,
        storage_class=storage_class,
    )
    
    # Enable uniform bucket-level access
    bucket.iam_configuration.uniform_bucket_level_access_enabled = True
    bucket.iam_configuration.public_access_prevention = "enforced"
    bucket.patch()
    
    print(f"Created bucket: {bucket.name}")
    print(f"Location: {bucket.location}")
    print(f"Storage Class: {bucket.storage_class}")
    
    return bucket

# Usage
create_bucket_with_config("my-production-bucket-unique-123")
```

### Bucket Naming Rules

```
✅ Valid:
- my-app-data
- my-app-data-prod
- myappdata123
- my-app-data-2026
- logs.myapp.com (domain-style)

❌ Invalid:
- My-Bucket (uppercase)
- my_bucket (underscores)
- my--bucket (consecutive hyphens)
- google (reserved names)
- goole (similar to reserved)

Requirements:
- 3-63 characters
- Lowercase letters, numbers, hyphens, periods
- Start with letter or number
- No "google" or close variants
- Globally unique
```

---

## Versioning Strategies

### What is Object Versioning?

Versioning keeps **all versions** of an object when it's overwritten or deleted:

```
Bucket: my-versioned-bucket
└── config.json
    ├── v1: Created 2026-01-01 (live: false)
    ├── v2: Created 2026-02-15 (live: false)
    └── v3: Created 2026-04-11 (live: true) ← Current version
```

### Enable Versioning

```bash
# Enable
gsutil versioning set on gs://my-bucket

# Disable
gsutil versioning set off gs://my-bucket

# List all versions
gsutil ls -a gs://my-bucket/config.json

# Restore specific version
gsutil cp gs://my-bucket/config.json#1234567890 gs://my-bucket/config.json
```

### Terraform

```hcl
resource "google_storage_bucket" "versioned" {
  name     = "my-versioned-bucket"
  location = "US-CENTRAL1"
  
  versioning {
    enabled = true
  }
}
```

### Versioning Use Cases

| Scenario | Without Versioning | With Versioning |
|----------|-------------------|-----------------|
| Accidental overwrite | Data lost forever | Restore previous version |
| Application bug corrupts data | Data lost | Rollback to good version |
| Compliance requires audit trail | Must implement separately | Built-in |
| Ransomware encrypts objects | All versions encrypted | Restore unencrypted version |

### Versioning Cost Implications

**Storage Costs**: You pay for ALL versions of objects

```
Example: 100 GB object updated daily for 30 days
- Total stored: 100 GB × 30 versions = 3,000 GB
- Monthly cost (Standard): 3,000 GB × $0.020 = $60
- Without versioning: 100 GB × $0.020 = $2
```

**Mitigation**:
- Use lifecycle rules to delete old versions
- Only enable versioning for critical buckets
- Monitor version count with Cloud Monitoring

### List and Manage Versions (Python)

```python
from google.cloud import storage

def list_object_versions(bucket_name, blob_name):
    """List all versions of an object."""
    client = storage.Client()
    blobs = client.list_blobs(bucket_name, prefix=blob_name, versions=True)
    
    for blob in blobs:
        if blob.name == blob_name:
            print(f"Version: {blob.generation}")
            print(f"Created: {blob.time_created}")
            print(f"Size: {blob.size} bytes")
            print(f"Is Live: {blob.time_deleted is None}")
            print("---")

def restore_object_version(bucket_name, blob_name, source_generation):
    """Restore a specific version of an object."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Copy old version to live
    source_blob = bucket.blob(blob_name, generation=source_generation)
    bucket.copy_blob(source_blob, bucket, new_name=blob_name)
    
    print(f"Restored {blob_name} from generation {source_generation}")

# Usage
list_object_versions("my-bucket", "config.json")
restore_object_version("my-bucket", "config.json", 1234567890)
```

---

## Lifecycle Management

### What is Lifecycle Management?

Lifecycle rules **automatically** transition or delete objects based on conditions:

```json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 90}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365}
    }
  ]
}
```

### Lifecycle Rule Components

#### Actions

| Action | Description | Example |
|--------|-------------|---------|
| `Delete` | Permanently delete object | Remove old logs |
| `SetStorageClass` | Change storage class | Standard → Nearline after 90 days |
| `AbortIncompleteMultipartUpload` | Clean up failed uploads | Delete incomplete uploads after 7 days |
| `SetRetentionPolicy` | Apply retention (rare) | Compliance scenarios |

#### Conditions

| Condition | Type | Description | Example |
|-----------|------|-------------|---------|
| `age` | Integer | Days since object creation | `{"age": 90}` |
| `createdBefore` | Date (YYYY-MM-DD) | Objects created before date | `{"createdBefore": "2025-01-01"}` |
| `withState` | String | Live/noncurrent (versioning) | `{"withState": "LIVE"}` |
| `matchesStorageClass` | Array | Match specific storage class | `{"matchesStorageClass": ["STANDARD"]}` |
| `numNewerVersions` | Integer | Keep N newer versions | `{"numNewerVersions": 3}` |
| `daysSinceCustomTime` | Integer | Days since custom timestamp | `{"daysSinceCustomTime": 180}` |
| `daysSinceNoncurrentTime` | Integer | Days since object became noncurrent | `{"daysSinceNoncurrentTime": 30}` |

### Common Lifecycle Patterns

#### Pattern 1: Log Retention

```json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 30}
    },
    {
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 90}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365}
    }
  ]
}
```

**Explanation**:
- Days 0-30: Standard (fast access for recent logs)
- Days 30-90: Nearline (monthly access)
- Days 90-365: Coldline (quarterly access)
- Day 365+: Deleted

#### Pattern 2: Backup Retention with Versioning

```json
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {
        "age": 90,
        "numNewerVersions": 5,
        "withState": "NONCURRENT"
      }
    },
    {
      "action": {"type": "AbortIncompleteMultipartUpload"},
      "condition": {"age": 7}
    }
  ]
}
```

**Explanation**:
- Delete noncurrent versions older than 90 days IF 5+ newer versions exist
- Clean up incomplete multipart uploads after 7 days

#### Pattern 3: Upload Bucket Cleanup

```json
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {
        "age": 30,
        "matchesStorageClass": ["STANDARD", "NEARLINE"]
      }
    }
  ]
}
```

**Explanation**: Delete all objects older than 30 days (useful for temporary upload buckets)

### Apply Lifecycle Rules

```bash
# Create lifecycle.json
cat > lifecycle.json << 'EOF'
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 90}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365}
    }
  ]
}
EOF

# Apply to bucket
gsutil lifecycle set lifecycle.json gs://my-bucket

# View current rules
gsutil lifecycle get gs://my-bucket

# Remove all rules
gsutil lifecycle set /dev/null gs://my-bucket
```

### Terraform Lifecycle Rules

```hcl
resource "google_storage_bucket" "with_lifecycle" {
  name     = "my-bucket"
  location = "US-CENTRAL1"
  
  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 90
    }
  }
  
  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
    condition {
      age = 180
    }
  }
  
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }
  
  lifecycle_rule {
    action {
      type = "AbortIncompleteMultipartUpload"
    }
    condition {
      age = 7
    }
  }
}
```

### Lifecycle Rule Testing

```bash
# Simulate lifecycle (doesn't actually delete)
gsutil lifecycle get gs://my-bucket

# Check object ages
gsutil ls -l gs://my-bucket/** | awk '{print $1, $2}'

# Monitor lifecycle actions via logs
gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.methodName:storage.objects.delete" \
  --limit=20
```

---

## Retention Policies

### What is a Retention Policy?

A retention policy **prevents deletion or modification** of objects for a specified period. Unlike lifecycle rules, retention policies can be **locked** (immutable).

### Retention Policy Configuration

```bash
# Set retention policy (60 seconds = 1 minute for testing)
gcloud storage buckets update gs://my-bucket \
  --retention-period=60

# Set retention policy (30 days)
gcloud storage buckets update gs://my-bucket \
  --retention-period=2592000

# Lock retention policy (IRREVERSIBLE)
gcloud storage buckets update gs://my-bucket \
  --retention-period=2592000 \
  --lock-retention-policy

# View retention policy
gcloud storage buckets describe gs://my-bucket \
  --format="yaml(retentionPolicy)"
```

### Retention Policy States

| State | Description | Can Remove? | Can Decrease Period? |
|-------|-------------|-------------|---------------------|
| **Unlocked** | Policy set but not locked | ✅ Yes | ✅ Yes |
| **Locked** | Policy is permanent | ❌ No | ❌ No (can only increase) |

**WARNING**: Locking a retention policy is **IRREVERSIBLE**. The bucket cannot be deleted until all objects meet the retention period.

### Retention Period Format

```
Seconds: 2592000 (30 days)
Maximum: 3155760000 (100 years)

gcloud duration format:
- P30D (30 days)
- P1Y (1 year)
- P2Y6M (2 years, 6 months)
```

### Retention Policy with Terraform

```hcl
resource "google_storage_bucket" "with_retention" {
  name     = "my-compliance-bucket"
  location = "US-CENTRAL1"
  
  # Unlocked retention (can be removed)
  retention_policy {
    retention_period = 2592000  # 30 days
    is_locked        = false
  }
}

resource "google_storage_bucket" "with_locked_retention" {
  name     = "my-immutable-bucket"
  location = "US-CENTRAL1"
  
  # Locked retention (IRREVERSIBLE)
  retention_policy {
    retention_period = 2592000  # 30 days
    is_locked        = true
  }
}
```

### Retention Policy Use Cases

| Scenario | Period | Locked? | Why |
|----------|--------|---------|-----|
| SEC compliance | 7 years | ✅ Yes | Regulatory requirement |
| Financial records | 5 years | ✅ Yes | Audit requirements |
| Healthcare data | 6 years | ✅ Yes | HIPAA requirements |
| Application logs | 90 days | ❌ No | Operational need |
| User uploads | 30 days | ❌ No | Business policy |

---

## Object Holds

### What are Object Holds?

Holds **prevent deletion** of specific objects, overriding lifecycle rules and retention policies.

### Hold Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Event-based hold** | Holds object until event occurs | Legal hold, investigation |
| **Temporary hold** | Holds object until manually released | Short-term retention extension |

### Manage Holds (gcloud)

```bash
# Set event-based hold on object
gcloud storage objects update gs://my-bucket/evidence.zip \
  --event-based-hold

# Release event-based hold
gcloud storage objects update gs://my-bucket/evidence.zip \
  --no-event-based-hold

# Set temporary hold
gcloud storage objects update gs://my-bucket/important-data.json \
  --temporary-hold

# Release temporary hold
gcloud storage objects update gs://my-bucket/important-data.json \
  --no-temporary-hold

# View holds on object
gcloud storage objects describe gs://my-bucket/evidence.zip \
  --format="yaml(eventBasedHold,temporaryHold)"
```

### Manage Holds (Python)

```python
from google.cloud import storage

def set_event_based_hold(bucket_name, blob_name):
    """Set event-based hold on an object."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    blob.event_based_hold = True
    blob.patch()
    
    print(f"Event-based hold set on {blob_name}")

def release_event_based_hold(bucket_name, blob_name):
    """Release event-based hold."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    blob.event_based_hold = False
    blob.patch()
    
    print(f"Event-based hold released on {blob_name}")

# Usage
set_event_based_hold("my-bucket", "legal-evidence.zip")
# ... investigation complete ...
release_event_based_hold("my-bucket", "legal-evidence.zip")
```

### Event-based Hold Workflow

```
1. Enable default event-based hold on bucket
   ↓
2. All new objects automatically get event-based hold
   ↓
3. Object retained indefinitely (ignores lifecycle/retention)
   ↓
4. Release event-based hold when event occurs
   ↓
5. Normal lifecycle/retention rules resume
```

```bash
# Enable default event-based hold on bucket
gcloud storage buckets update gs://my-bucket \
  --default-event-based-hold

# Disable
gcloud storage buckets update gs://my-bucket \
  --no-default-event-based-hold
```

---

## Soft Delete

### What is Soft Delete?

Soft Delete **retains deleted objects** for a configurable period, allowing recovery.

```bash
# Enable soft delete (7 days)
gcloud storage buckets update gs://my-bucket \
  --soft-delete-duration=7d

# Disable soft delete
gcloud storage buckets update gs://my-bucket \
  --clear-soft-delete-duration

# List soft-deleted objects
gsutil ls -a gs://my-bucket/**

# Restore soft-deleted object
gsutil cp gs://my-bucket/object#1234567890 gs://my-bucket/object
```

### Terraform

```hcl
resource "google_storage_bucket" "with_soft_delete" {
  name     = "my-bucket"
  location = "US-CENTRAL1"
  
  soft_delete_policy {
    retention_duration_seconds = 604800  # 7 days
  }
}
```

### Soft Delete vs Versioning

| Feature | Soft Delete | Versioning |
|---------|-------------|------------|
| **Retains** | Deleted objects | All versions (overwrites + deletes) |
| **Recovery** | Yes | Yes |
| **Cost** | Pay for retained objects | Pay for all versions |
| **Use Case** | Accident recovery | Full history, audit trail |

**Recommendation**: Use soft delete for accident recovery, versioning for audit/compliance.

---

## Naming Conventions

### Bucket Naming Best Practices

```
Format: {application}-{environment}-{data-type}-{optional-region}

Examples:
✅ payments-prod-transactions-us
✅ analytics-staging-events
✅ ml-training-prod-datasets
✅ user-uploads-prod-images
```

### Object Naming Best Practices

```
Format: {category}/{subcategory}/{date}/{unique-id}.{ext}

Examples:
✅ uploads/images/2026/04/11/user123-avatar.jpg
✅ logs/application/2026/04/app-20260411.log
✅ backups/database/2026/04/11/db-snapshot-001.sql.gz
✅ reports/financial/2026/Q1/revenue-report.pdf

Avoid:
❌ image.jpg (no context, collisions)
❌ 2026-04-11-log.txt (no category)
 uploads/my file with spaces.txt (use hyphens)
❌ Logs/APP.LOG (use lowercase)
```

### Preventing Hotspots

**Problem**: Sequential naming causes uneven load on servers.

```
❌ Bad (sequential):
sensor-data/000001.json
sensor-data/000002.json
sensor-data/000003.json

✅ Good (hash prefix):
sensor-data/01/abc123.json
sensor-data/02/def456.json
sensor-data/03/ghi789.json

✅ Good (date-based):
sensor-data/2026/04/11/reading-001.json
sensor-data/2026/04/11/reading-002.json
```

---

## Bucket Lock & Compliance

### Compliance Scenarios

| Regulation | Requirement | GCS Feature |
|------------|-------------|-------------|
| **SEC 17a-4** | WORM storage, 3-6 year retention | Locked retention policy |
| **FINRA** | Immutable records | Locked retention + event-based hold |
| **HIPAA** | Data protection, audit trail | CMEK + audit logging + retention |
| **GDPR** | Right to erasure (with exceptions) | Lifecycle + holds for legal exceptions |

### Implementing WORM (Write Once, Read Many)

```bash
# Create bucket with locked retention
gsutil mb -l US-CENTRAL1 gs://worm-compliance-bucket

# Set and lock retention (1 year = 31536000 seconds)
gcloud storage buckets update gs://worm-compliance-bucket \
  --retention-period=31536000 \
  --lock-retention-policy

# Verify lock
gcloud storage buckets describe gs://worm-compliance-bucket \
  --format="value(retentionPolicy.isLocked)"
```

Once locked:
- ❌ Cannot delete bucket until all objects expire
- ❌ Cannot remove retention policy
- ❌ Cannot decrease retention period
- ❌ Cannot delete objects before retention expires
- ✅ Can increase retention period
- ✅ Can still add objects

---

## Configuration Examples

### Production Application Bucket

```hcl
resource "google_storage_bucket" "prod_app_data" {
  name     = "payments-prod-transactions-us"
  location = "US-CENTRAL1"
  
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  
  versioning {
    enabled = true
  }
  
  # Lifecycle: Standard → Nearline → Delete
  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 90
    }
  }
  
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }
  
  # Clean up incomplete uploads
  lifecycle_rule {
    action {
      type = "AbortIncompleteMultipartUpload"
    }
    condition {
      age = 7
    }
  }
  
  labels = {
    environment = "production"
    application = "payments"
    team        = "transactions"
  }
}
```

### Backup Bucket with DR

```hcl
resource "google_storage_bucket" "backup_dr" {
  name     = "app-prod-backups-dr"
  location = "NAM4"  # Dual-region for DR
  
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  
  versioning {
    enabled = true
  }
  
  # Keep 5 versions, delete after 90 days
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 5
      with_state         = "NONCURRENT"
      age                = 90
    }
  }
  
  # Enable soft delete for accident recovery
  soft_delete_policy {
    retention_duration_seconds = 604800  # 7 days
  }
}
```

### Log Archive Bucket

```hcl
resource "google_storage_bucket" "log_archive" {
  name     = "platform-prod-logs-archive"
  location = "US-CENTRAL1"
  
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  storage_class               = "COLDLINE"
  
  # Lifecycle: COLDLINE → ARCHIVE → Delete
  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
    condition {
      age = 180
    }
  }
  
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 2555  # 7 years
    }
  }
  
  # Compliance: 7-year retention
  retention_policy {
    retention_period = 220752000  # 7 years in seconds
    is_locked        = true
  }
}
```

---

## Request Preconditions (Write Conflict Prevention)

### What are Request Preconditions?

Request preconditions prevent **accidental overwrites** and **lost updates** by ensuring operations only succeed if specific conditions are met:

```
Scenario Without Preconditions:
User A reads config.json (v1)
User B reads config.json (v1)
User A writes config.json (v2)
User B writes config.json (v2) ← OVERWRITES User A's changes!

Scenario With Preconditions:
User A reads config.json (generation=12345)
User B reads config.json (generation=12345)
User A writes with ifGenerationMatch=12345 ← SUCCESS (generation matches)
User B writes with ifGenerationMatch=12345 ← FAILS (generation is now 12346)
```

### Precondition Types

| Precondition | Purpose | Use Case |
|--------------|---------|----------|
| `ifGenerationMatch` | Object exists AND generation matches | Prevent overwrites |
| `ifGenerationNotMatch` | Object generation doesn't match | Skip known versions |
| `ifMetagenerationMatch` | Metadata version matches | Prevent metadata conflicts |
| `ifMetagenerationNotMatch` | Metadata version doesn't match | Skip known metadata |
| `ifSourceGenerationMatch` | Source object generation matches | Safe copy operations |

### Generation vs Metageneration

```
Generation: Changes when object DATA changes
- Upload new content → New generation
- Replace object → New generation
- Delete object → New generation (tombstone)

Metageneration: Changes when object METADATA changes
- Update custom metadata → New metageneration
- Update content-type → New metageneration
- Update ACL → New metageneration
- Replacing data → Resets metageneration to 1
```

### Using Preconditions (Python)

```python
from google.cloud import storage
from google.api_core import exceptions

client = storage.Client()
bucket = client.bucket("my-bucket")
blob = bucket.blob("config.json")

# Get current generation
blob.reload()
current_generation = blob.generation
print(f"Current generation: {current_generation}")

# Update with precondition (fails if generation changed)
try:
    blob.upload_from_string(
        '{"version": "2.0"}',
        if_generation_match=current_generation
    )
    print("Update succeeded")
except exceptions.PreconditionFailed:
    print("Precondition failed: object was modified by another process")
    # Re-read and retry
    blob.reload()
    blob.upload_from_string(
        '{"version": "2.0"}',
        if_generation_match=blob.generation
    )

# Create only if object doesn't exist
new_blob = bucket.blob("new-file.txt")
try:
    new_blob.upload_from_string(
        "New content",
        if_generation_match=0  # 0 = object must not exist
    )
except exceptions.PreconditionFailed:
    print("Object already exists")

# Update metadata with metageneration precondition
blob.reload()
blob.metadata = {"updated-by": "user-a"}
blob.patch(if_metageneration_match=blob.metageneration)
```

### Using Preconditions (gcloud)

```bash
# Get object generation
gcloud storage objects describe gs://my-bucket/config.json \
  --format="yaml(generation,metageneration)"

# Upload with precondition (JSON API)
curl -X POST \
  "https://storage.googleapis.com/upload/storage/v1/b/my-bucket/o?ifGenerationMatch=12345" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "config.json"}'

# Copy with source generation precondition
gcloud storage cp gs://my-bucket/source.txt gs://my-bucket/dest.txt \
  --if-source-generation-match=12345
```

### Using Preconditions (Terraform)

```hcl
# Terraform automatically handles preconditions for state consistency
# But you can use lifecycle rules to prevent accidental changes

resource "google_storage_bucket_object" "config" {
  name   = "config.json"
  bucket = google_storage_bucket.main.name
  content = jsonencode({
    version = "2.0"
  })
  
  # Prevent if generation changes
  lifecycle {
    prevent_destroy = true
  }
}
```

### When to Use Preconditions

| Scenario | Use Precondition? | Which One |
|----------|-------------------|-----------|
| Config file updates | ✅ Yes | `ifGenerationMatch` |
| Log file creation | ✅ Yes | `ifGenerationMatch=0` (create-only) |
| Metadata updates | ✅ Yes | `ifMetagenerationMatch` |
| Copy operations | ✅ Yes | `ifSourceGenerationMatch` |
| Overwrite is acceptable | ❌ No | None needed |
| Idempotent operations | ❌ No | Object naming handles this |

### Retry Logic with Preconditions

```python
from google.cloud import storage
from google.api_core import exceptions
import time

def update_with_retry(bucket_name, blob_name, content, max_retries=3):
    """Update object with precondition and retry on conflict."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    for attempt in range(max_retries):
        try:
            # Get current generation
            blob.reload()
            generation = blob.generation
            
            # Try update with precondition
            blob.upload_from_string(
                content,
                if_generation_match=generation
            )
            return True  # Success
            
        except exceptions.PreconditionFailed:
            if attempt < max_retries - 1:
                # Wait and retry (exponential backoff)
                wait_time = 2 ** attempt * 0.5
                time.sleep(wait_time)
                print(f"Conflict, retrying in {wait_time}s...")
            else:
                print(f"Failed after {max_retries} retries")
                raise

# Usage
update_with_retry("my-bucket", "config.json", '{"version": "3.0"}')
```

---

## Strong Consistency

### GCS is Strongly Consistent

**As of December 2020, GCS provides STRONG consistency for all operations:**

```
What This Means:
✅ Read after write: Immediately see latest version
✅ Read after delete: Immediately see deletion
✅ List after write: Immediately see new objects
✅ List after delete: Immediately see removed objects
✅ No eventual consistency delays

Before December 2020:
⚠️ Read after overwrite: Could return old version temporarily
⚠️ List after write: Could miss recently created objects
```

### Strong Consistency Implications

```python
# This ALWAYS works now (no eventual consistency delays)
from google.cloud import storage

client = storage.Client()
bucket = client.bucket("my-bucket")

# Upload
blob = bucket.blob("data.json")
blob.upload_from_string('{"key": "value"}')

# Immediately read back (will always get latest)
content = blob.download_as_text()
assert content == '{"key": "value"}'  # Always passes

# Delete
blob.delete()

# Immediately verify deletion (will always fail)
try:
    blob.download_as_text()
    assert False  # Should never reach here
except Exception:
    pass  # Expected: object is gone
```

### Strong Consistency + Preconditions

```
Strong consistency means preconditions work reliably:
- ifGenerationMatch will fail immediately if generation changed
- No window where stale reads could succeed
- No need for retry delays due to consistency (only for conflicts)
```

---

## Quick Reference Commands

```bash
# Create bucket with all settings
gsutil mb -l US-CENTRAL1 -c STANDARD gs://my-bucket
gsutil versioning set on gs://my-bucket
gsutil lifecycle set lifecycle.json gs://my-bucket
gcloud storage buckets update gs://my-bucket --uniform-bucket-level-access
gcloud storage buckets update gs://my-bucket --public-access-prevention=enforced

# View bucket configuration
gcloud storage buckets describe gs://my-bucket

# Test bucket accessibility
gsutil ls gs://my-bucket

# Upload with metadata
gsutil -h "Cache-Control:public, max-age=3600" cp file.txt gs://my-bucket/

# Set object custom time (for lifecycle rules)
gcloud storage objects update gs://my-bucket/file.txt \
  --custom-time=2026-04-11T00:00:00Z
```

---

*"Buckets are forever (or until someone deletes them). Configure carefully, version critical data, and automate lifecycle management."* — Storage Engineer Wisdom
