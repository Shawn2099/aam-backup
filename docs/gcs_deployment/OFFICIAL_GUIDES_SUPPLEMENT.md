# GCS Official Guides Supplement

**Source**: Official Google Cloud Storage Documentation  
**Last Updated**: 2026-04-11  
**Purpose**: Additional topics from official Google guides not covered in main documents

---

## Table of Contents

1. [Managed Folders](#managed-folders)
2. [Requester Pays](#requester-pays)
3. [Static Website Hosting](#static-website-hosting)
4. [Object Operations Deep Dive](#object-operations-deep-dive)
5. [Cloud Storage FUSE](#cloud-storage-fuse)
6. [Storage Transfer Service](#storage-transfer-service)
7. [Storage Insights](#storage-insights)
8. [Batch Operations](#batch-operations)
9. [API Reference Summary](#api-reference-summary)
10. [Quotas & Limits](#quotas--limits)
11. [HMAC Keys & S3 Interoperability](#hmac-keys--s3-interoperability)
12. [Official Code Samples](#official-code-samples)

---

## Managed Folders

### What Are Managed Folders?

Managed folders are **real Cloud Storage resources** (not just prefix simulations) that support:
- Direct IAM policy attachment
- Resource-level access control
- Audit logging visibility
- Fine-grained security boundaries

### Managed Folders vs Simulated Folders

| Feature | Simulated Folders (Prefixes) | Managed Folders |
|---------|------------------------------|-----------------|
| **IAM Support** | No (bucket-level only) | ✅ Yes (folder-level) |
| **Audit Logging** | Object-level only | ✅ Folder-level |
| **Entity Type** | Naming convention | Real resource |
| **Deletion** | Delete all objects | Cannot delete if non-empty |
| **Creation** | Automatic on upload | Explicit creation required |
| **Uniform Access Required** | No | ✅ Yes |

### Managed Folder Naming Rules

```
✅ Valid:
- uploads/
- data/team-a/
- projects/2026/Q1/reports/
- team/engineering/ml-models/

❌ Invalid:
- uploads (must end with /)
- .well-known/acme-challenge/ (reserved)
- . or .. (reserved)
- Names > 1024 bytes
- Nested > 15 levels deep
```

### Create Managed Folders

```bash
# Create managed folder
gcloud storage managed-folders create gs://my-bucket/team-a/

# Create nested managed folder
gcloud storage managed-folders create gs://my-bucket/data/team-a/reports/

# List managed folders
gcloud storage managed-folders list gs://my-bucket

# Describe managed folder
gcloud storage managed-folders describe gs://my-bucket/team-a/
```

### IAM on Managed Folders

```bash
# Grant IAM role on managed folder
gcloud storage managed-folders add-iam-policy-binding \
  gs://my-bucket/team-a/ \
  --member="group:team-a@example.com" \
  --role="roles/storage.objectAdmin"

# Get IAM policy
gcloud storage managed-folders get-iam-policy gs://my-bucket/team-a/

# Remove IAM binding
gcloud storage managed-folders remove-iam-policy-binding \
  gs://my-bucket/team-a/ \
  --member="group:team-a@example.com" \
  --role="roles/storage.objectAdmin"
```

### Terraform: Managed Folders

```hcl
resource "google_storage_managed_folder" "team_a" {
  bucket = google_storage_bucket.main.name
  name   = "team-a/"
}

resource "google_storage_managed_folder_iam_member" "team_a_access" {
  bucket = google_storage_bucket.main.name
  name   = google_storage_managed_folder.team_a.name
  role   = "roles/storage.objectAdmin"
  member = "group:team-a@example.com"
}

# Nested managed folders
resource "google_storage_managed_folder" "reports" {
  bucket = google_storage_bucket.main.name
  name   = "data/team-a/reports/"
}
```

### Managed Folder Use Cases

```
Multi-tenant Data Platform:
┌─────────────────────────────────────┐
│  Bucket: shared-data-platform       │
│  ├── customers/                     │
│  │   ├── customer-a/  ← IAM: Team A │
│  │   ├── customer-b/  ← IAM: Team B │
│  │   └── customer-c/  ← IAM: Team C │
│  ├── shared/          ← IAM: All    │
│  └── analytics/       ← IAM: BI     │
└─────────────────────────────────────┘

Compliance Scenarios:
- PII data: managed folder with restricted IAM
- Public data: managed folder with broader access
- Audit logs: managed folder with write-once policy
```

### Delete Managed Folders

```bash
# Delete empty managed folder
gcloud storage managed-folders delete gs://my-bucket/team-a/

# Delete non-empty managed folder (JSON API with allowNonEmpty)
# WARNING: This deletes the folder AND all contained objects
curl -X DELETE \
  "https://storage.googleapis.com/storage/v1/b/my-bucket/managedFolders/team-a/?allowNonEmpty=true"
```

---

## Requester Pays

### What is Requester Pays?

Requester Pays shifts **egress and operation costs** from bucket owner to the requester:

```
Normal Bucket:
- Bucket owner pays: Storage + Operations + Egress

Requester Pays Bucket:
- Bucket owner pays: Storage + Early Deletion
- Requester pays: Operations + Egress + Retrieval
```

### When to Use Requester Pays

| Scenario | Use Requester Pays? | Why |
|----------|---------------------|-----|
| Public dataset sharing | ✅ Yes | Consumers pay for their usage |
| Cross-project collaboration | ✅ Yes | Each project pays for their access |
| Partner data sharing | ✅ Yes | Partners responsible for their costs |
| Internal application | ❌ No | You control all access |
| CDN origin | ❌ No | You pay for CDN cache fills |
| Backup storage | ❌ No | You control all operations |

### Enable Requester Pays

```bash
# Enable on bucket
gsutil requesterpays set on gs://my-public-dataset

# Disable
gsutil requesterpays set off gs://my-public-dataset

# Check status
gsutil requesterpays get gs://my-public-dataset
```

### Terraform: Requester Pays

```hcl
resource "google_storage_bucket" "requester_pays" {
  name     = "my-public-dataset"
  location = "US-CENTRAL1"
  
  requester_pays = true
  
  uniform_bucket_level_access    = true
  public_access_prevention       = "inherited"  # Must allow public access
}

# Grant public read access
resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.requester_pays.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
```

### Access Requester Pays Buckets

```bash
# Access with billing project
gsutil -u my-billing-project ls gs://requester-pays-bucket/

# Download with billing project
gsutil -u my-billing-project cp gs://requester-pays-bucket/data.csv .

# Python: Access with billing project
from google.cloud import storage

client = storage.Client(project="my-billing-project")
bucket = client.bucket("requester-pays-bucket")
blob = bucket.blob("data.csv")
blob.download_to_filename("data.csv")
```

### Requester Pays Billing Breakdown

| Cost Component | Bucket Owner Pays | Requester Pays |
|----------------|-------------------|----------------|
| **Storage** | ✅ Yes | ❌ No |
| **Early Deletion** | ✅ Yes | ❌ No |
| **Operations** | ❌ No | ✅ Yes |
| **Egress** | ❌ No | ✅ Yes |
| **Retrieval Fees** | ❌ No | ✅ Yes |
| **Replication** | ❌ No | ✅ Yes |

### Requester Pays Restrictions

```
❌ Cannot use with:
- Cloud SQL imports/exports
- Pub/Sub exports
- Buckets with public access prevention enforced

⚠️ Requirements:
- Requester must have billing project
- Requester must have serviceusage.services.use permission
- Requester must have standard IAM permissions on bucket
```

### Cost Isolation Strategy

```
To track Requester Pays costs separately:

1. Create dedicated billing project: "gcs-requester-pays-tracking"
2. All requesters use this project for access
3. Monitor costs in Cloud Billing console
4. Set budget alerts on tracking project

This isolates Requester Pays charges from your regular GCS usage.
```

---

## Static Website Hosting

### Overview

GCS can host static websites with:
- Custom index page (index.html)
- Custom error page (404.html)
- Public access (required)
- Optional CDN + custom domain + SSL

### Basic Setup (GCS Only)

```bash
# 1. Create bucket
gsutil mb gs://my-website.com

# 2. Disable public access prevention (REQUIRED for static sites)
gcloud storage buckets update gs://my-website.com \
  --public-access-prevention=inherited

# 3. Make bucket publicly readable
gsutil iam ch allUsers:objectViewer gs://my-website.com

# 4. Set website configuration
gsutil web set -m index.html -e 404.html gs://my-website.com

# 5. Upload files
gsutil -m cp -r ./website-content gs://my-website.com/
```

### Terraform: Static Website

```hcl
resource "google_storage_bucket" "website" {
  name     = "my-website-com"
  location = "US-CENTRAL1"
  
  # CRITICAL: Cannot enforce public access prevention for static sites
  public_access_prevention = "inherited"
  
  # Website configuration
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
  
  # Enable versioning for easy rollbacks
  versioning {
    enabled = true
  }
}

# Make bucket publicly accessible
resource "google_storage_bucket_iam_member" "public" {
  bucket = google_storage_bucket.website.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
```

### Production Setup (Load Balancer + CDN + SSL)

```
Architecture:
User → Custom Domain (HTTPS) → Load Balancer → Cloud CDN → GCS Bucket
                                    ↓
                            Google-managed SSL Certificate
```

#### Step 1: Reserve Static IP

```bash
gcloud compute addresses create website-ip --global
```

#### Step 2: Create Backend Bucket with CDN

```bash
gcloud compute backend-buckets create website-backend \
  --gcs-bucket-name=my-website-com \
  --enable-cdn \
  --cdn-policy-cache-mode=CACHE_ALL_STATIC \
  --cdn-policy-ttl=3600
```

#### Step 3: Create URL Map

```bash
gcloud compute url-maps create website-map \
  --default-backend-bucket=website-backend
```

#### Step 4: Create SSL Certificate

```bash
gcloud compute ssl-certificates create website-cert \
  --domains=my-website.com,www.my-website.com \
  --global
```

#### Step 5: Create HTTPS Target Proxy

```bash
gcloud compute target-https-proxies create website-proxy \
  --url-map=website-map \
  --ssl-certificates=website-cert
```

#### Step 6: Create Forwarding Rule

```bash
gcloud compute forwarding-rules create website-rule \
  --global \
  --target-https-proxy=website-proxy \
  --address=website-ip \
  --ports=443
```

#### Step 7: Update DNS

```
Add A records at your DNS registrar:
Type: A
Name: @
Value: [STATIC_IP_FROM_STEP_1]
TTL: 300

Type: A
Name: www
Value: [STATIC_IP_FROM_STEP_1]
TTL: 300
```

### Static Website Best Practices

1. **Version your assets**: `style-v2.css` instead of overwriting
2. **Set Cache-Control**: Static assets = long, HTML = short
3. **Enable CDN**: For global performance
4. **Use SSL**: Google-managed certificates are free
5. **Enable versioning**: Easy rollbacks
6. **Monitor costs**: CDN cache fills have charges

---

## Object Operations Deep Dive

### Object Immutability

**GCS objects are STRICTLY IMMUTABLE**:

```
❌ Cannot:
- Append to objects
- Truncate objects
- Modify partial content
- Update metadata without replacement

✅ Can:
- Replace entire object (atomic operation)
- Upload new version (with versioning)
- Update custom metadata (creates new generation)
```

### Atomic Replacement

```python
from google.cloud import storage

# Replacement is atomic
client = storage.Client()
bucket = client.bucket("my-bucket")
blob = bucket.blob("config.json")

# Old version serves until new upload completes
blob.upload_from_string('{"version": "2.0"}')
# Switch is instantaneous
```

### Object Replacement Rate Limit

```
Max: 1 replacement per second for same object

If exceeded:
- HTTP 429: Too Many Requests
- Implement exponential backoff
- Use different object names for high-frequency updates

Best Practice:
- For frequently updated data, use different naming pattern
- config/v1/config.json, config/v2/config.json, etc.
```

### Parallel Composite Uploads

```bash
# Enable parallel composite uploads (faster for large files)
gsutil -o GSUtil:parallel_composite_upload_threshold=150M \
  cp large-file.bin gs://my-bucket/

# Threshold: Files > 150MB are split into chunks
# Chunks upload in parallel, then compose
```

```python
# Python: Parallel composite upload
from google.cloud import storage

transfer_manager = storage.transfer_manager

# Upload large file in parallel
transfer_manager.upload_chunks_from_filename(
    "my-bucket",
    "large-file.bin",
    workers=8,
    chunk_size=100 * 1024 * 1024,  # 100 MB chunks
    skip_if_exists=True
)
```

### Sliced Downloads

```python
# Download object in parallel slices (faster for large objects)
from google.cloud import storage

transfer_manager = storage.transfer_manager

# Download with sliced downloads
transfer_manager.download_chunks_to_filename(
    "my-bucket",
    "large-file.bin",
    "local-file.bin",
    workers=8
)
```

### Batch Operations

```python
# Batch multiple operations (reduces API calls)
from google.cloud import storage
from google.cloud.storage.batch import Batch

client = storage.Client()
bucket = client.bucket("my-bucket")

with Batch(client) as batch:
    # Delete multiple objects in single request
    for blob_name in ["file1.txt", "file2.txt", "file3.txt"]:
        batch.delete(bucket.blob(blob_name))

# Batch supports up to 1000 operations
```

### Object Metadata

```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket("my-bucket")
blob = bucket.blob("data.json")

# System metadata (read-only)
print(f"Created: {blob.time_created}")
print(f"Updated: {blob.updated}")
print(f"Generation: {blob.generation}")
print(f"Metageneration: {blob.metageneration}")
print(f"Size: {blob.size} bytes")
print(f"Content Type: {blob.content_type}")
print(f"Storage Class: {blob.storage_class}")

# Custom metadata (application-specific)
blob.metadata = {
    "source": "mobile-app",
    "version": "2.0",
    "environment": "production"
}
blob.patch()

# Custom metadata in custom headers
# x-goog-meta-source: mobile-app
# x-goog-meta-version: 2.0
```

### Object Naming: What to Avoid

```
❌ Avoid:
- Carriage Return (\r) or Line Feed (\n)
- XML 1.0 illegal characters (#x7F-#x84, #x86-#x9F)
- # character (parsed as version ID separator)
- [*?] characters (wildcard conflicts)
- :"<>| characters (Windows incompatibility)
- ./ and ../ (relative path risks)
- Sensitive/PII data in names

✅ Use:
- Lowercase letters, numbers, hyphens, underscores
- Forward slashes for hierarchy simulation
- Dates in ISO format: 2026/04/11
- UUIDs for uniqueness: user-123-abc-def
```

---

## Cloud Storage FUSE

### What is Cloud Storage FUSE?

Cloud Storage FUSE allows mounting GCS buckets as **POSIX-like file systems**:

```
Mount Point: /mnt/gcs-bucket
Access: Standard file operations (ls, cp, cat, etc.)
Use Cases: AI/ML training, analytics, legacy applications
```

### Installation

```bash
# Ubuntu/Debian
curl -O https://github.com/GoogleCloudPlatform/gcsfuse/releases/latest/download/gcsfuse_1.4.0_amd64.deb
sudo dpkg -i gcsfuse_*.deb

# CentOS/RHEL
sudo yum install -y gcsfuse

# Verify installation
gcsfuse --version
```

### Mount Bucket

```bash
# Create mount point
mkdir -p /mnt/gcs-bucket

# Mount bucket
gcsfuse my-bucket /mnt/gcs-bucket

# Mount with options
gcsfuse \
  --implicit-dirs \
  --max-conns-per-host 100 \
  --stat-cache-ttl 60s \
  --type-cache-ttl 60s \
  --file-cache-max-size-mb 1024 \
  my-bucket /mnt/gcs-bucket
```

### Mount Options

| Option | Description | Recommended Value |
|--------|-------------|-------------------|
| `--implicit-dirs` | Support directory operations | Enable if needed |
| `--max-conns-per-host` | Max HTTP connections | 100-200 |
| `--stat-cache-ttl` | Metadata cache TTL | 60s-300s |
| `--type-cache-ttl` | Type cache TTL | 60s-300s |
| `--file-cache-max-size-mb` | File cache size | 1024-4096 MB |
| `--rename-dir-limit` | Max size for directory rename | 1000-5000 |

### AI/ML Integration

```bash
# Mount for ML training
gcsfuse \
  --file-cache-max-size-mb 8192 \
  --stat-cache-ttl 300s \
  --type-cache-ttl 300s \
  ml-training-data /mnt/training-data

# Use in training script
# Data automatically cached locally for fast access
```

### GKE Integration

```yaml
# gke-fuse-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: gcsfuse-pod
spec:
  containers:
  - name: app
    image: my-app:latest
    volumeMounts:
    - name: gcs-bucket
      mountPath: /data
      readOnly: true
    securityContext:
      privileged: true
  volumes:
  - name: gcs-bucket
    csi:
      driver: gcsfuse.csi.storage.gke.io
      volumeAttributes:
        bucketName: my-gcs-bucket
        mountOptions: "implicit-dirs,max-conns-per-host=100"
```

### FUSE Performance Tuning

```
Read-Heavy Workloads:
- Increase file-cache-max-size-mb: 4096-8192 MB
- Increase stat-cache-ttl: 300-600s
- Increase type-cache-ttl: 300-600s

Write-Heavy Workloads:
- Decrease cache TTLs: 10-60s
- Monitor for consistency issues
- Consider direct API access instead

AI/ML Training:
- Max file cache: 8192+ MB
- Long cache TTLs: 300s+
- Use zonal buckets for lowest latency
```

### FUSE Limitations

```
❌ Not Supported:
- File permissions (always 755/644)
- Hard links
- Extended attributes
- File locking (flock)
- Atomic renames (without hierarchical namespace)
- High-concurrency writes

⚠️ Performance Considerations:
- List operations can be slow without implicit-dirs
- Metadata caching can cause consistency issues
- Not suitable for databases or high-IOPS workloads
- Best for read-heavy, sequential access patterns
```

---

## Storage Transfer Service

### Transfer Types

| Type | Source | Destination | Use Case |
|------|--------|-------------|----------|
| **S3 to GCS** | Amazon S3 | GCS Bucket | AWS migration |
| **Azure to GCS** | Azure Blob | GCS Bucket | Azure migration |
| **GCS to GCS** | GCS Bucket | GCS Bucket | Cross-region copy |
| **HTTP/HTTPS to GCS** | URL list | GCS Bucket | Public data import |
| **POSIX to GCS** | Local file system | GCS Bucket | On-prem migration |

### S3 to GCS Migration

```bash
# Simple migration
gcloud storage transfer jobs create \
  s3://aws-bucket gs://gcs-bucket \
  --source-agent=aws \
  --aws-access-key-id=AKIAIOSFODNN7EXAMPLE \
  --aws-secret-access-key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Full migration (preserves metadata/ACLs)
gcloud storage transfer jobs create \
  s3://aws-bucket gs://gcs-bucket \
  --source-agent=aws \
  --aws-access-key-id=AKIAIOSFODNN7EXAMPLE \
  --aws-secret-access-key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  --preserve-metadata=acl \
  --overwrite-when=DIFFERENT
```

### Scheduled Transfers

```bash
# Daily transfer at 2 AM
gcloud storage transfer jobs create \
  gs://source-bucket gs://dest-bucket \
  --schedule-daily=02:00 \
  --overwrite-when=DIFFERENT

# Weekly transfer (Mondays at 3 AM)
gcloud storage transfer jobs create \
  gs://source-bucket gs://dest-bucket \
  --schedule-weekly=MON,03:00
```

### Transfer Options

```bash
# With all options
gcloud storage transfer jobs create \
  gs://source gs://dest \
  --delete-from-source-after-transfer \
  --overwrite-when=DIFFERENT \
  --manifest-file=manifest.csv \
  --bandwidth-limit=100M
```

---

## Storage Insights

### What is Storage Insights?

Storage Insights provides **visibility into GCS usage** with:
- Inventory reports (object-level metadata)
- Usage reports (access patterns)
- Storage Intelligence (AI-powered recommendations)

### Configure Storage Insights

```bash
# Create dataset configuration
gcloud storage insights dataset-configs create \
  my-insights-config \
  --location=US \
  --description="GCS insights for my project"

# Enable inventory reports
gcloud storage insights dataset-configs update \
  my-insights-config \
  --enable-inventory-reports

# Enable usage logs
gcloud storage insights dataset-configs update \
  my-insights-config \
  --enable-usage-logs
```

### Storage Intelligence

Storage Intelligence provides:
- **Bucket relocation recommendations**: Move buckets closer to compute
- **Cost optimization suggestions**: Right-size storage classes
- **Usage pattern analysis**: Identify inefficient access patterns
- **Orphaned object detection**: Find unused data

---

## API Reference Summary

### JSON API

```
Base URL: https://storage.googleapis.com/storage/v1
Authentication: OAuth 2.0, Service Accounts
Format: JSON
Operations: All GCS operations
Rate Limit: 5,000+ QPS per prefix
```

### XML API

```
Base URL: https://storage.googleapis.com
Authentication: HMAC keys, Signed URLs
Format: XML
Operations: Core operations, multipart uploads
Use Case: S3 compatibility, legacy systems
```

### Client Libraries

| Language | Package | gRPC Support |
|----------|---------|--------------|
| **Python** | `google-cloud-storage` | ✅ Yes |
| **Node.js** | `@google-cloud/storage` | ✅ Yes |
| **Java** | `google-cloud-storage` | ✅ Yes |
| **Go** | `cloud.google.com/go/storage` | ✅ Yes |
| **C++** | `google-cloud-cpp` | ✅ Yes |
| **.NET** | `Google.Cloud.Storage.V1` | ❌ No |
| **PHP** | `google/cloud-storage` | ❌ No |
| **Ruby** | `google-cloud-storage` | ❌ No |

---

## Quotas & Limits

### Bucket Limits

| Limit | Value |
|-------|-------|
| Max buckets per project | No enforced limit |
| Bucket name length | 3-63 characters |
| Max object size | 5 TB (single upload) |
| Max object size (composite) | 5 TB |

### Object Limits

| Limit | Value |
|-------|-------|
| Max object name length (flat) | 1,024 bytes (UTF-8) |
| Max folder name length (hierarchical) | 512 bytes |
| Max object name length (hierarchical) | 512 bytes (base) |
| Max custom metadata entries | No limit (counts toward storage) |
| Max object replacement rate | 1/second per object |

### Request Rate Guidelines

| Pattern | Max QPS |
|---------|---------|
| Single prefix | ~5,000 |
| 10 diverse prefixes | ~50,000 |
| 100+ diverse prefixes | Millions |

### API Quotas

| Operation | Rate Limit |
|-----------|------------|
| Bucket operations | No specific limit |
| Object operations | No specific limit |
| IAM operations | No specific limit |
| List operations | Paginate for large results |

---

## HMAC Keys & S3 Interoperability

### What are HMAC Keys?

HMAC keys enable **S3-compatible access** to GCS:

```
S3 Tool → HMAC Key + Secret → GCS XML API → Objects
```

### Create HMAC Keys

```bash
# Create HMAC key for service account
gcloud alpha storage hmac create \
  --service-account=my-app@project.iam.gserviceaccount.com

# List HMAC keys
gcloud alpha storage hmac list

# Activate HMAC key
gcloud alpha storage hmac activate ACCESS_KEY_ID

# Deactivate HMAC key
gcloud alpha storage hmac deactivate ACCESS_KEY_ID

# Delete HMAC key
gcloud alpha storage hmac delete ACCESS_KEY_ID
```

### S3 Migration with HMAC Keys

```bash
# Configure s3cmd for GCS
s3cmd --configure
Access Key: [HMAC_ACCESS_KEY_ID]
Secret Key: [HMAC_SECRET]
S3 Endpoint: storage.googleapis.com
DNS-style: %(bucket)s.storage.googleapis.com

# Use AWS CLI with GCS
aws configure set aws_access_key_id [HMAC_ACCESS_KEY_ID]
aws configure set aws_secret_access_key [HMAC_SECRET]
aws configure set default.s3.endpoint_url https://storage.googleapis.com

# Now use standard S3 commands
aws s3 ls s3://my-bucket
aws s3 cp file.txt s3://my-bucket/
```

### HMAC Key Security

```
✅ Best Practices:
- Rotate keys every 90 days
- Use service accounts, not user accounts
- Grant minimum required permissions
- Monitor usage via audit logs
- Deactivate unused keys

❌ Avoid:
- Storing keys in code repositories
- Sharing keys across applications
- Using HMAC for non-S3-compatible tools
- Long-lived keys without rotation
```

---

## Official Code Samples

### Python Quickstart

```python
from google.cloud import storage

def quickstart():
    # Initialize client
    client = storage.Client()
    
    # Create bucket
    bucket = client.create_bucket("my-unique-bucket", location="US-CENTRAL1")
    print(f"Created bucket: {bucket.name}")
    
    # Upload object
    blob = bucket.blob("hello.txt")
    blob.upload_from_string("Hello, GCS!")
    print(f"Uploaded: {blob.name}")
    
    # Download object
    content = blob.download_as_text()
    print(f"Downloaded: {content}")
    
    # List objects
    blobs = bucket.list_blobs()
    for blob in blobs:
        print(f"  - {blob.name}")

quickstart()
```

### Node.js Quickstart

```javascript
const {Storage} = require('@google-cloud/storage');

async function quickstart() {
  const storage = new Storage();
  
  // Create bucket
  const [bucket] = await storage.createBucket('my-unique-bucket');
  console.log(`Created bucket: ${bucket.name}`);
  
  // Upload object
  await bucket.file('hello.txt').save('Hello, GCS!');
  console.log('Uploaded: hello.txt');
  
  // Download object
  const [content] = await bucket.file('hello.txt').download();
  console.log(`Downloaded: ${content.toString()}`);
  
  // List objects
  const [files] = await bucket.getFiles();
  files.forEach(file => console.log(`  - ${file.name}`));
}

quickstart();
```

### Go Quickstart

```go
import (
    "context"
    "fmt"
    "io"
    "cloud.google.com/go/storage"
)

func quickstart(w io.Writer, projectID, bucketName string) error {
    ctx := context.Background()
    client, err := storage.NewClient(ctx)
    if err != nil {
        return fmt.Errorf("storage.NewClient: %v", err)
    }
    defer client.Close()
    
    // Create bucket
    bucket := client.Bucket(bucketName)
    if err := bucket.Create(ctx, projectID, nil); err != nil {
        return fmt.Errorf("Bucket.Create: %v", err)
    }
    fmt.Fprintf(w, "Created bucket: %s\n", bucketName)
    
    return nil
}
```

---

## Official Documentation References

### Essential Guides
- [Quickstarts](https://cloud.google.com/storage/docs/quickstart)
- [Create Buckets](https://cloud.google.com/storage/docs/creating-buckets)
- [Storage Classes](https://cloud.google.com/storage/docs/storage-classes)
- [Bucket Locations](https://cloud.google.com/storage/docs/locations)
- [Upload Objects](https://cloud.google.com/storage/docs/uploading-objects)
- [Download Objects](https://cloud.google.com/storage/docs/downloading-objects)
- [Object Lifecycle](https://cloud.google.com/storage/docs/lifecycle)
- [Object Versioning](https://cloud.google.com/storage/docs/object-versioning)
- [Bucket Lock](https://cloud.google.com/storage/docs/bucket-lock)
- [Managed Folders](https://cloud.google.com/storage/docs/managed-folders)
- [Requester Pays](https://cloud.google.com/storage/docs/requester-pays)
- [Static Website Hosting](https://cloud.google.com/storage/docs/hosting-static-website)
- [Storage Transfer Service](https://cloud.google.com/storage-transfer/docs)
- [Cloud Storage FUSE](https://cloud.google.com/storage/docs/gcs-fuse)
- [Storage Insights](https://cloud.google.com/storage/docs/insights)
- [Quotas & Limits](https://cloud.google.com/storage/quotas)
- [Pricing](https://cloud.google.com/storage/pricing)
- [Release Notes](https://cloud.google.com/storage/docs/release-notes)

### API References
- [JSON API Reference](https://cloud.google.com/storage/docs/json-api/v1)
- [XML API Reference](https://cloud.google.com/storage/docs/xml-api)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference/storage)
- [gsutil Reference](https://cloud.google.com/storage/docs/gsutil)
- [IAM Reference](https://cloud.google.com/storage/docs/access-control/iam-roles)

### Client Libraries
- [Python](https://cloud.google.com/python/docs/reference/storage/latest)
- [Node.js](https://cloud.google.com/nodejs/docs/reference/storage/latest)
- [Java](https://cloud.google.com/java/docs/reference/google-cloud-storage/latest)
- [Go](https://cloud.google.com/go/docs/reference/cloud.google.com/go/storage/latest)
- [C++](https://cloud.google.com/cpp/docs/reference/storage/latest)
- [.NET](https://cloud.google.com/dotnet/docs/reference/Google.Cloud.Storage.V1/latest)
- [PHP](https://cloud.google.com/php/docs/reference/google-cloud-storage/latest)
- [Ruby](https://cloud.google.com/ruby/docs/reference/google-cloud-storage/latest)

### Training & Tutorials
- [Interactive Tutorial (Console)](https://console.cloud.google.com/welcome?cloudshell=true)
- [AWS Professionals](https://cloud.google.com/storage/docs/aws-professionals)
- [Azure Professionals](https://cloud.google.com/storage/docs/azure-professionals)
- [Code Samples](https://cloud.google.com/storage/docs/samples)

---

*"Official documentation is your source of truth. Always verify configurations against the latest Google guides."* — Cloud Engineer Best Practice
