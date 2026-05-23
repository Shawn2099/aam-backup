# Monitoring & Operations - Google Cloud Storage

**Level**: Intermediate to Expert  
**Prerequisites**: All previous documents  
**Time to Master**: 2-3 weeks of operational experience

---

## Table of Contents

1. [Cloud Monitoring Integration](#cloud-monitoring-integration)
2. [Key Metrics](#key-metrics)
3. [Alert Policies](#alert-policies)
4. **Audit Logging**
5. [Dashboards](#dashboards)
6. [SLO/SLI Definition](#slosli-definition)
7. [Incident Response](#incident-response)
8. [Operational Runbooks](#operational-runbooks)
9. [Backup & DR Procedures](#backup--dr-procedures)
10. [Capacity Planning](#capacity-planning)
11. [Usage Reporting](#usage-reporting)
12. [Log Analysis](#log-analysis)

---

## Cloud Monitoring Integration

GCS automatically exports metrics to Cloud Monitoring. No configuration needed.

### Available Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| `storage.googleapis.com/storage/total_bytes` | Gauge | Bytes | Total bytes stored |
| `storage.googleapis.com/storage/object_count` | Gauge | Count | Number of objects |
| `storage.googleapis.com/storage/bucket_count` | Gauge | Count | Number of buckets |
| `storage.googleapis.com/api/request_count` | Delta | Count | API request count |
| `storage.googleapis.com/api/request_latencies` | Delta | Milliseconds | Request latency |
| `storage.googleapis.com/api/bytes_sent` | Delta | Bytes | Bytes sent (egress) |
| `storage.googleapis.com/api/bytes_received` | Delta | Bytes | Bytes received (ingress) |

### Metric Labels

All metrics include these labels:
- `resource_type`: Type of resource (gcs_bucket)
- `project_id`: GCP project ID
- `location`: Bucket location
- `storage_class`: Storage class (Standard, Nearline, etc.)

---

## Key Metrics

### Storage Metrics

```
Total Bytes Stored:
- Track growth rate
- Set alerts on unexpected growth
- Project future costs

Object Count:
- Monitor for sudden drops (deletions)
- Track application scaling
```

### Request Metrics

```
Request Count by Method:
- storage.objects.get (reads)
- storage.objects.create (writes)
- storage.objects.delete (deletions)
- storage.objects.list (listings)

Request Latency:
- P50 (median)
- P95 (tail)
- P99 (worst case)
```

### Network Metrics

```
Bytes Sent:
- Monitor egress costs
- Detect unusual data transfers
- Track CDN offload

Bytes Received:
- Monitor ingestion rates
- Detect upload spikes
```

---

## Alert Policies

### Critical Alerts

#### 1. High Error Rate

```json
{
  "displayName": "GCS High Error Rate",
  "conditions": [
    {
      "conditionThreshold": {
        "filter": "metric.type=\"storage.googleapis.com/api/request_count\" AND resource.type=\"gcs_bucket\" AND metric.label=\"error\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 100,
        "duration": "300s",
        "trigger": {"count": 1}
      }
    }
  ],
  "alertStrategy": {
    "autoClose": "3600s"
  }
}
```

#### 2. Storage Growth Spike

```json
{
  "displayName": "GCS Unexpected Storage Growth",
  "conditions": [
    {
      "conditionThreshold": {
        "filter": "metric.type=\"storage.googleapis.com/storage/total_bytes\" AND resource.type=\"gcs_bucket\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 1099511627776,  // 1 TB
        "duration": "3600s"
      }
    }
  ]
}
```

#### 3. High Egress Volume

```json
{
  "displayName": "GCS High Egress Volume",
  "conditions": [
    {
      "conditionThreshold": {
        "filter": "metric.type=\"storage.googleapis.com/api/bytes_sent\" AND resource.type=\"gcs_bucket\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 1099511627776,  // 1 TB per day
        "duration": "86400s"
      }
    }
  ]
}
```

### Terraform Alert Policies

```hcl
resource "google_monitoring_alert_policy" "gcs_error_rate" {
  display_name = "GCS High Error Rate"
  
  conditions {
    display_name = "Request errors > 100 in 5 minutes"
    
    condition_threshold {
      filter     = "metric.type=\"storage.googleapis.com/api/request_count\" AND resource.type=\"gcs_bucket\" AND metric.label=\"error\""
      comparison = "COMPARISON_GT"
      threshold_value = 100
      duration   = "300s"
      
      trigger {
        count = 1
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email.id
  ]
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "Platform Team Email"
  type         = "email"
  
  labels = {
    email_address = "platform-team@example.com"
  }
}
```

---

## Audit Logging

### Log Types

| Log Type | Captures | Enabled By Default |
|----------|----------|-------------------|
| **Admin Activity** | Bucket creation, deletion, IAM changes | ✅ Yes |
| **Data Access** | Object reads, writes, metadata | ❌ No (must enable) |

### Enable Data Access Logs

```bash
gcloud projects update-iam-policy my-project \
  --add-binding \
  --member="allAuthenticatedUsers" \
  --role="roles/logging.admin"
```

### Query Audit Logs

```bash
# Bucket IAM changes
gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.methodName:storage.setIamPolicy" \
  --limit=10

# Object deletions
gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.methodName:storage.objects.delete" \
  --limit=50

# Public access attempts
gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.authenticationInfo.principalEmail=allUsers" \
  --limit=10
```

### Export Logs to BigQuery

```bash
gcloud logging sinks create gcs-audit-sink \
  bigquery.googleapis.com/projects/my-project/datasets/audit_logs \
  --log-filter="resource.type=gcs_bucket"
```

---

## SLO/SLI Definition

### Service Level Indicators (SLIs)

| SLI | Target | Measurement |
|-----|--------|-------------|
| **Availability** | 99.99% | Successful requests / Total requests |
| **Latency (P50)** | < 100ms | Median request duration |
| **Latency (P99)** | < 500ms | 99th percentile duration |
| **Durability** | 99.999999999% | Annual object survival rate |

### Error Budget

```
Error Budget = 1 - SLO

For 99.99% availability:
- Error Budget = 0.01% = 4.32 minutes/month
- Can be unavailable for 4.32 minutes/month
```

---

## Incident Response

### Common Incidents

| Incident | Severity | Response Time | Resolution Time |
|----------|----------|---------------|-----------------|
| **Bucket unavailable** | Critical | 5 minutes | 30 minutes |
| **High error rate** | High | 15 minutes | 1 hour |
| **Data breach** | Critical | 5 minutes | 4 hours |
| **Performance degradation** | Medium | 30 minutes | 2 hours |
| **Cost spike** | Low | 4 hours | 1 day |

### Incident Response Checklist

#### Data Breach Response

1. **Contain**: Remove public access immediately
2. **Assess**: Identify exposed objects via audit logs
3. **Notify**: Inform security team and affected users
4. **Remediate**: Fix IAM policy, enable prevention
5. **Document**: Create incident report
6. **Review**: Update security controls

#### Performance Incident

1. **Identify**: Check Cloud Monitoring dashboards
2. **Isolate**: Determine if bucket-wide or prefix-specific
3. **Mitigate**: Enable parallelism, check for hotspots
4. **Resolve**: Implement fix, monitor recovery
5. **Post-mortem**: Document root cause and prevention

---

## Operational Runbooks

### Runbook 1: Add New Bucket

```
1. Create Terraform configuration
2. Review security settings (uniform access, public prevention)
3. Configure IAM bindings
4. Set lifecycle rules
5. Apply via CI/CD pipeline
6. Verify in Cloud Console
7. Update documentation
8. Notify stakeholders
```

### Runbook 2: Investigate High Costs

```
1. Check billing export in BigQuery
2. Identify top cost buckets
3. Review storage growth
4. Check egress volume
5. Review operation count
6. Identify optimization opportunities
7. Implement fixes
8. Monitor impact
```

### Runbook 3: Restore Deleted Objects

```
1. Check if versioning is enabled
2. List object versions: gsutil ls -a gs://bucket/object
3. Restore version: gsutil cp gs://bucket/object#generation gs://bucket/object
4. If soft delete enabled: Check for soft-deleted versions
5. Verify restored object
6. Investigate deletion cause
7. Update lifecycle rules if needed
```

---

## Backup & DR Procedures

### Backup Strategy

| Data Type | Backup Frequency | Retention | Storage Class |
|-----------|------------------|-----------|---------------|
| **Database dumps** | Daily | 30 days | Nearline |
| **Application configs** | On change | 90 days | Standard |
| **User uploads** | Real-time (versioning) | 365 days | Autoclass |
| **Logs** | Continuous | 7 years (compliance) | Coldline → Archive |

### Disaster Recovery

#### RTO/RPO Targets

| Scenario | RTO | RPO | Strategy |
|----------|-----|-----|----------|
| **Bucket deletion** | 1 hour | 0 (versioning) | Versioning + soft delete |
| **Region outage** | 4 hours | < 1 minute | Dual-region bucket |
| **Data corruption** | 2 hours | Last good version | Versioning + event-based hold |
| **Ransomware** | 8 hours | Last clean version | Versioning + immutable backups |

#### DR Runbook

```
1. Assess impact (what data is affected?)
2. Determine recovery point (which version/timestamp?)
3. Restore from versioning or backups
4. Verify data integrity
5. Update IAM if breach-related
6. Monitor for recurrence
7. Document incident
8. Update DR procedures
```

---

## Capacity Planning

### Growth Projections

```sql
-- Project storage growth
SELECT
  DATE(timestamp) as date,
  MAX(value) as bytes_stored
FROM `my-project.monitoring.metrics`
WHERE metric_type = 'storage.googleapis.com/storage/total_bytes'
GROUP BY 1
ORDER BY 1
```

### Planning Triggers

| Metric | Current | 3-Month Target | 12-Month Target | Action Threshold |
|--------|---------|----------------|-----------------|------------------|
| Storage (TB) | 10 | 15 | 50 | Review lifecycle at 25 TB |
| Requests/day | 1M | 2M | 10M | Review patterns at 5M |
| Egress/day (GB) | 100 | 200 | 1000 | Enable CDN at 500 GB |
| Cost/month ($) | 500 | 750 | 2000 | Audit at $1500 |

---

## Usage Reporting

### Monthly Report Template

```
GCS Monthly Report - April 2026

Storage:
- Total stored: 15.2 TB (+8% from last month)
- Object count: 2.3M (+5%)
- Top bucket: my-app-data (8.5 TB)

Operations:
- Total requests: 45M (-2%)
- Class A (writes): 5M
- Class B (reads): 40M
- Error rate: 0.01% (target: <0.1%)

Network:
- Egress: 3.2 TB (+15%)
- Ingress: 1.8 TB (+5%)
- CDN hit rate: 92%

Costs:
- Total: $850 (+12%)
- Storage: $320 (38%)
- Operations: $45 (5%)
- Egress: $384 (45%)
- Other: $101 (12%)

Issues:
- 1 incident (high error rate, resolved in 45 min)
- Cost spike due to increased egress (investigating)

Action Items:
- Enable CDN for high-egress bucket
- Review lifecycle rules for old data
- Set up cost anomaly detection
```

---

## Log Analysis

### Common Queries

```bash
# Failed requests
gcloud logging read \
  "resource.type=gcs_bucket AND severity>=ERROR" \
  --limit=50

# IAM policy changes
gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.methodName:storage.setIamPolicy" \
  --limit=20

# Bucket creation/deletion
gcloud logging read \
  "resource.type=gcs_bucket AND (protoPayload.methodName:storage.buckets.create OR protoPayload.methodName:storage.buckets.delete)" \
  --limit=20

# Public access attempts
gcloud logging read \
  "resource.type=gcs_bucket AND protoPayload.authenticationInfo.principalEmail=allUsers" \
  --limit=10
```

### BigQuery Analysis

```sql
-- Top 10 most expensive buckets
SELECT
  resource.labels.bucket_name,
  SUM(cost) as total_cost
FROM `my-project.billing_export.gcp_billing_export_v1_*`
WHERE service.description = 'Cloud Storage'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10

-- Daily egress trend
SELECT
  DATE(usage_start_time) as date,
  SUM(usage.amount) as egress_gb
FROM `my-project.billing_export.gcp_billing_export_v1_*`
WHERE service.description = 'Cloud Storage'
  AND sku.description LIKE '%Egress%'
GROUP BY 1
ORDER BY 1 DESC
LIMIT 30
```

---

*"Monitor everything, alert on what matters, and always have a runbook ready."* — SRE Mantra
