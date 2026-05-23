# Cost Optimization - Google Cloud Storage

**Level**: Intermediate to Expert  
**Prerequisites**: [Bucket Configuration](./BUCKET_CONFIGURATION.md)  
**Time to Master**: 2-3 weeks of cost analysis and optimization

---

## Table of Contents

1. [Cost Components](#cost-components)
2. [Storage Costs](#storage-costs)
3. [Operation Costs](#operation-costs)
4. [Network & Egress Costs](#network--egress-costs)
5. [Retrieval Fees](#retrieval-fees)
6. [Early Deletion Fees](#early-deletion-fees)
7. [Cost Optimization Strategies](#cost-optimization-strategies)
8. [Autoclass Economics](#autoclass-economics)
9. [CDN Integration Savings](#cdn-integration-savings)
10. [Cost Monitoring](#cost-monitoring)
11. [Budget Alerts](#budget-alerts)
12. **Cost Allocation & Tagging**
13. [Common Cost Pitfalls](#common-cost-pitfalls)
14. [Cost Optimization Checklist](#cost-optimization-checklist)

---

## Cost Components

GCS billing has **5 major components**:

```
Total GCS Cost = Storage + Operations + Network Egress + Retrieval + Early Deletion
```

| Component | Description | Typical % of Bill |
|-----------|-------------|-------------------|
| **Storage** | GB/month stored | 40-60% |
| **Operations** | API requests (A, B, C, D classes) | 5-15% |
| **Network Egress** | Data transfer out of GCS | 20-40% |
| **Retrieval** | Reading from cold storage | 5-10% |
| **Early Deletion** | Deleting before minimum duration | 0-10% |

---

## Storage Costs

### Pricing by Storage Class (US Regions)

| Storage Class | $/GB/Month | Durability | Min Duration |
|---------------|------------|------------|--------------|
| **Standard** | $0.020 | 99.999999999% | None |
| **Nearline** | $0.010 | 99.999999999% | 30 days |
| **Coldline** | $0.004 | 99.999999999% | 90 days |
| **Archive** | $0.0012 | 99.999999999% | 365 days |
| **Zonal (Rapid)** | $0.108 | 99.999999999% | None |

### Location Multipliers

| Location Type | Cost Multiplier | Example |
|---------------|-----------------|---------|
| Regional | 1.0x (baseline) | us-central1 |
| Dual-region | 1.1x | NAM4 |
| Multi-region | 1.15-1.3x | US, EU |
| Zonal | 5.4x | us-central1-a (Rapid bucket) |

### Storage Cost Calculation

```
Monthly Storage Cost = Average GB Stored × Price/GB/Month

Example: 10 TB in Standard, US-CENTRAL1
= 10,240 GB × $0.020/GB/month
= $204.80/month
= $2,457.60/year

Same data in Nearline:
= 10,240 GB × $0.010/GB/month
= $102.40/month (50% savings!)
= $1,228.80/year

Same data in Archive:
= 10,240 GB × $0.0012/GB/month
= $12.29/month (94% savings!)
= $147.48/year
```

### Billed Storage Details

**What counts toward storage costs**:
- Live object data
- Noncurrent object versions (if versioning enabled)
- Soft-deleted objects
- Incomplete multipart upload parts
- Custom metadata (negligible)

**What does NOT count**:
- Bucket configuration metadata
- IAM policies
- Lifecycle rules

---

## Operation Costs

### Operation Classes

| Class | Operations | Regional Price (per 1,000) | Examples |
|-------|------------|---------------------------|----------|
| **Class A** | Writes/Config | $0.005 | Create object, set IAM, set lifecycle |
| **Class B** | Reads/Metadata | $0.0004 | Get object, list objects, get metadata |
| **Class C** | Rapid Bucket Only | $0.000625 | Rapid bucket specific |
| **Class D** | Rapid Bucket Only | $0.00002 | Rapid bucket specific |
| **Free** | Various | $0.00 | Delete object, get bucket metadata |

### Dual/Multi-Region Operation Pricing

| Class | Regional | Dual/Multi-Region |
|-------|----------|-------------------|
| Class A | $0.005/1k | $0.010/1k (2x) |
| Class B | $0.0004/1k | $0.0008/1k (2x) |

### Operation Cost Examples

```
Scenario 1: High-write application
- 1 million writes/day (Class A)
- 100,000 reads/day (Class B)

Class A: 1,000,000 × 30 / 1,000 × $0.005 = $150/month
Class B: 100,000 × 30 / 1,000 × $0.0004 = $1.20/month
Total Operations: $151.20/month

Scenario 2: Read-heavy analytics
- 10,000 writes/day (Class A)
- 10 million reads/day (Class B)

Class A: 10,000 × 30 / 1,000 × $0.005 = $1.50/month
Class B: 10,000,000 × 30 / 1,000 × $0.0004 = $120/month
Total Operations: $121.50/month

Scenario 3: Archive (cold storage)
- 1,000 writes/month (Class A)
- 100 reads/month (Class B)

Class A: 1,000 / 1,000 × $0.050 = $0.05/month (Archive pricing)
Class B: 100 / 1,000 × $0.050 = $0.005/month
Total Operations: $0.055/month
```

### Operation Cost Optimization

1. **Batch operations**: Use batch APIs when available
2. **Reduce metadata reads**: Cache metadata locally
3. **Use hierarchical namespace**: Can reduce costs for certain workloads (though adds 30% premium)
4. **Avoid unnecessary list operations**: Prefix-based queries are cheaper than full bucket lists
5. **Minimize IAM changes**: IAM updates are Class A operations

---

## Network & Egress Costs

### Egress Pricing Tiers (Worldwide)

| Monthly Egress | $/GB |
|----------------|------|
| 0-10 TiB | $0.12 |
| 10-150 TiB | $0.11 |
| >150 TiB | $0.08 |

### Egress by Destination

| Destination | $/GB |
|-------------|------|
| **Internet (Worldwide)** | $0.12 → $0.08 (tiered) |
| **Internet (China)** | $0.23 → $0.20 |
| **Internet (Australia)** | $0.19 → $0.15 |
| **Same region** | FREE |
| **Same multi-region** | FREE |
| **Cross-region (Google Cloud)** | $0.02 → $0.14 |
| **Cloud CDN cache fill** | $0.01 (waives standard egress) |

### Egress Cost Examples

```
Scenario 1: API serving 100 GB/day to users
- 100 GB/day × 30 days = 3,000 GB/month = ~3 TiB
- 3 TiB × $0.12/GB = $360/month
- Annual: $4,320

Scenario 2: ML training data egress to another region
- 50 TB one-time transfer
- 50,000 GB × $0.02/GB (cross-region) = $1,000 one-time

Scenario 3: CDN-optimized website
- 10 TB/month egress, 95% CDN hit rate
- Direct egress: 10 TB × $0.12/GB = $1,200/month
- With CDN: 0.5 TB × $0.12/GB + cache fill fees = ~$100/month
- Savings: $1,100/month (92% reduction!)
```

### Egress Optimization

1. **Use Cloud CDN**: For frequently accessed content
2. **Colocate services**: Keep compute and storage in same region
3. **Compress data**: Reduce egress volume with gzip
4. **Use premium tier networking**: For consistent high-volume egress
5. **Leverage Google's global network**: Peering reduces costs
6. **Cache aggressively**: Reduce origin fetches

---

## Retrieval Fees

Retrieval fees apply when reading data from cold storage classes:

| Storage Class | Retrieval Fee ($/GB) |
|---------------|---------------------|
| Standard | FREE |
| Nearline | $0.01 |
| Coldline | $0.02 |
| Archive | $0.05 |

### Retrieval Cost Examples

```
Reading 1 TB from each storage class:

Standard: 1,024 GB × $0.00 = $0.00
Nearline: 1,024 GB × $0.01 = $10.24
Coldline: 1,024 GB × $0.02 = $20.48
Archive: 1,024 GB × $0.05 = $51.20
```

### Avoiding Retrieval Fees

1. **Use Autoclass**: Automatically avoids fees during transitions
2. **Predict access patterns**: Keep frequently accessed data in Standard
3. **Monitor access frequency**: Move data based on actual usage
4. **Use lifecycle rules**: Automate transitions based on age

---

## Early Deletion Fees

Early deletion fees apply when objects are deleted before meeting minimum storage durations:

| Storage Class | Min Duration | Early Deletion Charge |
|---------------|--------------|----------------------|
| Standard | None | None |
| Nearline | 30 days | Charged as if stored for 30 days |
| Coldline | 90 days | Charged as if stored for 90 days |
| Archive | 365 days | Charged as if stored for 365 days |

### Early Deletion Calculation

```
Example: Delete Nearline object after 10 days
- Stored: 100 GB for 10 days
- Minimum: 30 days
- Missing: 20 days
- Charge: 100 GB × (20/30) × $0.010 = $0.67

Example: Delete Archive object after 100 days
- Stored: 500 GB for 100 days
- Minimum: 365 days
- Missing: 265 days
- Charge: 500 GB × (265/365) × $0.0012 = $0.44
```

### Avoiding Early Deletion Fees

1. **Use Object Lifecycle Management**: Automatic transitions don't incur early deletion
2. **Use Autoclass**: Transitions via Autoclass are exempt
3. **Plan deletions**: Wait until minimum duration is met
4. **Soft delete**: Objects in soft delete retention don't incur early deletion

---

## Cost Optimization Strategies

### Strategy 1: Storage Class Right-Sizing

```
Audit current storage:
1. List objects by last access date
2. Calculate access frequency
3. Match to appropriate storage class

Access Pattern → Storage Class:
- Daily/Weekly → Standard
- Monthly → Nearline
- Quarterly → Coldline
- Yearly → Archive
- Unknown → Autoclass
```

### Strategy 2: Lifecycle Rule Optimization

```hcl
# Cost-optimized lifecycle rules
lifecycle_rule {
  action {
    type          = "SetStorageClass"
    storage_class = "NEARLINE"
  }
  condition {
    age = 30
  }
}

lifecycle_rule {
  action {
    type          = "SetStorageClass"
    storage_class = "COLDLINE"
  }
  condition {
    age = 90
  }
}

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
    age = 730  # 2 years
  }
}
```

### Strategy 3: Versioning Cost Management

```
Versioning can multiply storage costs:
- Object updated daily for 30 days = 30 versions
- 100 GB object = 3 TB stored (30 × 100 GB)
- Cost: 3 TB × $0.020 = $60/month vs $2/month without versioning

Mitigation:
1. Limit number of versions via lifecycle
2. Delete old versions automatically
3. Use soft delete instead for simple recovery
```

```hcl
# Limit version count
lifecycle_rule {
  action {
    type = "Delete"
  }
  condition {
    num_newer_versions = 5
    with_state         = "NONCURRENT"
  }
}
```

### Strategy 4: Data Compression

```
Compress before upload:
- Text data: 70-90% reduction
- Cost savings: 70-90% on storage + egress

Example: 1 TB JSON logs
- Uncompressed: 1,024 GB × $0.020 = $20.48/month
- Compressed (80%): 205 GB × $0.020 = $4.10/month
- Savings: $16.38/month ($196.56/year)
```

### Strategy 5: Clean Up Unused Resources

```bash
#!/bin/bash
# Find buckets with no recent access
for bucket in $(gsutil ls); do
    last_modified=$(gsutil ls -l $bucket | tail -1 | awk '{print $1}')
    echo "$bucket - Last modified: $last_modified"
done

# Find large objects that could be transitioned
gsutil ls -lr gs://my-bucket/** | sort -n -k2 | tail -20
```

---

## Autoclass Economics

### How Autoclass Saves Money

Autoclass automatically transitions objects based on access patterns:
- **No manual lifecycle rules needed**
- **Avoids retrieval fees during transitions**
- **Adapts to changing access patterns**

### Autoclass vs Manual Lifecycle

| Factor | Autoclass | Manual Lifecycle |
|--------|-----------|------------------|
| **Setup** | One click | Custom rules |
| **Adaptability** | Dynamic | Static |
| **Retrieval Fees** | Waived during transitions | Apply |
| **Early Deletion** | Waived | Apply if not careful |
| **Cost Predictability** | Variable | Predictable |
| **Best For** | Unpredictable access | Predictable access |

### Enabling Autoclass

```bash
gcloud storage buckets update gs://my-bucket --enable-autoclass
```

```hcl
resource "google_storage_bucket" "with_autoclass" {
  name     = "my-bucket"
  location = "US-CENTRAL1"
  
  autoclass {
    enabled = true
  }
}
```

---

## CDN Integration Savings

### Cloud CDN Cost Benefits

| Scenario | Direct GCS | With Cloud CDN | Savings |
|----------|------------|----------------|---------|
| 10 TB/month, 90% hit rate | $1,200 | $120 | 90% |
| 50 TB/month, 95% hit rate | $5,500 | $275 | 95% |
| 100 TB/month, 99% hit rate | $8,000 | $80 | 99% |

### CDN Configuration

```bash
# Create backend bucket
gcloud compute backend-buckets create my-backend \
  --gcs-bucket-name=my-public-bucket \
  --enable-cdn

# Set cache TTL
gcloud compute backend-buckets update my-backend \
  --cdn-policy-cache-mode=CACHE_ALL_STATIC \
  --cdn-policy-ttl=3600
```

---

## Cost Monitoring

### Cloud Monitoring Metrics

| Metric | Description | Use |
|--------|-------------|-----|
| `storage.googleapis.com/storage/total_bytes` | Total stored bytes | Track growth |
| `storage.googleapis.com/storage/object_count` | Object count | Monitor scale |
| `storage.googleapis.com/api/request_count` | Request count | Track operations |
| `storage.googleapis.com/api/bytes_sent` | Egress bytes | Monitor egress costs |

### Cost Dashboard

Create a Cloud Monitoring dashboard with:
1. Storage growth over time
2. Operation count by class
3. Egress volume trend
4. Cost by bucket (via billing export)

### BigQuery Billing Export

```sql
-- Query GCS costs from billing export
SELECT
  DATE(usage_start_time) as date,
  resource.global_resource_name as bucket,
  SUM(cost) as total_cost,
  SUM(usage.amount) as usage_amount,
  usage.unit as usage_unit
FROM `my-project.billing_export.gcp_billing_export_v1_*`
WHERE service.description = 'Cloud Storage'
GROUP BY 1, 2, 5
ORDER BY 1 DESC, 3 DESC
LIMIT 100
```

---

## Budget Alerts

### Create Budget Alert

```bash
gcloud billing budgets create \
  --display-name="GCS Monthly Budget" \
  --billing-account=000000-000000-000000 \
  --budget-amount=1000 \
  --budget-threshold-percent=0.5,0.75,1.0 \
  --services=storage.googleapis.com \
  --notification-emails=team@example.com
```

### Terraform Budget Alert

```hcl
resource "google_billing_budget" "gcs_budget" {
  billing_account = var.billing_account
  display_name    = "GCS Monthly Budget"
  
  amount {
    specified_amount {
      units = "1000"  # $1,000/month
    }
  }
  
  threshold_rules {
    threshold_percent = 0.5
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 0.75
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "CURRENT_SPEND"
  }
}
```

---

## Cost Allocation & Tagging

### Label Strategy

```hcl
labels = {
  environment   = "production"
  application   = "payments"
  team          = "transactions"
  cost-center   = "eng-123"
  data-classification = "confidential"
  retention     = "1-year"
}
```

### Cost Report by Labels

```sql
-- Cost breakdown by environment
SELECT
  labels['environment'] as environment,
  labels['application'] as application,
  SUM(cost) as total_cost
FROM `my-project.billing_export.gcp_billing_export_v1_*`
WHERE service.description = 'Cloud Storage'
GROUP BY 1, 2
ORDER BY 3 DESC
```

---

## Common Cost Pitfalls

### 1. Uncontrolled Versioning

```
Problem: Objects updated frequently with versioning enabled
Impact: 10-100x storage cost increase
Fix: Limit versions via lifecycle rules
```

### 2. Forgotten Test Buckets

```
Problem: Development buckets left running
Impact: Ongoing storage costs for unused data
Fix: Lifecycle rules to auto-delete dev buckets
```

### 3. Cross-Region Egress

```
Problem: Compute in us-east1, storage in us-central1
Impact: $0.02/GB cross-region egress
Fix: Colocate compute and storage
```

### 4. No Lifecycle Rules

```
Problem: Data grows forever
Impact: Linearly increasing storage costs
Fix: Implement lifecycle rules immediately
```

### 5. Over-provisioned Storage Class

```
Problem: Archive data in Standard storage
Impact: 16x higher cost than necessary
Fix: Transition to appropriate storage class
```

---

## Cost Optimization Checklist

### Monthly
- [ ] Review storage growth trend
- [ ] Check egress costs by bucket
- [ ] Audit versioning overhead
- [ ] Identify buckets with no recent access
- [ ] Review operation costs

### Quarterly
- [ ] Evaluate Autoclass candidates
- [ ] Review lifecycle rule effectiveness
- [ ] Clean up unused buckets
- [ ] Assess CDN hit rates
- [ ] Review budget vs actual

### Annually
- [ ] Full cost allocation review
- [ ] Storage class optimization
- [ ] Archive old data
- [ ] Review retention requirements
- [ ] Negotiate committed use discounts (if applicable)

---

*"Storage is cheap until it isn't. Optimize early, monitor constantly, and automate lifecycle management."* — FinOps Engineer Mantra
