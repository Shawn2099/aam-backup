# IAM & Security - Google Cloud Storage

**Level**: Intermediate to Expert  
**Prerequisites**: [Bucket Configuration](./BUCKET_CONFIGURATION.md)  
**Time to Master**: 2-3 weeks of hands-on practice

---

## Table of Contents

1. [IAM Fundamentals](#iam-fundamentals)
2. [Predefined Roles](#predefined-roles)
3. [Custom Roles](#custom-roles)
4. [IAM Policy Structure](#iam-policy-structure)
5. [Service Account Best Practices](#service-account-best-practices)
6. [Signed URLs & Signed Policies](#signed-urls--signed-policies)
7. [VPC Service Controls](#vpc-service-controls)
8. [Encryption Strategies](#encryption-strategies)
9. [Public Access Prevention](#public-access-prevention)
10. [Condition-Based Access](#condition-based-access)
11. [Audit & Compliance](#audit--compliance)
12. [Security Automation](#security-automation)
13. [Common Security Mistakes](#common-security-mistakes)

---

## IAM Fundamentals

### How GCS IAM Works

GCS IAM operates at two levels:
1. **Bucket-level IAM**: Controls access to the bucket and all objects within it
2. **Object-level ACLs**: Fine-grained control (deprecated in favor of uniform bucket-level access)

**CRITICAL**: Always use **uniform bucket-level access** instead of fine-grained ACLs. ACLs are legacy, harder to audit, and don't integrate with Cloud IAM.

```bash
# Check if uniform bucket-level access is enabled
gsutil iam get gs://my-bucket

# If you see "bindings" with "allUsers" or ACLs, you're not using uniform access
# Enable it (WARNING: This is irreversible without recreating the bucket)
gcloud storage buckets update gs://my-bucket --uniform-bucket-level-access
```

### IAM Hierarchy & Inheritance

```
Organization
  └── Folder
        └── Project
              └── Bucket (IAM applies here)
                    └── Objects (Inherit bucket IAM)
```

**Key Principle**: IAM policies are **additive** across the hierarchy. A user with `roles/storage.objectViewer` at the project level can read ALL buckets in that project.

---

## Predefined Roles

### Bucket-Level Roles

| Role | Name | Permissions | When to Use |
|------|------|-------------|-------------|
| `roles/storage.admin` | Storage Admin | Full control over buckets AND objects | Platform engineers, DevOps |
| `roles/storage.legacyBucketOwner` | Legacy Bucket Owner | Full bucket config + object access | Legacy systems (avoid for new projects) |
| `roles/storage.legacyBucketReader` | Legacy Bucket Reader | List buckets, read metadata | Monitoring, auditing |

### Object-Level Roles

| Role | Name | Permissions | When to Use |
|------|------|-------------|-------------|
| `roles/storage.objectAdmin` | Storage Object Admin | Full object management (create, read, delete, metadata) | Application write access |
| `roles/storage.objectCreator` | Storage Object Creator | Create objects only | Log ingestion, data pipelines |
| `roles/storage.objectViewer` | Storage Object Viewer | Read objects only | Analytics, read-only applications |

### Critical Permission Details

```yaml
# roles/storage.objectViewer includes:
- storage.objects.get
- storage.objects.list
- storage.buckets.get
- storage.buckets.list

# roles/storage.objectCreator includes:
- storage.objects.create
- storage.objects.delete (multipart uploads)
- storage.buckets.get

# roles/storage.objectAdmin includes:
- All objectViewer permissions
- storage.objects.create
- storage.objects.delete
- storage.objects.update
- storage.objects.setIamPolicy
- storage.objects.getIamPolicy

# roles/storage.admin includes:
- All objectAdmin permissions
- storage.buckets.create
- storage.buckets.delete
- storage.buckets.update
- storage.buckets.getIamPolicy
- storage.buckets.setIamPolicy
- storage.buckets.setRetention
```

### Granting Roles (Examples)

#### Via gcloud

```bash
# Grant role to a user
gsutil iam ch user:jane@example.com:objectViewer gs://my-bucket

# Grant role to a service account
gsutil iam ch serviceAccount:my-app@my-project.iam.gserviceaccount.com:objectAdmin gs://my-bucket

# Grant role to a group (RECOMMENDED for teams)
gsutil iam ch group:engineering@example.com:objectViewer gs://my-bucket

# Grant role to all authenticated users (use with extreme caution)
gsutil iam ch allAuthenticatedUsers:objectViewer gs://my-bucket

# Remove a role
gsutil iam ch -d user:jane@example.com:objectViewer gs://my-bucket

# View current policy
gsutil iam get gs://my-bucket > policy.json
cat policy.json
```

#### Via Terraform

```hcl
resource "google_storage_bucket_iam_member" "viewer" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectViewer"
  member = "user:jane@example.com"
}

resource "google_storage_bucket_iam_member" "service_account" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:my-app@my-project.iam.gserviceaccount.com"
}

# Use groups for team access (RECOMMENDED)
resource "google_storage_bucket_iam_member" "team" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectViewer"
  member = "group:team@example.com"
}
```

#### Via Python

```python
from google.cloud import storage

def grant_bucket_role(bucket_name, role, member):
    """Grant an IAM role on a bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # Get current policy (version 3 supports conditions)
    policy = bucket.get_iam_policy(requested_policy_version=3)
    
    # Add binding
    policy.bindings.append({
        "role": role,
        "members": {member}
    })
    
    # Update policy
    bucket.set_iam_policy(policy)
    print(f"Granted {role} to {member} on {bucket_name}")

# Usage
grant_bucket_role(
    "my-bucket",
    "roles/storage.objectViewer",
    "user:jane@example.com"
)
```

---

## Custom Roles

### When to Use Custom Roles

Predefined roles are often too broad. Create custom roles when:
- You need specific permission combinations not covered by predefined roles
- You want to enforce least-privilege strictly
- You have compliance requirements (SOC2, HIPAA, PCI-DSS)

### Creating a Custom Role

#### Via gcloud

```yaml
# custom-storage-role.yaml
title: "Custom Storage Reader"
description: "Read-only access to specific prefixes"
stage: "GA"
includedPermissions:
  - storage.objects.get
  - storage.objects.list
  - storage.buckets.get
```

```bash
gcloud iam roles create customStorageReader \
  --project=my-project \
  --file=custom-storage-role.yaml
```

#### Via Terraform

```hcl
resource "google_project_iam_custom_role" "storage_reader" {
  role_id     = "customStorageReader"
  title       = "Custom Storage Reader"
  description = "Read-only access to specific prefixes"
  permissions = [
    "storage.objects.get",
    "storage.objects.list",
    "storage.buckets.get"
  ]
  stage = "GA"
}

resource "google_storage_bucket_iam_member" "custom_reader" {
  bucket = google_storage_bucket.main.name
  role   = google_project_iam_custom_role.storage_reader.id
  member = "serviceAccount:my-app@my-project.iam.gserviceaccount.com"
}
```

### Custom Role Best Practices

1. **Start Minimal**: Begin with the fewest permissions needed, add as necessary
2. **Test in Dev**: Always test custom roles in non-production first
3. **Monitor Usage**: Use Cloud Audit Logs to verify the role provides sufficient access
4. **Version Control**: Store role definitions in IaC, not created manually
5. **Document Rationale**: Comment why each permission is needed

---

## IAM Policy Structure

### Policy Versions

| Version | Features | When to Use |
|---------|----------|-------------|
| **1** | Basic role bindings | Legacy systems |
| **2** | Conditional bindings | Rarely used |
| **3** | Conditions + fine-grained control | **RECOMMENDED** |

**ALWAYS use version 3** when reading and writing policies:

```python
policy = bucket.get_iam_policy(requested_policy_version=3)
```

### Policy JSON Structure

```json
{
  "version": 3,
  "etag": "BwWKMjU0NzE=",
  "bindings": [
    {
      "role": "roles/storage.objectViewer",
      "members": [
        "user:jane@example.com",
        "serviceAccount:my-app@my-project.iam.gserviceaccount.com"
      ],
      "condition": {
        "title": "expires_after_2025",
        "description": "Temporary access",
        "expression": "request.time < timestamp('2025-12-31T23:59:59Z')"
      }
    }
  ]
}
```

**Key Fields**:
- `version`: Policy format version (always 3)
- `etag`: Concurrency control (prevents simultaneous updates)
- `bindings`: Array of role + member + optional condition
- `members`: Can be users, groups, service accounts, or special identifiers

### Member Identifiers

| Type | Format | Example |
|------|--------|---------|
| User | `user:EMAIL` | `user:jane@example.com` |
| Group | `group:EMAIL` | `group:team@example.com` |
| Service Account | `serviceAccount:EMAIL` | `serviceAccount:app@proj.iam.gserviceaccount.com` |
| Domain | `domain:DOMAIN` | `domain:example.com` |
| All Users | `allUsers` | (Public access - avoid) |
| All Authenticated | `allAuthenticatedUsers` | (Any Google account - avoid) |
| Project SA Set | `principalSet://...` | All SAs in project/folder/org |

---

## Service Account Best Practices

### Service Account Types

| Type | Description | Best Practice |
|------|-------------|---------------|
| **User-managed** | Created by you, full control | **RECOMMENDED** for applications |
| **Compute Engine default** | Auto-created for GCE | Disable auto-grants, replace with user-managed |
| **App Engine default** | Auto-created for App Engine | Same as above |
| **Cloud Run default** | Auto-created for Cloud Run | Same as above |

### Service Account Security Checklist

```yaml
# DO:
- Create dedicated service accounts per application
- Grant minimum required permissions (least privilege)
- Use Workload Identity Federation for external access
- Rotate keys regularly (or avoid keys entirely)
- Monitor service account usage via audit logs
- Disable default service accounts if not needed

# DON'T:
- Share service accounts across unrelated applications
- Grant Editor/Owner roles to service accounts
- Store service account keys in code repositories
- Use default service accounts with auto-granted permissions
- Create long-lived keys when Workload Identity is available
```

### Workload Identity Federation (No Keys Needed)

For workloads outside GCP (AWS, Azure, on-prem, GitHub Actions):

```bash
# Create workload identity pool
gcloud iam workload-identity-pools create "my-pool" \
  --project="my-project" \
  --location="global" \
  --description="GitHub Actions pool"

# Add AWS provider
gcloud iam workload-identity-pools providers create-aws \
  "my-aws-provider" \
  --project="my-project" \
  --location="global" \
  --workload-identity-pool="my-pool" \
  --account-id="123456789012"

# Grant role to pool members
gsutil iam ch \
  "principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/my-pool/*:objectViewer" \
  gs://my-bucket
```

### Service Account Key Management

If you MUST use keys (prefer Workload Identity instead):

```bash
# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account=my-app@my-project.iam.gserviceaccount.com

# List keys
gcloud iam service-accounts keys list \
  --iam-account=my-app@my-project.iam.gserviceaccount.com

# Delete old key
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=my-app@my-project.iam.gserviceaccount.com
```

**Key Rotation Schedule**: Rotate every 90 days maximum. Automate with Cloud Functions or CI/CD.

---

## Signed URLs & Signed Policies

### What Are Signed URLs?

Signed URLs provide **time-limited access** to private objects without requiring IAM permissions. They're cryptographically signed with a service account's private key.

### Use Cases

- Allow users to upload files directly from browser
- Share private objects with external users temporarily
- Grant time-limited download access
- Secure webhook callbacks

### Generate Signed URLs (Python)

```python
import datetime
from google.cloud import storage

def generate_download_signed_url(bucket_name, blob_name):
    """Generate a time-limited download URL."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=15),
        method="GET",
    )
    
    return url

def generate_upload_signed_url(bucket_name, blob_name):
    """Generate a time-limited upload URL."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(hours=1),
        method="PUT",
        content_type="application/octet-stream",
    )
    
    return url

# Usage
download_url = generate_download_signed_url("my-bucket", "private-report.pdf")
print(f"Share this URL (valid for 15 minutes): {download_url}")
```

### Generate Signed URLs (Node.js)

```javascript
const {Storage} = require('@google-cloud/storage');
const storage = new Storage();

async function generateSignedUrl(bucketName, fileName) {
  const options = {
    version: 'v4',
    action: 'read',
    expires: Date.now() + 15 * 60 * 1000, // 15 minutes
  };

  const [url] = await storage
    .bucket(bucketName)
    .file(fileName)
    .getSignedUrl(options);

  console.log(`Generated signed URL: ${url}`);
  return url;
}

async function generateUploadSignedUrl(bucketName, fileName) {
  const options = {
    version: 'v4',
    action: 'write',
    expires: Date.now() + 60 * 60 * 1000, // 1 hour
    contentType: 'application/octet-stream',
  };

  const [url] = await storage
    .bucket(bucketName)
    .file(fileName)
    .getSignedUrl(options);

  return url;
}
```

### Signed Policy Documents (Browser Uploads)

For direct browser uploads without exposing credentials:

```python
from google.cloud import storage
import datetime

def generate_upload_policy(bucket_name, blob_name):
    """Generate a policy for browser-based uploads."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    policy = bucket.generate_upload_policy(
        conditions=[
            ["eq", "$key", blob_name],
            ["starts-with", "$Content-Type", "image/"],
        ],
        expiration=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    )
    
    return policy
```

### Signed URL Security Best Practices

1. **Short Expiration**: Use minimum time needed (minutes, not days)
2. **Specific Method**: Sign only GET, PUT, or DELETE (not all)
3. **Content-Type Validation**: Require matching content type for uploads
4. **Size Limits**: Set maximum upload size in policy
5. **Monitor Usage**: Log signed URL generation and access
6. **Rotate Signing Keys**: Use different service accounts for different purposes

---

## VPC Service Controls

### What Are VPC Service Controls?

VPC Service Controls create a **security perimeter** around GCP services (including GCS) to prevent data exfiltration and unauthorized access.

### When to Use

- Regulated industries (healthcare, finance, government)
- Multi-tenant architectures
- Data sovereignty requirements
- Compliance mandates (SOC2, HIPAA, PCI-DSS)

### Creating a Service Perimeter

```bash
# Create access level (who can access)
gcloud access-context-manager levels create "trusted-networks" \
  --title="Trusted Networks" \
  --description="Corporate and trusted networks" \
  --basic-level-spec=access-level.yaml \
  --policy=POLICY_ID

# Create service perimeter
gcloud access-context-manager perimeters create "gcs-perimeter" \
  --title="GCS Data Perimeter" \
  --description="Protects sensitive GCS buckets" \
  --resources=projects/123456789012 \
  --restricted-services=storage.googleapis.com \
  --access-levels=trusted-networks \
  --policy=POLICY_ID
```

### Perimeter Configuration (YAML)

```yaml
# access-level.yaml
- ipSubnetworks:
  - 10.0.0.0/8
  - 172.16.0.0/12
- members:
  - user:jane@example.com
  - serviceAccount:my-app@my-project.iam.gserviceaccount.com
```

### VPC Service Controls Limitations

- Adds complexity to cross-project access
- Can break legitimate external integrations
- Requires careful testing before production deployment
- Not all GCS features work within perimeters (e.g., signed URLs need explicit allow)

---

## Encryption Strategies

### Encryption Options

| Option | Description | Management | Performance | Use Case |
|--------|-------------|------------|-------------|----------|
| **Google-managed** | Encrypted with Google keys | Zero management | Fastest | Default, non-sensitive data |
| **CMEK** (Customer-Managed) | Encrypted with your Cloud KMS keys | You manage keys | Minimal overhead | Sensitive data, compliance |
| **CSEK** (Customer-Supplied) | Encrypted with your keys | You provide key per object | Key management overhead | Highly sensitive, regulatory |

### CMEK Configuration

#### Create KMS Key

```bash
# Create key ring
gcloud kms keyrings create "gcs-keys" \
  --location="us-central1"

# Create crypto key
gcloud kms keys create "gcs-bucket-key" \
  --location="us-central1" \
  --keyring="gcs-keys" \
  --purpose="encryption"

# Grant GCS service account access to key
gcloud kms keys add-iam-policy-binding \
  "gcs-bucket-key" \
  --location="us-central1" \
  --keyring="gcs-keys" \
  --member="serviceAccount:service-PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```

#### Create Bucket with CMEK

```bash
gcloud storage buckets create gs://my-secure-bucket \
  --location=us-central1 \
  --default-kms-key=projects/my-project/locations/us-central1/keyRings/gcs-keys/cryptoKeys/gcs-bucket-key
```

#### Terraform with CMEK

```hcl
resource "google_kms_key_ring" "gcs_keys" {
  name     = "gcs-keys"
  location = "us-central1"
}

resource "google_kms_crypto_key" "bucket_key" {
  name     = "gcs-bucket-key"
  key_ring = google_kms_key_ring.gcs_keys.id
  
  rotation_period = "7776000s" # 90 days
  
  lifecycle {
    prevent_destroy = false
  }
}

resource "google_storage_bucket" "encrypted" {
  name     = "my-secure-bucket"
  location = "US-CENTRAL1"
  
  encryption {
    default_kms_key_name = google_kms_crypto_key.bucket_key.id
  }
  
  depends_on = [google_kms_crypto_key_iam_member.gcs_encrypter]
}

resource "google_kms_crypto_key_iam_member" "gcs_encrypter" {
  crypto_key_id = google_kms_crypto_key.bucket_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:service-${data.google_project.current.number}@gs-project-accounts.iam.gserviceaccount.com"
}
```

### Encryption Best Practices

1. **Use CMEK for sensitive data**: PII, financial records, health data
2. **Rotate keys regularly**: 90-day rotation for high-security, annual for standard
3. **Separate key rings by environment**: dev-keys, staging-keys, prod-keys
4. **Monitor key usage**: Cloud Audit Logs track all encryption/decryption
5. **Plan key destruction carefully**: 24-hour waiting period minimum
6. **Never use CSEK unless required**: CMEK provides similar security with less complexity

---

## Public Access Prevention

### Why Prevent Public Access?

Public buckets are the #1 cause of data breaches in GCS. Even accidental public access can expose sensitive data permanently.

### Enforce Public Access Prevention

#### Via gcloud

```bash
# Enable on existing bucket
gcloud storage buckets update gs://my-bucket \
  --public-access-prevention=enforced

# Verify setting
gcloud storage buckets describe gs://my-bucket \
  --format="value(iamConfig.publicAccessPrevention)"
```

#### Via Terraform

```hcl
resource "google_storage_bucket" "main" {
  name     = "my-bucket"
  location = "US-CENTRAL1"
  
  # CRITICAL: Enforce public access prevention
  public_access_prevention = "enforced"
  
  # Also use uniform bucket-level access
  uniform_bucket_level_access = true
}
```

### Public Access Prevention Levels

| Setting | Behavior | When to Use |
|---------|----------|-------------|
| `inherited` | Inherits from org policy | Default, allows public if org allows |
| `enforced` | Blocks all public access | **RECOMMENDED** for all buckets |

**NEVER** use `allUsers` or `allAuthenticatedUsers` in IAM policies for production buckets.

---

## Condition-Based Access

### IAM Conditions

IAM Conditions allow **attribute-based access control**:

```hcl
resource "google_storage_bucket_iam_member" "time_limited" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectViewer"
  member = "user:contractor@example.com"
  
  condition {
    title       = "expires_end_of_contract"
    description = "Access expires 2025-12-31"
    expression  = "request.time < timestamp('2025-12-31T23:59:59Z')"
  }
}

resource "google_storage_bucket_iam_member" "prefix_limited" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:app@my-project.iam.gserviceaccount.com"
  
  condition {
    title       = "limit_to_uploads_prefix"
    description = "Can only access uploads/ prefix"
    expression  = "resource.name.startsWith('projects/_/buckets/my-bucket/objects/uploads/')"
  }
}
```

### Available Condition Attributes

| Attribute | Use | Example |
|-----------|-----|---------|
| `request.time` | Time-based access | `request.time < timestamp('2025-01-01T00:00:00Z')` |
| `resource.name` | Resource-based | `resource.name.endsWith('.pdf')` |
| `resource.service` | Service filtering | `resource.service == 'storage.googleapis.com'` |
| `resource.type` | Resource type | `resource.type == 'storage.googleapis.com/Object'` |

### Condition Best Practices

1. **Always add expiration**: Use time conditions for temporary access
2. **Test conditions**: Use IAM Policy Simulator before deploying
3. **Document rationale**: Explain why each condition exists
4. **Monitor expirations**: Alert before conditions expire to avoid outages
5. **Keep simple**: Complex conditions are hard to debug

---

## Audit & Compliance

### Cloud Audit Logs

GCS generates two types of audit logs:

| Log Type | What It Captures | Enabled By Default |
|----------|------------------|-------------------|
| **Admin Activity** | Bucket creation, deletion, IAM changes | ✅ Yes (cannot disable) |
| **Data Access** | Object reads, writes, metadata access | ❌ No (must enable) |

### Enable Data Access Logs

```bash
gcloud projects update-iam-policy my-project \
  --add-binding \
  --member="allAuthenticatedUsers" \
  --role="roles/logging.admin" \
  --condition=None

# Enable via Cloud Console: Logging > Logs Router > Create Sink
```

### Terraform: Enable Audit Logs

```hcl
resource "google_project_iam_audit_config" "gcs_audit" {
  project = "my-project"
  service = "storage.googleapis.com"
  
  audit_log_config {
    log_type = "ADMIN_READ"
  }
  
  audit_log_config {
    log_type = "DATA_READ"
  }
  
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}
```

### Query Audit Logs

```bash
# View bucket IAM changes
gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.methodName:storage.setIamPolicy" \
  --limit=10

# View object access by specific user
gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.authenticationInfo.principalEmail='user@example.com'" \
  --limit=50

# Export logs to BigQuery for analysis
gcloud logging sinks create gcs-audit-sink \
  bigquery.googleapis.com/projects/my-project/datasets/audit_logs \
  --log-filter="resource.type=gcs_bucket"
```

### Compliance Frameworks

| Framework | GCS Support | Key Requirements |
|-----------|-------------|------------------|
| **SOC2** | ✅ Certified | Audit logs, access controls, encryption |
| **HIPAA** | ✅ Eligible | BAA required, CMEK, audit logging |
| **PCI-DSS** | ✅ Certified | Encryption, access controls, monitoring |
| **GDPR** | ✅ Compliant | Data residency, deletion, access controls |
| **FedRAMP** | ✅ Authorized | Moderate & High impact levels |

---

## Security Automation

### Automated IAM Policy Validation

```python
from google.cloud import storage
import json

def audit_bucket_iam(bucket_name):
    """Audit bucket IAM policy for security issues."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    policy = bucket.get_iam_policy(requested_policy_version=3)
    
    issues = []
    
    for binding in policy.bindings:
        # Check for public access
        if "allUsers" in binding["members"] or "allAuthenticatedUsers" in binding["members"]:
            issues.append(f"CRITICAL: {binding['role']} granted to public")
        
        # Check for overly broad access
        if binding["role"] == "roles/storage.admin":
            for member in binding["members"]:
                if member.startswith("user:") or member.startswith("group:"):
                    issues.append(f"WARNING: {binding['role']} granted to {member}")
        
        # Check for service accounts with admin
        if binding["role"] in ["roles/storage.admin", "roles/storage.objectAdmin"]:
            for member in binding["members"]:
                if "default-compute" in member:
                    issues.append(f"DANGER: Default SA with admin role")
    
    return issues

# Run audit
issues = audit_bucket_iam("my-bucket")
for issue in issues:
    print(f"⚠️  {issue}")
```

### Automated Public Access Detection

```bash
#!/bin/bash
# Scan all buckets for public access

PROJECT_ID="my-project"

for bucket in $(gsutil ls); do
    policy=$(gsutil iam get $bucket 2>/dev/null)
    
    if echo "$policy" | grep -q "allUsers"; then
        echo "🚨 PUBLIC: $bucket"
    fi
    
    if echo "$policy" | grep -q "allAuthenticatedUsers"; then
        echo "⚠️  AUTHENTICATED: $bucket"
    fi
done
```

### Terraform: Enforce Security Baseline

```hcl
# Organization policy to prevent public buckets
resource "google_org_policy_policy" "no_public_buckets" {
  name   = "projects/${var.project_id}/policies/storage.publicAccessPrevention"
  parent = "projects/${var.project_id}"
  
  spec {
    rules {
      enforce = "TRUE"
    }
  }
}

# Module with security defaults
module "secure_bucket" {
  source = "./modules/gcs-secure-bucket"
  
  name                        = var.bucket_name
  location                    = var.location
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  versioning_enabled          = true
  enable_audit_logs           = true
}
```

---

## Common Security Mistakes

### 🚨 Critical Mistakes

1. **Public Buckets**: Accidentally exposing data via `allUsers`
   - **Fix**: Enforce public access prevention, audit regularly
   
2. **Service Account Key Leaks**: Storing keys in GitHub
   - **Fix**: Use Workload Identity, rotate keys, scan repos
   
3. **Overly Broad IAM**: Granting `roles/storage.admin` to users
   - **Fix**: Use least-privilege, object-level roles only
   
4. **Default Service Accounts**: Using auto-created SAs with Editor role
   - **Fix**: Create dedicated SAs, disable auto-grants
   
5. **No Audit Logging**: Can't investigate incidents
   - **Fix**: Enable all audit log types, export to SIEM

### ⚠️ Common Mistakes

6. **Long-lived Signed URLs**: URLs valid for days/weeks
   - **Fix**: Use minutes/hours, monitor generation
   
7. **Ignoring Egress to Unknown Destinations**: Data exfiltration risk
   - **Fix**: VPC Service Controls, egress monitoring
   
8. **Not Testing IAM Changes**: Breaking production access
   - **Fix**: Test in dev, use IAM Policy Simulator
   
9. **Manual IAM Management**: Direct console changes without audit trail
   - **Fix**: Use Terraform, version control all changes
   
10. **Missing Key Rotation**: Keys never rotated
    - **Fix**: Automate rotation, set calendar reminders

### Security Checklist (Monthly Review)

- [ ] Audit all bucket IAM policies
- [ ] Review service account keys
- [ ] Check audit logs for anomalies
- [ ] Verify public access prevention on all buckets
- [ ] Rotate service account keys
- [ ] Review signed URL generation patterns
- [ ] Test disaster recovery procedures
- [ ] Update organization policies
- [ ] Review VPC Service Controls
- [ ] Check encryption key rotation status

---

## Quick Reference Commands

```bash
# Audit all buckets for public access
gsutil -m ls | xargs -I {} gsutil iam get {} | grep -B5 "allUsers"

# List service account keys
gcloud iam service-accounts keys list --iam-account=SA_EMAIL

# Test IAM permissions
gsutil iam test-permissions gs://my-bucket storage.objects.get storage.objects.create

# Get bucket security configuration
gcloud storage buckets describe gs://my-bucket --format="yaml(iamConfig,versioning,lifecycle)"

# Enable uniform bucket-level access
gcloud storage buckets update gs://my-bucket --uniform-bucket-level-access
```

---

*"Security is not a feature, it's a process. Audit often, grant minimally, and assume breach."* — Security Engineer Mantra
