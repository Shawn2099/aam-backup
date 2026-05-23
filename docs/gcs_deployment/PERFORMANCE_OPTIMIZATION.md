# Performance Optimization - Google Cloud Storage

**Level**: Intermediate to Expert  
**Prerequisites**: [Bucket Configuration](./BUCKET_CONFIGURATION.md), [IAM & Security](./IAM_AND_SECURITY.md)  
**Time to Master**: 2-3 weeks of hands-on benchmarking

---

## Table of Contents

1. [Performance Fundamentals](#performance-fundamentals)
2. [Throughput Optimization](#throughput-optimization)
3. [Latency Optimization](#latency-optimization)
4. [Parallel Operations](#parallel-operations)
5. [Object Naming & Hotspot Avoidance](#object-naming--hotspot-avoidance)
6. [Client-Side Optimization](#client-side-optimization)
7. [gRPC API](#grpc-api)
8. [Resumable & Multipart Uploads](#resumable--multipart-uploads)
9. [Composite Objects](#composite-objects)
10. [Caching Strategies](#caching-strategies)
11. [Connection Pooling & Retries](#connection-pooling--retries)
12. [Hedged Requests](#hedged-requests)
13. [Compression](#compression)
14. [Performance Benchmarks](#performance-benchmarks)
15. [Performance Monitoring](#performance-monitoring)
16. [Troubleshooting Performance](#troubleshooting-performance)

---

## Performance Fundamentals

### GCS Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Per-object throughput** | Up to 2.5 Gbps | Single stream limit |
| **Bucket request rate** | 5,000+ queries/second | Per prefix |
| **Read availability** | 99.99% (Standard) | SLA-backed |
| **Durability** | 99.999999999% (11 9's) | Annual |
| **First byte latency** | 50-150ms (Standard) | P50, within region |
| **Upload throughput** | Limited by client network | Can saturate 10 Gbps+ with parallelism |

### Key Performance Principles

1. **GCS scales automatically**: No manual provisioning needed
2. **Parallelism is key**: Single connections are slow, parallel streams are fast
3. **Location matters**: Latency increases ~7ms per 1,000 km
4. **Object size affects performance**: Larger objects benefit from parallelism
5. **Naming affects distribution**: Sequential names cause hotspots

---

## Throughput Optimization

### Single-Stream vs Multi-Stream

```
Single Stream (slow):
┌────────────────────────────────────┐
│ Client ─────── 50 Mbps ──────> GCS │
└────────────────────────────────────┘

Multi-Stream (fast):
┌──────────────────────────────────────┐
│ Client ──┬── 200 Mbps ──┐           │
│          ├── 200 Mbps ──┤           │
│          ├── 200 Mbps ──┤──> 2 Gbps │
│          └── 200 Mbps ──┘           │
└──────────────────────────────────────┘
```

### Optimal Chunk Sizes

| Object Size | Strategy | Chunk Size | Parallel Streams |
|-------------|----------|------------|------------------|
| < 1 MB | Single upload | N/A | 1 |
| 1-10 MB | Single upload | N/A | 1 |
| 10-100 MB | Parallel upload | 8 MB | 4-8 |
| 100 MB - 1 GB | Parallel upload | 32 MB | 8-16 |
| 1-10 GB | Parallel upload | 64 MB | 16-32 |
| > 10 GB | Parallel upload | 128 MB | 32-64 |

### gsutil Parallel Transfer Tuning

```bash
# Basic parallel upload
gsutil -m cp -r large-dir gs://my-bucket/

# Tuned parallel upload (100 threads)
gsutil -o GSUtil:parallel_process_count=1 \
       -o GSUtil:thread_count=100 \
       -m cp -r large-dir gs://my-bucket/

# Optimal for high-bandwidth connections
gsutil -o GSUtil:parallel_process_count=1 \
       -o GSUtil:thread_count=200 \
       -o GSUtil:composite_upload_threshold=1M \
       -m cp large-file.tar.gz gs://my-bucket/
```

### Python: Parallel Upload

```python
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor
import os

def upload_directory_parallel(local_dir, bucket_name, prefix="", max_workers=32):
    """Upload a directory to GCS in parallel."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    def upload_file(file_path):
        blob_name = os.path.relpath(file_path, local_dir)
        if prefix:
            blob_name = f"{prefix}/{blob_name}"
        
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return blob_name
    
    files = []
    for root, _, filenames in os.walk(local_dir):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    
    uploaded = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(upload_file, f) for f in files]
        for future in futures:
            uploaded.append(future.result())
    
    print(f"Uploaded {len(uploaded)} files")
    return uploaded

# Usage
upload_directory_parallel(
    "/path/to/large-directory",
    "my-bucket",
    prefix="uploads/2026-04-11",
    max_workers=32
)
```

### Python: Parallel Download

```python
def download_directory_parallel(bucket_name, prefix, local_dir, max_workers=32):
    """Download objects from GCS in parallel."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    
    def download_blob(blob):
        local_path = os.path.join(local_dir, blob.name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        return blob.name
    
    downloaded = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_blob, b) for b in blobs]
        for future in futures:
            downloaded.append(future.result())
    
    print(f"Downloaded {len(downloaded)} files")
    return downloaded
```

---

## Latency Optimization

### First-Byte Latency Factors

| Factor | Impact | Optimization |
|--------|--------|--------------|
| **Distance** | +7ms per 1,000 km | Colocate compute & storage |
| **Object size** | Minimal for metadata | Use smaller objects for metadata |
| **Request rate** | Degrades at hotspot | Use diverse prefixes |
| **Connection reuse** | Saves 50-100ms | Use connection pooling |
| **DNS resolution** | 10-50ms first request | Cache DNS results |
| **TLS handshake** | 20-100ms | Reuse connections |

### Latency Optimization Techniques

#### 1. Use HTTP/2

```python
from google.cloud import storage
from google.api_core import client_options

# HTTP/2 is enabled by default in recent client versions
client = storage.Client()
```

#### 2. Set Appropriate Timeouts

```python
from google.cloud import storage
from google.api_core import retry

client = storage.Client()
bucket = client.bucket("my-bucket")
blob = bucket.blob("data.json")

# Aggressive timeout for latency-sensitive apps
blob.download_as_bytes(
    retry=retry.Retry(
        initial=0.1,  # 100ms initial backoff
        maximum=2.0,  # 2s max backoff
        multiplier=2.0,
        deadline=5.0  # 5s total deadline
    )
)
```

#### 3. Use Small Objects for Metadata

```
❌ Bad: 10 MB JSON file for config (slow reads)
✅ Good: 10 KB JSON file (fast reads)

Separate data by access pattern:
- config.json (small, read frequently)
- data-2026-04-11.parquet (large, read occasionally)
```

---

## Object Naming & Hotspot Avoidance

### The Hotspot Problem

GCS distributes load across servers based on object name prefixes. Sequential names overload specific servers:

```
❌ BAD: Sequential naming
logs/app-000001.log  → Server A (overloaded!)
logs/app-000002.log  → Server A (overloaded!)
logs/app-000003.log  → Server A (overloaded!)

✅ GOOD: Hash prefix distributes load
logs/a1/app-000001.log  → Server A
logs/b3/app-000002.log  → Server B
logs/c7/app-000003.log  → Server C
```

### Hash Prefix Strategy

```python
import hashlib

def get_hash_prefix(name, num_prefixes=256):
    """Generate a hash prefix for distributing load."""
    hash_val = int(hashlib.md5(name.encode()).hexdigest(), 16)
    return f"{hash_val % num_prefixes:03x}"

def create_distributed_name(base_name):
    """Create a load-distributed object name."""
    prefix = get_hash_prefix(base_name)
    return f"data/{prefix}/{base_name}"

# Usage
print(create_distributed_name("sensor-reading-001.json"))
# Output: data/a3f/sensor-reading-001.json
```

### Time-Based Distribution

For most workloads, time-based naming is sufficient:

```
✅ Good: Time-based
logs/2026/04/11/14/30/app.log    ← Natural distribution
uploads/2026-04-11/user123.jpg   ← Natural distribution
metrics/2026/04/11/cpu.json      ← Natural distribution

❌ Avoid: Sequential within same prefix
events/000001.json
events/000002.json
events/000003.json
```

### Prefix Request Rate Limits

| Prefix Pattern | Max Request Rate |
|----------------|------------------|
| Single prefix | ~5,000 QPS |
| 10 diverse prefixes | ~50,000 QPS |
| 100 diverse prefixes | ~500,000 QPS |
| 1,000+ diverse prefixes | Millions QPS |

---

## Client-Side Optimization

### Python Client Optimization

```python
from google.cloud import storage
from google.api_core import retry, client_info
import http.client

# Configure client with custom timeout and retry
client = storage.Client(
    client_info=client_info.ClientInfo(
        user_agent="my-app/1.0 (optimized)"
    )
)

# Configure retry policy
retry_policy = retry.Retry(
    predicate=retry.if_transient_error,
    initial=1.0,
    maximum=60.0,
    multiplier=2.0,
    deadline=600.0,  # 10 minutes
)

# Upload with retry
blob = bucket.blob("large-file.bin")
blob.upload_from_filename(
    "large-file.bin",
    retry=retry_policy,
    timeout=300  # 5 minutes
)

# Download with retry
content = blob.download_as_bytes(retry=retry_policy)
```

### Node.js Client Optimization

```javascript
const {Storage} = require('@google-cloud/storage');

const storage = new Storage({
  retryOptions: {
    autoRetry: true,
    retryDelayMultiplier: 2,
    totalTimeout: 600,  // 10 minutes
    maxRetryDelay: 60,
    maxRetries: 10,
  },
  timeout: 30000,  // 30 seconds per request
});

// Upload with options
async function uploadOptimized(bucketName, fileName, filePath) {
  await storage.bucket(bucketName).upload(filePath, {
    gzip: true,  // Enable compression
    resumable: true,  // Enable resumable uploads
    validation: 'md5',  // Verify integrity
    timeout: 300000,  // 5 minutes
  });
}
```

### Connection Reuse

```python
# HTTP connection pooling (automatic in recent versions)
# The storage client maintains a connection pool

from google.cloud import storage
import google.auth.transport.requests

# Use session for connection reuse
session = google.auth.transport.requests.AuthorizedSession(
    google.auth.default()[0]
)

# Session maintains connection pool automatically
```

---

## gRPC API

### Why gRPC?

GCS now supports gRPC for improved performance:

| Feature | JSON API | gRPC API |
|---------|----------|----------|
| **Protocol** | HTTP/1.1 or HTTP/2 | HTTP/2 (multiplexed) |
| **Serialization** | JSON (text) | Protobuf (binary) |
| **Latency** | Higher | 10-30% lower |
| **Throughput** | Good | 20-50% higher |
| **Streaming** | Limited | Full bidirectional |

### Enable gRPC (Python)

```bash
# Install gRPC support
pip install google-cloud-storage[grpc]
```

```python
from google.cloud import storage

# Enable gRPC transport
client = storage.Client(
    transport="grpc"  # Use gRPC instead of REST
)

# All operations work the same, but faster
bucket = client.bucket("my-bucket")
blob = bucket.blob("data.bin")
blob.upload_from_filename("data.bin")  # Uses gRPC
```

### gRPC Limitations

- Not all GCS features available via gRPC yet
- Signed URLs still use REST
- Some legacy APIs not supported
- Requires additional dependencies

---

## Resumable & Multipart Uploads

### Resumable Uploads (Recommended)

Resumable uploads survive network interruptions:

```python
from google.cloud import storage

def upload_resumable(bucket_name, source_file, destination_blob):
    """Upload a file using resumable upload."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    
    # Start resumable upload
    blob.chunk_size = 5 * 1024 * 1024  # 5 MB chunks
    
    with open(source_file, "rb") as f:
        blob.upload_from_file(f)
    
    print(f"Resumable upload complete: {destination_blob}")

# For large files
upload_resumable("my-bucket", "large-file.tar.gz", "archives/large-file.tar.gz")
```

### XML API Multipart Uploads

For parallel upload performance:

```python
import requests
import hashlib

def multipart_upload(bucket_name, object_name, file_path, chunk_size=64*1024*1024):
    """Upload using multipart/parallel strategy."""
    # Read file in chunks
    chunks = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    
    # Upload chunks in parallel (use ThreadPoolExecutor in production)
    etags = []
    for i, chunk in enumerate(chunks):
        # Upload each chunk (simplified - use proper multipart API)
        blob_name = f"{object_name}.part{i+1}"
        blob = storage.Client().bucket(bucket_name).blob(blob_name)
        blob.upload_from_string(chunk)
        etags.append(blob.etag)
    
    # Compose chunks into final object
    compose_chunks = [
        storage.Client().bucket(bucket_name).blob(f"{object_name}.part{i+1}")
        for i in range(len(chunks))
    ]
    
    final_blob = storage.Client().bucket(bucket_name).blob(object_name)
    final_blob.compose(compose_chunks)
    
    # Clean up chunks
    for chunk_blob in compose_chunks:
        chunk_blob.delete()
    
    print(f"Multipart upload complete: {object_name}")
```

### Resumable Upload Best Practices

1. **Chunk size**: 8-64 MB (larger for high-bandwidth)
2. **Retry on failure**: Resume from last successful chunk
3. **Track upload ID**: Save to resume after process restart
4. **Set timeout**: Prevent indefinite hangs
5. **Monitor progress**: Report % complete for UX

---

## Composite Objects

### What are Composite Objects?

Composite objects combine multiple source objects into one:

```python
from google.cloud import storage

def create_composite_object(bucket_name, destination_name, source_names):
    """Combine multiple objects into one."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Get source blobs
    source_blobs = [bucket.blob(name) for name in source_names]
    
    # Create composite
    destination = bucket.blob(destination_name)
    destination.compose(source_blobs)
    
    print(f"Created composite object: {destination_name}")
    return destination

# Usage: Combine 100 part files
source_files = [f"uploads/part-{i:03d}" for i in range(100)]
create_composite_object("my-bucket", "combined-file.txt", source_files)
```

### Composite Object Limits

| Limit | Value |
|-------|-------|
| Max source components | 32 (single compose) |
| Max total components | 1,024 (with tree composition) |
| Max component size | 5 GB each |
| Component retention | Deleted after composition |

### Tree Composition Pattern

For >32 components:

```
Level 1: Compose 32 parts → 32 intermediate objects
Level 2: Compose 32 intermediates → 1 final object
Total: 1,024 parts in 2 levels
```

```python
def tree_compose(bucket_name, destination_name, source_names, max_components=32):
    """Tree composition for >32 sources."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    current_sources = source_names
    
    while len(current_sources) > 1:
        next_level = []
        
        for i in range(0, len(current_sources), max_components):
            chunk = current_sources[i:i+max_components]
            if len(chunk) == 1:
                next_level.append(chunk[0])
                continue
            
            dest = bucket.blob(f"temp-composite-{i}")
            blobs = [bucket.blob(name) for name in chunk]
            dest.compose(blobs)
            next_level.append(dest.name)
            
            # Clean up sources
            for name in chunk:
                bucket.blob(name).delete()
        
        current_sources = next_level
    
    # Rename final to destination
    bucket.blob(current_sources[0]).copy_to(destination_name)
    bucket.blob(current_sources[0]).delete()
    
    return bucket.blob(destination_name)
```

---

## Caching Strategies

### Cloud CDN Integration

```bash
# Create backend bucket
gcloud compute backend-buckets create my-cdn-backend \
  --gcs-bucket-name=my-bucket

# Create URL map
gcloud compute url-maps create my-cdn-map \
  --default-backend-bucket=my-cdn-backend

# Create target HTTP proxy
gcloud compute target-http-proxies create my-cdn-proxy \
  --url-map=my-cdn-map

# Create global forwarding rule
gcloud compute forwarding-rules create my-cdn-rule \
  --global \
  --target-http-proxy=my-cdn-proxy \
  --address=STATIC_IP \
  --ports=80
```

### Cache-Control Headers

```python
from google.cloud import storage

def set_cache_control(bucket_name, blob_name, max_age=3600):
    """Set Cache-Control header on object."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Reload metadata
    blob.reload()
    
    # Set cache control
    blob.cache_control = f"public, max-age={max_age}"
    blob.patch()
    
    print(f"Set Cache-Control: {blob.cache_control}")

# Usage
set_cache_control("my-bucket", "images/logo.png", max_age=86400)  # 24 hours
set_cache_control("my-bucket", "api/data.json", max_age=300)  # 5 minutes
```

### Cache Invalidation

```bash
# Invalidate specific path
gcloud compute url-maps invalidate-cdn-cache my-cdn-map \
  --path="/images/logo.png"

# Invalidate prefix
gcloud compute url-maps invalidate-cdn-cache my-cdn-map \
  --path="/images/*"

# Invalidate all
gcloud compute url-maps invalidate-cdn-cache my-cdn-map \
  --path="/*"
```

### Cache Best Practices

1. **Set appropriate max-age**: Static assets = long, dynamic = short
2. **Use versioned filenames**: `logo-v2.png` instead of invalidating
3. **Leverage CDN for hot objects**: >100 requests/hour
4. **Monitor cache hit ratio**: Target >90% for static content
5. **Use signed URLs with CDN**: Cache securely with expiration

---

## Connection Pooling & Retries

### Retry Configuration

```python
from google.cloud import storage
from google.api_core import retry

# Default retry policy
default_retry = retry.Retry(
    predicate=retry.if_transient_error,
    initial=1.0,
    maximum=60.0,
    multiplier=2.0,
    deadline=600.0,
)

# Custom retry for specific operations
upload_retry = retry.Retry(
    predicate=retry.if_transient_error,
    initial=2.0,
    maximum=120.0,
    multiplier=2.0,
    deadline=1800.0,  # 30 minutes for large uploads
)

download_retry = retry.Rretry(
    predicate=retry.if_transient_error,
    initial=0.5,
    maximum=30.0,
    multiplier=2.0,
    deadline=120.0,
)

# Apply retry
blob.upload_from_filename("large-file.bin", retry=upload_retry)
content = blob.download_as_bytes(retry=download_retry)
```

### Transient Errors to Retry

```python
from google.api_core import exceptions

def is_transient_error(exc):
    """Determine if exception is retryable."""
    if isinstance(exc, exceptions.TooManyRequests):
        return True
    if isinstance(exc, exceptions.ServiceUnavailable):
        return True
    if isinstance(exc, exceptions.InternalServerError):
        return True
    if isinstance(exc, exceptions.BadGateway):
        return True
    if isinstance(exc, exceptions.GatewayTimeout):
        return True
    if isinstance(exc, ConnectionError):
        return True
    return False
```

---

## Hedged Requests

### What are Hedged Requests?

Hedged requests send **duplicate requests** to reduce tail latency:

```
Normal Request:
Client ──────(200ms)─────> GCS (slow server)

Hedged Request:
Client ──(50ms)──> GCS Server A
       ──(10ms)──> GCS Server B (returns first!)
       ──(cancel)──> GCS Server A
```

### Implementation

```python
import concurrent.futures
import time
from google.cloud import storage

def hedged_read(bucket_name, blob_name, hedging_delay=0.05, max_hedges=2):
    """Read with hedged requests to reduce tail latency."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    def do_read():
        blob = bucket.blob(blob_name)
        return blob.download_as_bytes()
    
    # Send initial request
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        
        # First request
        futures.append(executor.submit(do_read))
        
        # Wait for hedging delay
        time.sleep(hedging_delay)
        
        # Check if first request completed
        done, not_done = concurrent.futures.wait(
            futures, timeout=0, return_when=concurrent.futures.FIRST_COMPLETED
        )
        
        if done:
            return done.pop().result()
        
        # Send hedged requests
        for _ in range(max_hedges):
            futures.append(executor.submit(do_read))
        
        # Return first to complete
        for future in concurrent.futures.as_completed(futures):
            return future.result()

# Usage - critical for latency-sensitive apps
data = hedged_read("my-bucket", "config.json", hedging_delay=0.05)
```

---

## Compression

### Gzip Compression

```python
from google.cloud import storage

def upload_compressed(bucket_name, source_file, destination_blob):
    """Upload with gzip compression."""
    import gzip
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    
    # Compress in memory
    with open(source_file, 'rb') as f:
        content = f.read()
    
    compressed = gzip.compress(content)
    
    # Upload with content encoding
    blob.content_encoding = 'gzip'
    blob.upload_from_string(compressed)
    
    original_size = len(content)
    compressed_size = len(compressed)
    ratio = (1 - compressed_size / original_size) * 100
    
    print(f"Original: {original_size:,} bytes")
    print(f"Compressed: {compressed_size:,} bytes")
    print(f"Reduction: {ratio:.1f}%")

# Usage
upload_compressed("my-bucket", "data.json", "data.json")
```

### gsutil Compression

```bash
# Upload with automatic gzip
gsutil -h "Content-Encoding:gzip" cp data.json gs://my-bucket/

# Compress then upload
gzip -k data.json
gsutil cp data.json.gz gs://my-bucket/data.json
```

### Compression Ratios by Type

| Data Type | Compression Ratio | Recommendation |
|-----------|-------------------|----------------|
| Text (JSON, XML, CSV) | 70-90% | ✅ Always compress |
| Logs | 80-95% | ✅ Always compress |
| Code | 60-80% | ✅ Compress |
| Images (JPEG, PNG) | 0-5% | ❌ Already compressed |
| Video/Audio | 0-2% | ❌ Already compressed |
| Parquet/ORC | 0-5% | ❌ Already compressed |
| ZIP/Tar.gz | 0-2% | ❌ Already compressed |

---

## Performance Benchmarks

### Real-World Benchmarks

#### Single Object Upload

| Object Size | Single Stream | Parallel (32 threads) | Improvement |
|-------------|---------------|-----------------------|-------------|
| 1 MB | 0.2s | 0.2s | None (overhead) |
| 10 MB | 1.5s | 0.8s | 1.9x |
| 100 MB | 12s | 4s | 3x |
| 1 GB | 120s | 35s | 3.4x |
| 10 GB | 1,200s | 300s | 4x |

#### Directory Upload (10,000 x 1 MB files)

| Method | Time | Notes |
|--------|------|-------|
| Sequential `gsutil cp` | ~50 minutes | Very slow |
| `gsutil -m cp` | ~8 minutes | Default parallelism |
| Tuned `gsutil -m` (100 threads) | ~5 minutes | Optimal |
| Python ThreadPoolExecutor (32) | ~6 minutes | Programmatic control |

### Benchmark Script

```python
import time
from google.cloud import storage
import os

def benchmark_upload(bucket_name, file_size_mb, num_files, max_workers=1):
    """Benchmark upload performance."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Create test file
    test_file = "/tmp/test-file.bin"
    with open(test_file, 'wb') as f:
        f.write(os.urandom(file_size_mb * 1024 * 1024))
    
    start = time.time()
    
    from concurrent.futures import ThreadPoolExecutor
    
    def upload_one(i):
        blob = bucket.blob(f"bench/file-{i}.bin")
        blob.upload_from_filename(test_file)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(upload_one, range(num_files)))
    
    elapsed = time.time() - start
    throughput = (file_size_mb * num_files) / elapsed
    
    print(f"Files: {num_files}")
    print(f"Size per file: {file_size_mb} MB")
    print(f"Workers: {max_workers}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Throughput: {throughput:.2f} MB/s")
    
    os.remove(test_file)
    return elapsed, throughput

# Run benchmarks
for workers in [1, 4, 16, 32]:
    benchmark_upload("my-bucket", 10, 10, max_workers=workers)
```

---

## Performance Monitoring

### Cloud Monitoring Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `storage.googleapis.com/api/request_count` | Request rate | Baseline + 50% |
| `storage.googleapis.com/api/request_latencies` | Request latency | P99 > 500ms |
| `storage.googleapis.com/api/bytes_sent` | Egress volume | Budget threshold |
| `storage.googleapis.com/api/bytes_received` | Ingress volume | Unexpected spikes |

### Create Performance Dashboard

```bash
# Create alert policy for high latency
gcloud alpha monitoring policies create \
  --policy-from-file=gcs-latency-alert.yaml
```

```yaml
# gcs-latency-alert.yaml
combiner: OR
conditions:
  - conditionThreshold:
      comparison: COMPARISON_GT
      duration: 300s
      filter: metric.type="storage.googleapis.com/api/request_latencies" AND resource.type="gcs_bucket"
      thresholdValue: 500
      trigger:
        count: 1
    displayName: "GCS High Latency (P99 > 500ms)"
displayName: "GCS Performance Alert"
```

---

## Pagination & Large Bucket Handling

### Paginating List Operations

When buckets have millions of objects, pagination is essential:

```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket("my-large-bucket")

# Basic pagination (automatic in client library)
blobs = bucket.list_blobs(max_results=1000)
for blob in blobs:
    print(blob.name)
# Client library automatically fetches next page

# Manual pagination
blobs = bucket.list_blobs()
pages = blobs.pages

for page in pages:
    print(f"Page with {len(list(page))} objects")
    # Process page
```

### Pagination Parameters

| Parameter | Description | Default | Max |
|-----------|-------------|---------|-----|
| `maxResults` | Objects per page | N/A | No limit |
| `pageToken` | Token for next page | N/A | From previous response |
| `prefix` | Filter by prefix | None | N/A |
| `delimiter` | Group by delimiter | None | Usually "/" |
| `startOffset` | Start after this prefix | None | N/A |
| `endOffset` | End before this prefix | None | N/A |

### Efficient Large Bucket Listing

```python
# Efficient: Use prefix filtering
blobs = bucket.list_blobs(prefix="logs/2026/04/")

# Efficient: Use delimiter for directory-like listing
blobs = bucket.list_blobs(prefix="data/", delimiter="/")
for blob in blobs:
    print(blob.name)  # Only objects at this level
# blobs.prefixes contains "subdirectories"

# Efficient: Use startOffset/endOffset for range queries
blobs = bucket.list_blobs(
    prefix="data/",
    start_offset="data/000",
    end_offset="data/100"
)

# INEFFICIENT: Don't do this on large buckets
all_blobs = list(bucket.list_blobs())  # Loads everything into memory
```

### JSON API Pagination

```bash
# First page
curl "https://storage.googleapis.com/storage/v1/b/my-bucket/o?maxResults=100"

# Next page (use nextPageToken from response)
curl "https://storage.googleapis.com/storage/v1/b/my-bucket/o?maxResults=100&pageToken=NEXT_PAGE_TOKEN"
```

### gsutil Pagination

```bash
# List with limit
gsutil ls -l gs://my-bucket/** | head -1000

# List with prefix filter
gsutil ls gs://my-bucket/logs/2026/04/

# List with recursive and limit
gsutil ls -r gs://my-bucket/** | head -500
```

---

## Rate Limits & Distribution Guidelines

### Explicit Rate Limits

| Operation | Rate Limit | Notes |
|-----------|------------|-------|
| **Object insert/update/delete** | ~5,000 QPS per prefix | Per bucket |
| **Object read (GET)** | ~5,000 QPS per prefix | Per bucket |
| **Bucket list** | ~200 QPS | Per bucket |
| **Bucket get metadata** | ~5,000 QPS | Per bucket |
| **IAM policy operations** | ~5 QPS | Per bucket |
| **Lifecycle rule evaluation** | Automatic | No user limit |

### Prefix Request Rate Scaling

| Prefix Diversity | Max QPS | Example |
|------------------|---------|---------|
| 1 prefix | ~5,000 | `uploads/file.txt` |
| 10 prefixes | ~50,000 | `uploads/0-9/` |
| 100 prefixes | ~500,000 | `uploads/00-99/` |
| 1,000 prefixes | ~5,000,000 | `uploads/000-999/` |
| 10,000+ prefixes | Millions+ | Hash-based distribution |

### Rate Limit Error Handling

```
HTTP 429: Too Many Requests
- Implement exponential backoff
- Retry with jitter
- Maximum retries: 5-10

HTTP 503: Service Unavailable
- Retry with exponential backoff
- Wait longer before retrying
- Maximum retries: 3-5
```

### Exponential Backoff Implementation

```python
import time
import random
from google.api_core import exceptions

def upload_with_backoff(blob, data, max_retries=5):
    """Upload with exponential backoff and jitter."""
    for attempt in range(max_retries):
        try:
            blob.upload_from_string(data)
            return True
        except (exceptions.TooManyRequests, exceptions.ServiceUnavailable) as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            base_delay = 2 ** attempt
            jitter = random.uniform(0, base_delay)
            delay = base_delay + jitter
            
            print(f"Retry {attempt + 1}/{max_retries} in {delay:.2f}s")
            time.sleep(delay)

# Usage
upload_with_backoff(bucket.blob("data.json"), '{"key": "value"}')
```

### Access Distribution Best Practices

```
DO:
✅ Spread requests across multiple prefixes
✅ Gradually ramp up request rates
✅ Use hash-based naming for high-write workloads
✅ Monitor request rates via Cloud Monitoring
✅ Implement client-side rate limiting

DON'T:
❌ Send burst traffic to single prefix
❌ Skip ramp-up period for new workloads
❌ Ignore 429 errors (always retry)
❌ Use sequential naming for high-throughput
❌ Exceed 5,000 QPS on single prefix
```

### Ramp-Up Guidelines

```
When increasing request rates:
- Start at 50% of target rate
- Increase by 10-20% every 5-10 minutes
- Monitor error rates during ramp-up
- Stop if error rate exceeds 1%
- Allow 30-60 minutes for full autoscaling

Example ramp-up to 50,000 QPS:
Minute 0:   5,000 QPS  (10%)
Minute 10:  10,000 QPS (20%)
Minute 20:  20,000 QPS (40%)
Minute 30:  30,000 QPS (60%)
Minute 40:  40,000 QPS (80%)
Minute 50:  50,000 QPS (100%)
```

---

## API Endpoints (Regional/Global/ITAR)

### Endpoint Types

| Endpoint Type | URL | Use Case | Latency |
|---------------|-----|----------|---------|
| **Global** | `storage.googleapis.com` | Default, worldwide access | Varies by location |
| **Regional** | `REGION.storage.googleapis.com` | Lower latency, single region | Lowest for region |
| **Dual-region** | Not directly supported | Uses multi-region bucket | Based on bucket |
| **ITAR** | `itar.storage.googleapis.com` | US government compliance | US only |

### Regional Endpoints

```
Available Regional Endpoints:
- us-central1.storage.googleapis.com
- us-east1.storage.googleapis.com
- us-west1.storage.googleapis.com
- europe-west1.storage.googleapis.com
- asia-east1.storage.googleapis.com
- (All GCP regions have endpoints)
```

### Using Regional Endpoints

```python
from google.cloud import storage
from google.api_core import client_options

# Use regional endpoint for lower latency
client = storage.Client(
    client_options=client_options.ClientOptions(
        api_endpoint="https://us-central1.storage.googleapis.com"
    )
)

# All operations use regional endpoint
bucket = client.bucket("my-bucket")
blob = bucket.blob("data.json")
blob.upload_from_string('{"key": "value"}')
```

### ITAR-Compliant Endpoints

```bash
# Use ITAR endpoint for government workloads
# Requires ITAR-compliant project and bucket

# JSON API ITAR endpoint
https://itar.storage.googleapis.com/storage/v1/

# gcloud with ITAR endpoint
gcloud config set api_endpoint_overrides/storage https://itar.storage.googleapis.com/
gcloud storage buckets list
```

### When to Use Regional vs Global

| Scenario | Use | Why |
|----------|-----|-----|
| Compute collocated with bucket | Regional endpoint | Lower latency |
| Multi-region compute | Global endpoint | Automatic routing |
| Government/compliance | ITAR endpoint | Regulatory requirement |
| Default configuration | Global endpoint | Simplicity |
| Performance optimization | Regional endpoint | 10-30% latency reduction |

---

## Troubleshooting Performance

### Slow Upload Diagnosis

```python
def diagnose_slow_upload(bucket_name, blob_name):
    """Diagnose slow upload issues."""
    checks = []
    
    # 1. Check network bandwidth
    import speedtest
    st = speedtest.Speedtest()
    upload_speed = st.upload() / 1_000_000  # Mbps
    checks.append(f"Upload speed: {upload_speed:.2f} Mbps")
    
    # 2. Check object size
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.reload()
    checks.append(f"Object size: {blob.size / 1_024 / 1_024:.2f} MB")
    
    # 3. Check location
    checks.append(f"Bucket location: {bucket.location}")
    
    # 4. Check for hotspot
    if blob_name.startswith(('0', '1', '2')):
        checks.append("WARNING: Possible hotspot with sequential naming")
    
    # 5. Check retry count
    # (Requires application-level instrumentation)
    
    return checks

print("\n".join(diagnose_slow_upload("my-bucket", "uploads/slow-file.bin")))
```

### Common Performance Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Hotspot** | High latency on specific prefix | Use diverse prefixes |
| **Single stream** | <100 MB/s throughput | Enable parallelism |
| **Wrong region** | 200+ ms latency | Colocate compute & storage |
| **Small chunks** | High overhead, low throughput | Increase chunk size to 32-64 MB |
| **No compression** | High egress costs | Enable gzip for text data |
| **Missing retries** | Intermittent failures | Add retry logic |
| **DNS resolution** | First request slow | Cache DNS or use IP |
| **Connection churn** | TLS overhead per request | Reuse connections |

### Performance Checklist

#### Upload Performance
- [ ] Use parallel uploads (16-32 threads minimum)
- [ ] Use resumable uploads for >10 MB objects
- [ ] Set chunk size to 32-64 MB
- [ ] Compress text-based data
- [ ] Use gRPC transport if available
- [ ] Avoid sequential object naming
- [ ] Monitor for hotspots
- [ ] Set appropriate timeouts (5-30 minutes for large)

#### Download Performance
- [ ] Use parallel downloads for multiple objects
- [ ] Use range reads for partial object access
- [ ] Enable CDN for frequently accessed objects
- [ ] Set Cache-Control headers
- [ ] Use hedged requests for latency-sensitive reads
- [ ] Implement client-side caching
- [ ] Reuse connections
- [ ] Configure retry logic

#### General Performance
- [ ] Colocate compute and storage
- [ ] Use HTTP/2 transport
- [ ] Enable connection pooling
- [ ] Set appropriate timeouts
- [ ] Implement retry logic with exponential backoff
- [ ] Monitor Cloud Monitoring metrics
- [ ] Set up alert policies
- [ ] Benchmark regularly

---

*"Performance is not a feature, it's a requirement. Parallelize everything, cache aggressively, and monitor constantly."* — Performance Engineer Mantra
