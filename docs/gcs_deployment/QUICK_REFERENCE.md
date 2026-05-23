# GCS Quick Reference & Checklists

**Purpose**: At-a-glance reference for daily operations  
**Print this page and keep it handy**

---

## 🚀 Bucket Creation Checklist

### Production Bucket

```bash
# 1. Create bucket
gsutil mb -l US-CENTRAL1 gs://my-app-prod-data

# 2. Enable uniform bucket-level access
gcloud storage buckets update gs://my-app-prod-data --uniform-bucket-level-access

# 3. Enforce public access prevention
gcloud storage buckets update gs://my-app-prod-data --public-access-prevention=enforced

# 4. Enable versioning
gsutil versioning set on gs://my-app-prod-data

# 5. Set lifecycle rules
gsutil lifecycle set lifecycle.json gs://my-app-prod-data

# 6. Grant IAM access
gsutil iam ch serviceAccount:my-app@project.iam.gserviceaccount.com:objectAdmin gs://my-app-prod-data

# 7. Verify configuration
gcloud storage buckets describe gs://my-app-prod-data
```

### Terraform Production Bucket

```hcl
resource "google_storage_bucket" "prod" {
  name     = "my-app-prod-data"
  location = "US-CENTRAL1"
  
  uniform_bucket_level_access    = true
  public_access_prevention       = "enforced"
  force_destroy                  = false
  
  versioning {
    enabled = true
  }
  
  lifecycle {
    prevent_destroy = true
  }
}
```

---

## 🔐 Security Checklist

### Bucket Security

- [ ] Uniform bucket-level access enabled
- [ ] Public access prevention = "enforced"
- [ ] No `allUsers` or `allAuthenticatedUsers` in IAM
- [ ] Service accounts have minimum required roles
- [ ] CMEK enabled for sensitive data
- [ ] Audit logging enabled (Admin Activity + Data Access)
- [ ] VPC Service Controls (if enterprise)
- [ ] Organization policies enforced
- [ ] Signed URLs have short expiration (< 1 hour)
- [ ] Lifecycle rules configured

### IAM Security

- [ ] Using groups instead of individual users
- [ ] Custom roles instead of predefined (when possible)
- [ ] No Editor/Owner roles on buckets
- [ ] Service account keys rotated (or eliminated via Workload Identity)
- [ ] Conditional IAM for temporary access
- [ ] IAM changes reviewed in PR/MR
- [ ] IAM changes tested in non-prod first

---

## 💰 Cost Optimization Checklist

### Monthly Review

- [ ] Check storage growth trend
- [ ] Review egress costs by bucket
- [ ] Identify buckets with no recent access
- [ ] Audit versioning overhead
- [ ] Check for incomplete multipart uploads
- [ ] Review operation costs
- [ ] Compare actual vs budget

### Quarterly Review

- [ ] Evaluate Autoclass candidates
- [ ] Review lifecycle rule effectiveness
- [ ] Clean up unused buckets
- [ ] Assess CDN hit rates
- [ ] Review storage class distribution
- [ ] Negotiate committed use (if applicable)

### Optimization Actions

- [ ] Enable lifecycle rules on all buckets
- [ ] Use Autoclass for unpredictable access
- [ ] Enable CDN for frequently accessed content
- [ ] Compress text-based data before upload
- [ ] Colocate compute and storage
- [ ] Clean up old object versions
- [ ] Set budget alerts

---

## ⚡ Performance Checklist

### Upload Performance

- [ ] Use `gsutil -m` for parallel uploads
- [ ] Use resumable uploads for > 10 MB
- [ ] Chunk size: 32-64 MB for large files
- [ ] Compress text-based data
- [ ] Avoid sequential object naming
- [ ] Use diverse prefixes for high-write workloads
- [ ] Set appropriate timeouts (5-30 min for large)

### Download Performance

- [ ] Use `gsutil -m` for parallel downloads
- [ ] Enable CDN for frequently accessed objects
- [ ] Set Cache-Control headers
- [ ] Use range reads for partial access
- [ ] Implement client-side caching
- [ ] Use hedged requests for latency-sensitive reads

### General Performance

- [ ] Colocate compute and storage
- [ ] Use HTTP/2 transport
- [ ] Enable connection pooling
- [ ] Configure retry logic
- [ ] Monitor Cloud Monitoring metrics
- [ ] Set up alert policies

---

## 📊 Storage Class Decision Tree

```
How often is data accessed?
├── Daily/Weekly → Standard
├── Monthly → Nearline
├── Quarterly → Coldline
└── Yearly → Archive

Is access pattern predictable?
├── Yes → Use lifecycle rules
└── No → Enable Autoclass

Does data need to be immediately available?
├── Yes → Standard, Nearline, or Autoclass
└── No → Coldline or Archive

What's the minimum storage duration?
├── < 30 days → Standard
├── 30-90 days → Nearline
├── 90-365 days → Coldline
└── > 365 days → Archive
```

---

## 🌍 Location Selection Quick Guide

```
Where is compute?
├── Single region → Same region as compute
├── Multiple regions → Dual-region or Multi-region
└── On-premises → Closest region

Data residency requirements?
├── GDPR (EU only) → EU multi-region
├── Data sovereignty → Specific country region
└── None → Optimize for latency/cost

Budget constraints?
├── Minimize cost → Region or Zone
├── Balance → Dual-region
└ Maximize availability → Multi-region
```

---

## 🔧 Essential Commands Reference

### Bucket Operations

```bash
# List buckets
gsutil ls

# Create bucket
gsutil mb -l REGION gs://bucket-name

# Delete bucket (must be empty)
gsutil rb gs://bucket-name

# Describe bucket
gcloud storage buckets describe gs://bucket-name

# Update bucket settings
gcloud storage buckets update gs://bucket-name [OPTIONS]
```

### Object Operations

```bash
# Upload
gsutil cp local-file gs://bucket/path/
gsutil -m cp -r local-dir gs://bucket/path/

# Download
gsutil cp gs://bucket/path/file local-file
gsutil -m cp -r gs://bucket/path/ local-dir

# List objects
gsutil ls gs://bucket/path/
gsutil ls -l gs://bucket/path/  # With details
gsutil ls -a gs://bucket/path/  # All versions

# Delete
gsutil rm gs://bucket/path/file
gsutil -m rm gs://bucket/path/**

# Move (copy + delete)
gsutil mv gs://bucket/old-path/** gs://bucket/new-path/
```

### IAM Operations

```bash
# Get IAM policy
gsutil iam get gs://bucket > policy.json

# Set IAM policy
gsutil iam set policy.json gs://bucket

# Change IAM (add/remove)
gsutil iam ch user:email@example.com:objectViewer gs://bucket
gsutil iam ch -d user:email@example.com:objectViewer gs://bucket

# Test permissions
gsutil iam test-permissions gs://bucket storage.objects.get
```

### Lifecycle Operations

```bash
# Get lifecycle rules
gsutil lifecycle get gs://bucket

# Set lifecycle rules
gsutil lifecycle set lifecycle.json gs://bucket

# Clear lifecycle rules
gsutil lifecycle set /dev/null gs://bucket
```

### Versioning Operations

```bash
# Enable versioning
gsutil versioning set on gs://bucket

# Disable versioning
gsutil versioning set off gs://bucket

# List all versions
gsutil ls -a gs://bucket/object

# Restore version
gsutil cp gs://bucket/object#generation gs://bucket/object
```

### Logging & Monitoring

```bash
# View recent errors
gcloud logging read "resource.type=gcs_bucket AND severity>=ERROR" --limit=20

# View IAM changes
gcloud logging read "resource.type=gcs_bucket AND protoPayload.methodName:storage.setIamPolicy" --limit=10

# View object deletions
gcloud logging read "resource.type=gcs_bucket AND protoPayload.methodName:storage.objects.delete" --limit=20

# Check bucket metrics
gcloud monitoring metrics list --filter="resource.type=gcs_bucket"
```

---

## 🚨 Incident Response Quick Guide

### Data Breach

```
1. CONTAIN: Remove public access immediately
   gsutil iam ch -d allUsers:objectViewer gs://bucket
   gsutil iam ch -d allAuthenticatedUsers:objectViewer gs://bucket

2. ASSESS: Check audit logs for scope
   gcloud logging read "resource.type=gcs_bucket AND severity>=ERROR" --limit=100

3. NOTIFY: Security team + affected users

4. REMEDIATE: Fix IAM, enable prevention
   gcloud storage buckets update gs://bucket --public-access-prevention=enforced

5. DOCUMENT: Create incident report

6. REVIEW: Update security controls
```

### Performance Degradation

```
1. IDENTIFY: Check monitoring dashboards

2. ISOLATE: Determine scope (bucket-wide or prefix-specific?)

3. MITIGATE:
   - Enable parallelism: gsutil -m ...
   - Check for hotspots
   - Verify network connectivity

4. RESOLVE: Implement fix

5. MONITOR: Verify recovery

6. POST-MORTEM: Document and prevent recurrence
```

### Cost Spike

```
1. IDENTIFY: Check billing export
   SELECT * FROM billing_export WHERE service.description = 'Cloud Storage' ORDER BY cost DESC

2. INVESTIGATE:
   - Storage growth?
   - Egress spike?
   - Versioning overhead?
   - New buckets?

3. MITIGATE:
   - Clean up unused data
   - Enable lifecycle rules
   - Review egress patterns

4. PREVENT:
   - Set budget alerts
   - Implement cost monitoring
   - Review before deploying changes
```

---

## 📋 Common Lifecycle Rule Templates

### Template 1: Log Retention

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

### Template 2: Backup with Versioning

```json
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {
        "age": 90,
        "num_newer_versions": 5,
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

### Template 3: Upload Bucket Cleanup

```json
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": 30}
    }
  ]
}
```

---

## 🎯 Best Practices Summary

### DO

✅ Use uniform bucket-level access  
✅ Enforce public access prevention  
✅ Enable versioning for critical data  
✅ Configure lifecycle rules  
✅ Use least-privilege IAM  
✅ Monitor with Cloud Monitoring  
✅ Set up budget alerts  
✅ Use Autoclass for unpredictable access  
✅ Colocate compute and storage  
✅ Use parallel operations for bulk transfers  
✅ Compress text-based data  
✅ Enable audit logging  
✅ Test in non-prod first  
✅ Use Terraform for infrastructure  
✅ Document everything  

### DON'T

❌ Make buckets publicly accessible  
❌ Use sequential object naming for high-write workloads  
❌ Grant Editor/Owner roles for bucket access  
❌ Store service account keys in code  
❌ Ignore cost growth  
❌ Skip lifecycle rules  
❌ Use multi-region when single region suffices  
❌ Deploy directly to production  
❌ Forget to monitor  
❌ Leave test buckets running  
❌ Use fine-grained ACLs (use uniform access)  
❌ Hardcode credentials  
❌ Skip disaster recovery testing  

---

*"Print this, laminate it, and keep it at your desk. Your future self will thank you."* — Practical Engineer
