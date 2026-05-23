# Troubleshooting - Google Cloud Storage

**Level**: Intermediate to Expert  
**Prerequisites**: All previous documents  
**Time to Master**: Ongoing (learn from every incident)

---

## Table of Contents

1. [Common Errors & Solutions](#common-errors--solutions)
2. [Access Issues](#access-issues)
3. [Performance Issues](#performance-issues)
4. [Upload Failures](#upload-failures)
5. [Download Failures](#download-failures)
6. [IAM Problems](#iam-problems)
7. [Lifecycle Rule Issues](#lifecycle-rule-issues)
8. [Cost Anomalies](#cost-anomalies)
9. [Replication Issues](#replication-issues)
10. [Debugging Tools](#debugging-tools)
11. [Log Analysis](#log-analysis)
12. [Support Escalation](#support-escalation)

---

## Common Errors & Solutions

### Error 403: Forbidden

```
Error: 403 Forbidden - user does not have storage.objects.get access

Causes:
1. Missing IAM role on bucket
2. Service account not granted role
3. VPC Service Controls blocking access
4. Public access prevention enforced

Diagnosis:
gsutil iam get gs://my-bucket
gcloud logging read "resource.type=gcs_bucket AND severity=ERROR" --limit=10

Fix:
gsutil iam ch user:email@example.com:objectViewer gs://my-bucket
```

### Error 404: Not Found

```
Error: 404 Not Found - Bucket not found

Causes:
1. Typo in bucket name
2. Bucket was deleted
3. Wrong project context

Diagnosis:
gsutil ls gs://my-bucket
gcloud storage buckets list --filter="name:my-bucket"

Fix:
- Verify bucket name (case-sensitive, lowercase only)
- Check if bucket exists in Cloud Console
- Verify you're authenticated to correct project
```

### Error 409: Conflict

```
Error: 409 Conflict - Bucket already exists

Causes:
1. Bucket name globally unique (even across deleted buckets)
2. Name reserved by Google

Fix:
- Use different bucket name
- Add random suffix: my-bucket-$(date +%s)
- Never use "google" or similar in names
```

### Error 429: Too Many Requests

```
Error: 429 Too Many Requests - Rate limit exceeded

Causes:
1. Exceeding per-prefix QPS limit (~5,000 QPS)
2. Hotspot from sequential naming
3. Burst traffic

Diagnosis:
gcloud logging read "resource.type=gcs_bucket AND protoPayload.status.code=429" --limit=20

Fix:
- Implement retry with exponential backoff
- Use diverse object prefixes
- Enable parallel operations with different prefixes
- Use hash-based naming for high-write workloads
```

---

## Access Issues

### Cannot List Bucket Contents

```
Symptom: gsutil ls gs://my-bucket fails
Permission Denied

Check IAM:
1. Does user have roles/storage.objectViewer or higher?
2. Is uniform bucket-level access enabled?
3. Is public access prevention enforced?

gsutil iam get gs://my-bucket | grep -A5 "objectViewer"

Fix:
gsutil iam ch user:email@example.com:objectViewer gs://my-bucket
```

### Cannot Upload Objects

```
Symptom: Upload fails with 403 Forbidden

Check:
1. Does SA/user have roles/storage.objectCreator or higher?
2. Is bucket full? (unlikely, but check project quota)
3. Is VPC Service Controls blocking upload?

Fix:
gsutil iam ch serviceAccount:my-app@project.iam.gserviceaccount.com:objectCreator gs://my-bucket
```

### Service Account Access Denied

```
Symptom: Application gets 403, but IAM looks correct

Check:
1. Is SA using correct email? (typos happen)
2. Is ADC configured correctly?
3. Is Workload Identity configured?

gcloud iam service-accounts describe my-app@project.iam.gserviceaccount.com
gcloud auth list  # Check active account

Fix:
gcloud auth activate-service-account --key-file=key.json
export GOOGLE_APPLICATION_CREDENTIALS=key.json
```

---

## Performance Issues

### Slow Uploads

```
Symptom: Upload speed < 10 MB/s

Diagnosis:
1. Check network bandwidth
   speedtest-cli
   
2. Check if using parallel uploads
   gsutil -m cp file.txt gs://my-bucket/
   
3. Check object size (small files have overhead)
   ls -lh file.txt
   
4. Check bucket location vs client location
   gsutil ls -L gs://my-bucket | grep Location

Fix:
- Use gsutil -m for parallel uploads
- Use resumable uploads for >10 MB
- Increase thread count: gsutil -o GSUtil:thread_count=100 -m cp ...
- Colocate client and bucket
```

### Slow Downloads

```
Symptom: Download speed < 10 MB/s

Diagnosis:
1. Same as slow uploads
2. Check if object is in cold storage (retrieval fees apply)
3. Check network path

gsutil ls -L gs://my-bucket/large-file.bin | grep "Storage class"

Fix:
- Use gsutil -m for parallel downloads
- Use Cloud CDN for frequently accessed objects
- Check if object is Nearline/Coldline/Archive (has retrieval costs)
```

### High Latency

```
Symptom: First-byte latency > 500ms

Diagnosis:
1. Check client-to-bucket distance
2. Check for hotspot (sequential naming)
3. Check request rate

# Check object naming
gsutil ls gs://my-bucket/ | head -20

Fix:
- Use diverse prefixes
- Use hash-based naming
- Enable connection pooling
- Use gRPC transport
- Implement hedged requests for latency-sensitive apps
```

---

## Upload Failures

### Multipart Upload Failures

```
Symptom: Large file upload fails partway

Check:
1. Network stability
2. Timeout settings
3. Chunk size

Fix:
# Use resumable upload
gsutil cp large-file.bin gs://my-bucket/

# Python resumable upload
blob = bucket.blob("large-file.bin")
blob.chunk_size = 5 * 1024 * 1024  # 5 MB chunks
blob.upload_from_filename("large-file.bin")
```

### Incomplete Multipart Uploads

```
Symptom: Storage costs increasing without new objects

Check for incomplete uploads:
gsutil ls -a gs://my-bucket/** | grep "#$"

Fix:
# Add lifecycle rule to cleanup
{
  "rule": [
    {
      "action": {"type": "AbortIncompleteMultipartUpload"},
      "condition": {"age": 7}
    }
  ]
}

gsutil lifecycle set lifecycle.json gs://my-bucket
```

---

## Download Failures

### Range Read Failures

```
Symptom: Partial downloads fail

Check:
1. Object exists and is accessible
2. Range header is valid
3. Object size >= range end

Fix:
# Test full download first
gsutil cp gs://my-bucket/file.bin /tmp/file.bin

# Then test range read
curl -H "Range: bytes=0-1023" https://storage.googleapis.com/my-bucket/file.bin
```

### Signed URL Failures

```
Symptom: Signed URL returns 403

Check:
1. URL not expired
2. HTTP method matches (GET vs PUT)
3. Content-Type matches (if specified)
4. Object exists

Diagnosis:
# Generate new signed URL with longer expiration
python -c "
from google.cloud import storage
import datetime
client = storage.Client()
blob = client.bucket('my-bucket').blob('file.txt')
url = blob.generate_signed_url(
    version='v4',
    expiration=datetime.timedelta(hours=1),
    method='GET'
)
print(url)
"

Fix:
- Increase expiration time
- Verify method matches
- Check content-type if specified
- Regenerate with correct parameters
```

---

## IAM Problems

### IAM Changes Not Taking Effect

```
Symptom: Added IAM binding, but still getting 403

Check:
1. IAM propagation delay (usually < 1 minute, can be 7 minutes)
2. Correct role granted?
3. Correct member format?

Wait 2-3 minutes and retry.

If still failing:
gsutil iam get gs://my-bucket > current-policy.json
cat current-policy.json  # Verify binding exists
```

### IAM Policy Too Large

```
Symptom: Cannot add more IAM bindings

Check policy size:
gsutil iam get gs://my-bucket | wc -c

Fix:
1. Use Google Groups instead of individual users
2. Use custom roles to reduce binding count
3. Use conditions to combine access patterns
4. Remove unused bindings
```

### Lost Access After IAM Change

```
Symptom: Team lost access after IAM policy update

Recovery:
1. Check Cloud Audit Logs for who made change
2. Restore previous policy from version control (if using Terraform)
3. Use IAM Policy Simulator to test before applying

gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.methodName:storage.setIamPolicy" \
  --limit=5
```

---

## Lifecycle Rule Issues

### Objects Not Being Deleted

```
Symptom: Lifecycle rule should delete objects, but they remain

Check:
1. Rule syntax correct?
2. Condition met? (age, createdBefore, etc.)
3. Versioning enabled? (noncurrent versions handled differently)
4. Retention policy blocking deletion?

gsutil lifecycle get gs://my-bucket

Fix:
# Test rule manually
gsutil lifecycle set test-lifecycle.json gs://my-bucket

# Check object age
gsutil ls -L gs://my-bucket/object.txt | grep "Creation time"
```

### Lifecycle Deleting Too Much

```
Symptom: Objects deleted earlier than expected

Recovery:
1. Check if versioning enabled (can restore versions)
2. Check if soft delete enabled (can restore)
3. Fix lifecycle rule immediately

gsutil ls -a gs://my-bucket/deleted-object.txt  # List all versions

Fix lifecycle:
# Increase age threshold
# Add matchesStorageClass condition
# Add numNewerVersions condition
```

---

## Cost Anomalies

### Sudden Cost Increase

```
Symptom: GCS bill doubled overnight

Investigation:
1. Check storage growth
   SELECT DATE(usage_start_time) as date, SUM(cost) as cost
   FROM `billing_export`
   WHERE service.description = 'Cloud Storage'
   GROUP BY 1 ORDER BY 1 DESC LIMIT 30

2. Check egress volume
   gcloud logging read "resource.type=gcs_bucket AND protoPayload.methodName:storage.objects.get" --limit=100

3. Check for new buckets
   gsutil ls

4. Check versioning overhead
   gsutil ls -a gs://my-bucket/** | wc -l

Common Causes:
- Application bug creating duplicate objects
- Versioning with frequent updates
- Cross-region egress spike
- New bucket created without lifecycle rules
```

### Storage Growing Unexpectedly

```
Symptom: Storage grew 10x in one day

Investigation:
1. List largest objects
   gsutil du -sh gs://my-bucket/** | sort -rh | head -20

2. Check for duplicate uploads
   gsutil ls -l gs://my-bucket/** | awk '{print $2}' | sort | uniq -c | sort -rn | head -20

3. Check versioning
   gsutil ls -a gs://my-bucket/ | wc -l

Fix:
# If duplicates, delete them
gsutil -m rm gs://my-bucket/duplicate-prefix/**

# Add lifecycle rule
gsutil lifecycle set cleanup.json gs://my-bucket
```

---

## Replication Issues

### Cross-Region Replication Lag

```
Symptom: Objects not appearing in destination bucket

Check:
1. Transfer job status
   gcloud storage transfer jobs list

2. Source bucket accessibility
   gsutil ls gs://source-bucket

3. Destination bucket permissions
   gsutil iam get gs://dest-bucket

Fix:
# Restart transfer job
gcloud storage transfer jobs run JOB_NAME

# Check transfer logs
gcloud logging read "resource.type=cloud_data_transfer" --limit=50
```

### Dual-Region Inconsistency

```
Symptom: Object visible in one region but not other

This is NORMAL for dual-region buckets (eventual consistency).

Wait: Usually resolves within seconds, can take minutes.

If persists > 1 hour:
1. Check RPO setting
2. Contact Google Cloud Support
3. Check for ongoing outages
```

---

## Debugging Tools

### gsutil Debug Mode

```bash
# Verbose output
gsutil -D cp file.txt gs://my-bucket/

# Even more verbose
gsutil -DD cp file.txt gs://my-bucket/

# Show HTTP requests
gsutil -D ls gs://my-bucket
```

### Cloud Logging Queries

```bash
# All GCS errors
gcloud logging read \
  "resource.type=gcs_bucket AND severity>=ERROR" \
  --limit=50

# Specific bucket errors
gcloud logging read \
  'resource.type=gcs_bucket AND resource.labels.bucket_name="my-bucket" AND severity>=ERROR' \
  --limit=50

# IAM-related logs
gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.methodName:storage.setIamPolicy" \
  --limit=20
```

### Network Debugging

```bash
# Test connectivity to GCS
curl -I https://storage.googleapis.com

# Test upload speed
gsutil perf test gs://my-bucket

# Trace route to GCS
traceroute storage.googleapis.com
```

---

## Log Analysis

### Export Logs for Analysis

```bash
# Create log sink to BigQuery
gcloud logging sinks create gcs-logs \
  bigquery.googleapis.com/projects/my-project/datasets/gcs_logs \
  --log-filter="resource.type=gcs_bucket"

# Create log sink to GCS
gcloud logging sinks create gcs-logs-backup \
  storage.googleapis.com/projects/my-project/buckets/gcs-log-archive \
  --log-filter="resource.type=gcs_bucket"
```

### Common Analysis Queries

```sql
-- Error rate by day
SELECT
  DATE(timestamp) as day,
  COUNTIF(severity >= 'ERROR') as errors,
  COUNT(*) as total,
  COUNTIF(severity >= 'ERROR') / COUNT(*) as error_rate
FROM `my-project.gcs_logs.log_entries`
GROUP BY 1
ORDER BY 1 DESC

-- Top error types
SELECT
  protoPayload.status.message,
  COUNT(*) as count
FROM `my-project.gcs_logs.log_entries`
WHERE severity >= 'ERROR'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 20

-- Access patterns by user
SELECT
  protoPayload.authenticationInfo.principalEmail,
  protoPayload.methodName,
  COUNT(*) as count
FROM `my-project.gcs_logs.log_entries`
GROUP BY 1, 2
ORDER BY 3 DESC
LIMIT 50
```

---

## Support Escalation

### When to Contact Support

| Issue | Severity | When to Contact |
|-------|----------|-----------------|
| **Data loss** | Critical | Immediately |
| **Service outage** | Critical | After 15 minutes |
| **Security breach** | Critical | Immediately |
| **Billing dispute** | High | After internal review |
| **Performance degradation** | High | After self-diagnosis |
| **Feature request** | Low | Via feature request form |

### Gathering Support Info

```bash
# Collect bucket info
gsutil ls -L gs://my-bucket > bucket-info.txt

# Collect IAM policy
gsutil iam get gs://my-bucket > iam-policy.json

# Collect lifecycle rules
gsutil lifecycle get gs://my-bucket > lifecycle.json

# Collect recent errors
gcloud logging read \
  "resource.type=gcs_bucket AND severity>=ERROR" \
  --limit=100 > recent-errors.json

# Collect project info
gcloud projects describe my-project > project-info.json
```

### Support Ticket Template

```
Subject: [SEVERITY] - Brief description of issue

Project ID: my-project
Bucket: gs://my-bucket
Region: us-central1

Issue Description:
[What happened, when, impact]

Expected Behavior:
[What should have happened]

Steps to Reproduce:
1. Step 1
2. Step 2
3. Step 3

Troubleshooting Done:
- [List what you've already tried]

Attachments:
- bucket-info.txt
- iam-policy.json
- recent-errors.json
- screenshots (if applicable)

Business Impact:
[Describe impact on users/revenue/compliance]
```

---

## Quick Diagnostic Commands

```bash
# Full bucket health check
echo "=== Bucket Info ==="
gsutil ls -L gs://my-bucket

echo "=== IAM Policy ==="
gsutil iam get gs://my-bucket

echo "=== Lifecycle Rules ==="
gsutil lifecycle get gs://my-bucket

echo "=== Versioning ==="
gsutil versioning get gs://my-bucket

echo "=== Recent Errors ==="
gcloud logging read "resource.type=gcs_bucket AND severity>=ERROR" --limit=10

echo "=== Storage Usage ==="
gsutil du -sh gs://my-bucket

echo "=== Object Count ==="
gsutil ls gs://my-bucket/** | wc -l
```

---

*"Every error is a lesson. Document it, automate the fix, and share the knowledge."* — Veteran SRE Wisdom
