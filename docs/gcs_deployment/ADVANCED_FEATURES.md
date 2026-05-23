# Advanced Features - Google Cloud Storage

**Level**: Expert  
**Prerequisites**: All previous documents  
**Time to Master**: 4-6 weeks of enterprise implementations

---

## Table of Contents

1. [Organization Policies](#organization-policies)
2. [VPC Service Controls Deep Dive](#vpc-service-controls-deep-dive)
3. [Cross-Project Access Patterns](#cross-project-access-patterns)
4. [CORS Configuration](#cors-configuration)
5. [Object Metadata Strategies](#object-metadata-strategies)
6. [Notifications & Event-Driven Architecture](#notifications--event-driven-architecture)
7. [Integration with GCP Services](#integration-with-gcp-services)
8. [Zonal Buckets for AI/ML](#zonal-buckets-for-aiml)
9. **Hierarchical Namespace**
10. [Object Tags](#object-tags)
11. [Multi-Region Turbo Replication](#multi-region-turbo-replication)
12. [Transfer Service Advanced](#transfer-service-advanced)
13. [Security Edge Cases](#security-edge-cases)
14. [Compliance Implementations](#compliance-implementations)

---

## Organization Policies

### GCS-Specific Org Policies

| Constraint | Purpose | Recommended Value |
|------------|---------|-------------------|
| `storage.publicAccessPrevention` | Prevent public buckets | Enforce for all projects |
| `storage.uniformBucketLevelAccess` | Force uniform access | Enforce |
| `storage.locationRestriction` | Restrict bucket locations | Allowed regions only |
| `storage.retentionPolicyRestriction` | Require retention policies | Min 30 days for prod |

### Enforce via Terraform

```hcl
# Prevent public buckets organization-wide
resource "google_org_policy_policy" "no_public_buckets" {
  name   = "projects/${var.project_id}/policies/storage.publicAccessPrevention"
  parent = "projects/${var.project_id}"
  
  spec {
    rules {
      enforce = "TRUE"
    }
  }
}

# Restrict bucket locations
resource "google_org_policy_policy" "location_restriction" {
  name   = "organizations/${var.org_id}/policies/storage.locationRestriction"
  parent = "organizations/${var.org_id}"
  
  spec {
    rules {
      enforce = "TRUE"
      condition {
        expression = "resource.location in ['us-central1', 'us-east1', 'us-west1']"
      }
    }
  }
}

# Require uniform bucket-level access
resource "google_org_policy_policy" "uniform_access" {
  name   = "organizations/${var.org_id}/policies/storage.uniformBucketLevelAccess"
  parent = "organizations/${var.org_id}"
  
  spec {
    rules {
      enforce = "TRUE"
    }
  }
}
```

### List Org Policies

```bash
gcloud org-policies list --project=my-project
gcloud org-policies describe storage.publicAccessPrevention --project=my-project
```

---

## VPC Service Controls Deep Dive

### Architecture

```
┌─────────────────────────────────────┐
│         Service Perimeter           │
│  ┌───────────────────────────────┐  │
│  │   VPC Network                 │  │
│  │   ┌─────────────────────┐     │  │
│  │   │  GCS Buckets        │     │  │
│  │   │  BigQuery Datasets  │     │  │
│  │   │  Cloud Functions    │     │  │
│  │   └─────────────────────┘     │  │
│  └───────────────────────────────┘  │
│                                     │
│  Access Levels:                     │
│  - IP ranges                        │
│  - Device policy                    │
│  - Identity                         │
└─────────────────────────────────────┘
```

### Configuration

```bash
# Create access context manager policy
gcloud access-context-manager policies create \
  --organization=ORG_ID \
  --title="Default Policy"

# Create access level
gcloud access-context-manager levels create "trusted-networks" \
  --title="Trusted Networks" \
  --basic-level-spec=access-level.yaml \
  --policy=POLICY_ID
```

```yaml
# access-level.yaml
- ipSubnetworks:
  - 10.0.0.0/8
  - 172.16.0.0/12
- requiredAccessLevels:
  - "corporate-devices"
```

### Create Perimeter

```bash
gcloud access-context-manager perimeters create "gcs-perimeter" \
  --title="GCS Data Perimeter" \
  --description="Protects sensitive GCS buckets" \
  --resources=projects/123456789012 \
  --restricted-services=storage.googleapis.com \
  --access-levels=trusted-networks \
  --policy=POLICY_ID
```

### Perimeter Bridge (Cross-Perimeter Access)

```bash
gcloud access-context-manager access-policies create \
  --title="Bridge GCS to BigQuery" \
  --perimeters="gcs-perimeter,bq-perimeter" \
  --policy=POLICY_ID
```

### Testing Perimeters

```bash
# Test access from within perimeter (should succeed)
gsutil ls gs://protected-bucket

# Test access from outside perimeter (should fail)
gsutil ls gs://protected-bucket
# Error: Request is prohibited by organization's ingress VPC Service Controls policy
```

---

## Cross-Project Access Patterns

### Pattern 1: Shared Bucket

```
Project A (Data Producer) ──writes──> Shared Bucket
Project B (Data Consumer) ──reads──> Shared Bucket
```

```hcl
# In Project A (bucket owner)
resource "google_storage_bucket" "shared" {
  name = "shared-data-bucket"
}

resource "google_storage_bucket_iam_member" "project_b_access" {
  bucket = google_storage_bucket.shared.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:project-b-sa@project-b.iam.gserviceaccount.com"
}

# In Project B (consumer)
data "google_storage_bucket" "shared" {
  name = "shared-data-bucket"
}

# Use bucket with cross-project SA
provider "google" {
  alias   = "project_a"
  project = "project-a"
}
```

### Pattern 2: Cross-Project Replication

```bash
# Use Storage Transfer Service for cross-project replication
gcloud storage transfer jobs create \
  gs://source-bucket gs://dest-bucket \
  --source-project=project-a \
  --dest-project=project-b \
  --schedule-daily=02:00
```

### Pattern 3: Centralized Logging

```
Project A (App) ──writes logs──> Project B (Central Logs)
Project C (App) ──writes logs──> Project B (Central Logs)
```

```hcl
# Central log bucket (Project B)
resource "google_storage_bucket" "central_logs" {
  name     = "central-logs-org"
  location = "US-CENTRAL1"
  
  # Only allow writes from specific SAs
  uniform_bucket_level_access    = true
  public_access_prevention       = "enforced"
}

# Grant write access to app projects
resource "google_storage_bucket_iam_member" "app_a_writer" {
  bucket = google_storage_bucket.central_logs.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:app-a@project-a.iam.gserviceaccount.com"
}
```

---

## CORS Configuration

### CORS for Web Applications

```json
// cors-config.json
[
  {
    "origin": ["https://myapp.example.com"],
    "method": ["GET", "HEAD", "PUT", "POST", "DELETE"],
    "responseHeader": ["Content-Type", "Authorization", "Content-Disposition"],
    "maxAgeSeconds": 3600
  }
]
```

```bash
# Apply CORS configuration
gsutil cors set cors-config.json gs://my-bucket

# View current CORS
gsutil cors get gs://my-bucket

# Remove CORS
gsutil cors set /dev/null gs://my-bucket
```

### Terraform CORS

```hcl
resource "google_storage_bucket" "web_assets" {
  name     = "my-web-assets"
  location = "US-CENTRAL1"
  
  cors {
    origin          = ["https://myapp.example.com"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type", "Cache-Control"]
    max_age_seconds = 3600
  }
  
  cors {
    origin          = ["https://admin.myapp.example.com"]
    method          = ["GET", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 7200
  }
}
```

### CORS for Direct Browser Uploads

```json
[
  {
    "origin": ["*"],
    "method": ["PUT", "POST"],
    "responseHeader": ["*"],
    "maxAgeSeconds": 3600
  }
]
```

---

## Object Metadata Strategies

### System Metadata

| Metadata | Description | Immutable |
|----------|-------------|-----------|
| `content_type` | MIME type | No |
| `content_encoding` | Encoding (gzip) | No |
| `content_disposition` | Download behavior | No |
| `cache_control` | CDN caching directives | No |
| `storage_class` | Storage class | No |
| `time_created` | Creation time | ✅ Yes |
| `generation` | Version identifier | ✅ Yes |
| `metageneration` | Metadata version | ✅ Yes |

### Custom Metadata

```python
from google.cloud import storage

def upload_with_metadata(bucket_name, source_file, destination_blob):
    """Upload object with custom metadata."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    
    # System metadata
    blob.content_type = "application/json"
    blob.content_encoding = "gzip"
    blob.cache_control = "public, max-age=3600"
    
    # Custom metadata (application-specific)
    blob.metadata = {
        "uploaded-by": "user-123",
        "source": "mobile-app",
        "version": "2.0",
        "environment": "production"
    }
    
    blob.upload_from_filename(source_file)
    print(f"Uploaded with metadata: {blob.metadata}")
```

### Query by Metadata

```python
from google.cloud import storage

def find_by_metadata(bucket_name, key, value):
    """Find objects by custom metadata."""
    client = storage.Client()
    blobs = client.list_blobs(bucket_name)
    
    results = []
    for blob in blobs:
        if blob.metadata and blob.metadata.get(key) == value:
            results.append(blob)
    
    return results

# Usage
uploads = find_by_metadata("my-bucket", "uploaded-by", "user-123")
print(f"Found {len(uploads)} uploads from user-123")
```

---

## Notifications & Event-Driven Architecture

### Pub/Sub Notifications

```bash
# Create Pub/Sub topic
gcloud pubsub topics create gcs-events

# Create notification on bucket
gsutil notification create -t gcs-events -f json gs://my-bucket

# List notifications
gsutil notification list gs://my-bucket

# Delete notification
gsutil notification delete projects/_/buckets/my-bucket/notificationConfigs/1
```

### Event Types

| Event | Trigger | Use Case |
|-------|---------|----------|
| `OBJECT_FINALIZE` | Object uploaded | Trigger processing pipeline |
| `OBJECT_DELETE` | Object deleted | Cleanup related resources |
| `OBJECT_ARCHIVE` | Object archived | Audit logging |
| `OBJECT_METADATA_UPDATE` | Metadata changed | Index updates |

### Terraform Notification

```hcl
resource "google_pubsub_topic" "gcs_events" {
  name = "gcs-events"
}

resource "google_storage_notification" "notification" {
  bucket         = google_storage_bucket.main.name
  payload_format = "JSON_API_V1"
  topic          = google_pubsub_topic.gcs_events.id
  event_types    = ["OBJECT_FINALIZE", "OBJECT_DELETE"]
  
  depends_on = [google_pubsub_topic_iam_member.binding]
}

resource "google_pubsub_topic_iam_member" "binding" {
  topic  = google_pubsub_topic.gcs_events.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:service-${data.google_project.current.number}@gs-project-accounts.iam.gserviceaccount.com"
}
```

### Cloud Functions Integration

```python
# functions/main.py
from google.cloud import storage
import functions_framework

@functions_framework.cloud_event
def on_gcs_event(cloud_event):
    """Handle GCS events."""
    data = cloud_event.data
    
    bucket = data["bucket"]
    name = data["name"]
    event_type = cloud_event.type
    
    if event_type == "google.cloud.storage.object.v1.finalized":
        process_new_object(bucket, name)
    elif event_type == "google.cloud.storage.object.v1.deleted":
        cleanup_deleted_object(bucket, name)

def process_new_object(bucket, name):
    """Process newly uploaded object."""
    print(f"Processing gs://{bucket}/{name}")
    # Add processing logic here
```

```hcl
resource "google_cloudfunctions2_function" "gcs_handler" {
  name        = "gcs-event-handler"
  location    = "us-central1"
  description = "Handle GCS events"
  
  build_config {
    runtime     = "python311"
    entry_point = "on_gcs_event"
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = "functions.zip"
      }
    }
  }
  
  service_config {
    max_instance_count = 100
    available_memory   = "256M"
    timeout_seconds    = 60
  }
  
  event_trigger {
    trigger_region = "us-central1"
    event_type     = "google.cloud.storage.object.v1.finalized"
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}
```

---

## Integration with GCP Services

### BigQuery External Tables

```sql
-- Query GCS data directly from BigQuery
CREATE OR REPLACE EXTERNAL TABLE `my-project.my_dataset.gcs_logs`
OPTIONS (
  format = 'JSON',
  uris = ['gs://my-bucket/logs/*.json']
);

-- Query
SELECT * FROM `my-project.my_dataset.gcs_logs`
WHERE DATE(timestamp) = '2026-04-11'
LIMIT 100;
```

```hcl
resource "google_bigquery_table" "external" {
  dataset_id = google_bigquery_dataset.main.dataset_id
  table_id   = "gcs_logs"
  
  external_data_configuration {
    autodetect    = true
    source_format = "NEWLINE_DELIMITED_JSON"
    
    source_uris = [
      "gs://my-bucket/logs/*.json"
    ]
  }
}
```

### Cloud Run Integration

```python
# Cloud Run service processing GCS uploads
from flask import Flask, request
from google.cloud import storage
import os

app = Flask(__name__)

@app.route("/", methods=["POST"])
def process_upload():
    """Process GCS upload notification."""
    data = request.get_json()
    bucket = data["bucket"]
    name = data["name"]
    
    # Process file
    client = storage.Client()
    blob = client.bucket(bucket).blob(name)
    content = blob.download_as_text()
    
    # Process and store results
    result = process_data(content)
    
    return {"status": "success"}, 200
```

### Vertex AI Integration

```python
from google.cloud import aiplatform
from google.cloud import storage

def train_model_from_gcs(bucket_name, prefix):
    """Train ML model using data from GCS."""
    # Initialize Vertex AI
    aiplatform.init(project="my-project", location="us-central1")
    
    # Create dataset from GCS
    dataset = aiplatform.TabularDataset.create(
        display_name="training-data",
        gcs_source=f"gs://{bucket_name}/{prefix}/training.csv"
    )
    
    # Train model
    job = aiplatform.AutoMLTabularTrainingJob(
        display_name="train-model",
        optimization_prediction_type="classification"
    )
    
    model = job.run(
        dataset=dataset,
        target_column="label",
        budget_milli_node_hours=1000
    )
    
    return model
```

---

## Zonal Buckets for AI/ML

### What are Zonal Buckets?

Zonal buckets provide **ultra-low latency** and **high throughput** for AI/ML workloads:

| Feature | Standard Bucket | Zonal Bucket |
|---------|-----------------|--------------|
| **Latency** | 50-150ms | 5-10ms |
| **Throughput** | 2.5 Gbps/stream | 10+ Gbps/stream |
| **Use Case** | General purpose | AI/ML training, inference |
| **Location** | Region/Multi-region | Single zone |
| **Cost** | Standard | Higher ($0.108/GB/mo) |

### Create Zonal Bucket

```bash
gcloud storage buckets create gs://ml-training-data-zonal \
  --location=us-central1-a \
  --zone-info-collection=us-central1-a
```

### Use with Vertex AI

```python
from google.cloud import aiplatform

# Training job reading from zonal bucket
job = aiplatform.CustomTrainingJob(
    display_name="ml-training",
    script_path="train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-11:latest",
    requirements=["gcsfs"],
    model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-11:latest"
)

job.run(
    dataset=None,
    model_display_name="ml-model",
    args=[
        "--data_path=gs://ml-training-data-zonal/dataset/",
        "--epochs=100"
    ]
)
```

---

## Hierarchical Namespace

### What is Hierarchical Namespace?

Hierarchical namespace provides **true directory operations** (not just prefix simulation):

```
Standard (flat):
- Rename directory = Copy all objects + delete originals (slow)
- Delete directory = List + delete each object (slow)

Hierarchical (true directories):
- Rename directory = Single operation (fast)
- Delete directory = Single operation (fast)
```

### Enable Hierarchical Namespace

```bash
gcloud storage buckets create gs://my-hierarchical-bucket \
  --location=us-central1 \
  --enable-hierarchical-namespace
```

### Benefits

| Operation | Flat Namespace | Hierarchical Namespace |
|-----------|----------------|------------------------|
| **Rename directory** | Copy + delete all objects | Single metadata update |
| **Delete directory** | List + delete each object | Single operation |
| **List directory** | Scan all prefixes | Direct directory access |
| **Atomic directory operations** | No | Yes |

### Limitations

- 30% higher operation costs
- Not all tools support it yet
- Cannot convert existing buckets

---

## Object Tags

### What are Object Tags?

Tags allow **cost tracking** and **organization** at the object level:

```python
from google.cloud import storage

def upload_with_tags(bucket_name, source_file, destination_blob):
    """Upload object with tags."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    
    # Set tags
    blob.tags = {
        "department": "engineering",
        "project": "ml-pipeline",
        "sensitivity": "confidential"
    }
    
    blob.upload_from_filename(source_file)
    print(f"Uploaded with tags: {blob.tags}")
```

### Tag-Based Billing

```sql
-- Query costs by tag (requires billing export with tags)
SELECT
  system_labels.value as tag_value,
  SUM(cost) as total_cost
FROM `my-project.billing_export.gcp_billing_export_v1_*`
CROSS JOIN UNNEST(system_labels) as system_labels
WHERE system_labels.key = 'goog-gcs-object-tags'
GROUP BY 1
ORDER BY 2 DESC
```

### Tag Cost

- $0.005/month per tag
- Maximum 64 tags per object
- Tags count toward storage usage

---

## Multi-Region Turbo Replication

### What is Turbo Replication?

Turbo replication provides **15-minute RPO** for multi-region buckets:

```bash
# Enable turbo replication
gcloud storage buckets update gs://my-multi-region-bucket \
  --turbo-replication=ASYNC_TURBO

# Check replication status
gcloud storage buckets describe gs://my-multi-region-bucket \
  --format="value(rpo)"
```

### RPO Options

| RPO Type | Replication Time | Cost | Use Case |
|----------|------------------|------|----------|
| **DEFAULT** | Hours | Standard | Standard HA |
| **ASYNC_TURBO** | ~15 minutes | +20% | Critical data, low RPO |

### Terraform Turbo Replication

```hcl
resource "google_storage_bucket" "turbo_replicated" {
  name     = "my-critical-data"
  location = "US"  # Multi-region
  
  rpo = "ASYNC_TURBO"
}
```

---

## Transfer Service Advanced

### Cross-Cloud Transfer

```bash
# AWS S3 to GCS
gcloud storage transfer jobs create \
  s3://aws-bucket gs://gcs-bucket \
  --source-agent=aws \
  --aws-access-key-id=AKIAIOSFODNN7EXAMPLE \
  --aws-secret-access-key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Azure Blob to GCS
gcloud storage transfer jobs create \
  azure://azure-container gs://gcs-bucket \
  --azure-sas-token="?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupx&se=..."
```

### Scheduled Transfers

```bash
# Daily transfer at 2 AM
gcloud storage transfer jobs create \
  gs://source-bucket gs://dest-bucket \
  --schedule-daily=02:00 \
  --overwrite-when=DIFFERENT
```

### Transfer Options

```bash
# With options
gcloud storage transfer jobs create \
  gs://source gs://dest \
  --delete-from-source-after-transfer \
  --overwrite-when=DIFFERENT \
  --manifest-file=manifest.csv
```

---

## Security Edge Cases

### Signed URL Vulnerabilities

```
Problem: Signed URLs with long expiration
Impact: Object accessible for extended period
Fix: Use short expiration (minutes, not hours)

Problem: Signed URLs without content-type validation
Impact: Object can be replaced with malicious content
Fix: Require content-type in signed URL
```

### IAM Escalation Patterns

```
Problem: Service Account User role + SA with Storage Admin
Impact: User can impersonate SA and get Storage Admin
Fix: Don't grant SA User role to non-admins

Problem: Project Editor includes Storage Admin
Impact: Editor can access all buckets in project
Fix: Use custom roles instead of Editor
```

### Data Exfiltration Prevention

```bash
# Prevent data transfer to personal accounts
gcloud org-policies set-policy allowPolicyOnlyForMembers \
  --organization=ORG_ID \
  --allowed-members=group:company.com
```

---

## Compliance Implementations

### HIPAA Compliance

```hcl
# HIPAA-compliant bucket
resource "google_storage_bucket" "hipaa" {
  name     = "phi-data-bucket"
  location = "US-CENTRAL1"
  
  # Security
  uniform_bucket_level_access    = true
  public_access_prevention       = "enforced"
  
  # Encryption
  encryption {
    default_kms_key_name = google_kms_crypto_key.hipaa_key.id
  }
  
  # Versioning
  versioning {
    enabled = true
  }
  
  # Audit logging (enable Data Access logs)
  # Retention
  retention_policy {
    retention_period = 220752000  # 7 years
    is_locked        = true
  }
  
  # Labels
  labels = {
    compliance      = "hipaa"
    data-classification = "phi"
  }
}
```

### SOC2 Compliance

```
Requirements:
✅ Access controls (IAM, uniform bucket-level access)
✅ Audit logging (Admin Activity + Data Access logs)
✅ Encryption (CMEK)
✅ Change management (Terraform, version control)
✅ Monitoring (Cloud Monitoring alerts)
✅ Backup & recovery (versioning, soft delete)
```

### GDPR Compliance

```
Requirements:
✅ Data residency (EU multi-region)
✅ Right to erasure (delete objects, versions, soft-deleted)
✅ Data portability (export objects)
✅ Access controls (IAM, audit logging)
✅ Encryption (CMEK with key rotation)

Implementation:
- Store EU data in EU regions only
- Implement automated deletion on request
- Maintain audit trail of all access
- Document data processing activities
```

---

## API Endpoints Reference

For detailed information on Global, Regional, and ITAR endpoints, see [PERFORMANCE_OPTIMIZATION.md](./PERFORMANCE_OPTIMIZATION.md#api-endpoints-regionalglobalitar)

Quick reference:
- **Global**: `storage.googleapis.com` (default)
- **Regional**: `REGION.storage.googleapis.com` (lower latency)
- **ITAR**: `itar.storage.googleapis.com` (government compliance)

---

*"Advanced features solve advanced problems. Use them when you need them, but don't over-engineer simple use cases."* — Senior Architect Wisdom
