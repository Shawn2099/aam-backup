# Terraform Deployment - Google Cloud Storage

**Level**: Intermediate to Expert  
**Prerequisites**: [Bucket Configuration](./BUCKET_CONFIGURATION.md), Terraform basics  
**Time to Master**: 3-4 weeks of production deployments

---

## Table of Contents

1. [Terraform Fundamentals for GCS](#terraform-fundamentals-for-gcs)
2. [Basic Bucket Deployment](#basic-bucket-deployment)
3. [Production-Ready Module](#production-ready-module)
4. [Multi-Environment Setup](#multi-environment-setup)
5. [State Management](#state-management)
6. [IAM with Terraform](#iam-with-terraform)
7. [Lifecycle Rules](#lifecycle-rules)
8. [Advanced Configurations](#advanced-configurations)
9. [CI/CD Integration](#cicd-integration)
10. [Policy-as-Code](#policy-as-code)
11. [Drift Detection](#drift-detection)
12. [Migration Strategies](#migration-strategies)
13. [Testing Terraform](#testing-terraform)
14. [Common Pitfalls](#common-pitfalls)

---

## Terraform Fundamentals for GCS

### Provider Setup

```hcl
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  # Backend for state storage (use GCS!)
  backend "gcs" {
    bucket = "terraform-state-my-project"
    prefix = "state/gcs"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  
  # Authentication (choose one):
  # 1. Application Default Credentials (recommended)
  # 2. Service account key file
  # credentials = file(var.credentials_file)
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}
```

### Authentication Methods

| Method | Use Case | Security |
|--------|----------|----------|
| **ADC** (Application Default Credentials) | Local dev, CI/CD | ✅ Best |
| **Service account key file** | Legacy systems | ⚠️ Rotate keys |
| **Workload Identity** | GKE workloads | ✅ Best for K8s |
| **OIDC Federation** | GitHub Actions, external | ✅ No keys needed |

---

## Basic Bucket Deployment

### Simple Bucket

```hcl
resource "google_storage_bucket" "simple" {
  name     = "my-simple-bucket"
  location = "US-CENTRAL1"
}
```

### Production Bucket

```hcl
resource "google_storage_bucket" "production" {
  name     = "my-app-prod-data-us"
  location = "US-CENTRAL1"
  
  # Security
  uniform_bucket_level_access    = true
  public_access_prevention       = "enforced"
  force_destroy                  = false  # Prevent accidental deletion
  
  # Versioning
  versioning {
    enabled = true
  }
  
  # Labels
  labels = {
    environment = "production"
    managed-by  = "terraform"
    team        = "platform"
  }
  
  # Prevent accidental destruction
  lifecycle {
    prevent_destroy = true
  }
}
```

### Bucket with All Features

```hcl
resource "google_storage_bucket" "complete" {
  name          = "my-complete-bucket"
  location      = "US-CENTRAL1"
  storage_class = "STANDARD"
  
  # Security
  uniform_bucket_level_access    = true
  public_access_prevention       = "enforced"
  force_destroy                  = false
  
  # Versioning
  versioning {
    enabled = true
  }
  
  # Soft Delete (7 days)
  soft_delete_policy {
    retention_duration_seconds = 604800
  }
  
  # Retention Policy (unlocked)
  retention_policy {
    retention_period = 2592000  # 30 days
    is_locked        = false
  }
  
  # Lifecycle Rules
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
  
  lifecycle_rule {
    action {
      type = "AbortIncompleteMultipartUpload"
    }
    condition {
      age = 7
    }
  }
  
  # Encryption (CMEK)
  encryption {
    default_kms_key_name = google_kms_crypto_key.bucket_key.id
  }
  
  # Labels
  labels = {
    environment = "production"
    managed-by  = "terraform"
  }
}

resource "google_kms_key_ring" "gcs_keys" {
  name     = "gcs-keys"
  location = "us-central1"
}

resource "google_kms_crypto_key" "bucket_key" {
  name     = "gcs-bucket-key"
  key_ring = google_kms_key_ring.gcs_keys.id
  
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = false
  }
}

resource "google_kms_crypto_key_iam_member" "gcs_encrypter" {
  crypto_key_id = google_kms_crypto_key.bucket_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:service-${data.google_project.current.number}@gs-project-accounts.iam.gserviceaccount.com"
}

data "google_project" "current" {}
```

---

## Production-Ready Module

### Module Structure

```
modules/gcs-bucket/
├── main.tf
├── variables.tf
├── outputs.tf
├── iam.tf
├── lifecycle.tf
└── README.md
```

### modules/gcs-bucket/main.tf

```hcl
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "google_storage_bucket" "this" {
  name          = var.use_random_suffix ? "${var.name}-${random_id.bucket_suffix.hex}" : var.name
  location      = var.location
  storage_class = var.storage_class
  
  # Security
  uniform_bucket_level_access    = var.uniform_bucket_level_access
  public_access_prevention       = var.public_access_prevention
  force_destroy                  = var.force_destroy
  
  # Versioning
  dynamic "versioning" {
    for_each = var.enable_versioning ? [1] : []
    content {
      enabled = true
    }
  }
  
  # Soft Delete
  dynamic "soft_delete_policy" {
    for_each = var.enable_soft_delete ? [1] : []
    content {
      retention_duration_seconds = var.soft_delete_duration_seconds
    }
  }
  
  # Retention Policy
  dynamic "retention_policy" {
    for_each = var.retention_period > 0 ? [1] : []
    content {
      retention_period = var.retention_period
      is_locked        = var.lock_retention_policy
    }
  }
  
  # Encryption
  dynamic "encryption" {
    for_each = var.kms_key_name != "" ? [1] : []
    content {
      default_kms_key_name = var.kms_key_name
    }
  }
  
  # CORS
  dynamic "cors" {
    for_each = var.cors_rules
    content {
      origin          = cors.value.origins
      method          = lookup(cors.value, "methods", [])
      response_header = lookup(cors.value, "response_headers", [])
      max_age_seconds = lookup(cors.value, "max_age_seconds", 3600)
    }
  }
  
  # Website (if applicable)
  dynamic "website" {
    for_each = var.website_config != null ? [var.website_config] : []
    content {
      main_page_suffix = website.value.main_page_suffix
      not_found_page   = website.value.not_found_page
    }
  }
  
  # Logging
  logging {
    log_bucket        = var.logging_bucket
    log_object_prefix = var.logging_object_prefix
  }
  
  # Labels
  labels = merge(var.labels, {
    managed-by  = "terraform"
    environment = var.environment
  })
  
  lifecycle {
    prevent_destroy = var.prevent_destroy
  }
}
```

### modules/gcs-bucket/variables.tf

```hcl
variable "name" {
  description = "Bucket name (without suffix if using random suffix)"
  type        = string
}

variable "location" {
  description = "Bucket location (region or multi-region)"
  type        = string
  default     = "US-CENTRAL1"
}

variable "storage_class" {
  description = "Storage class"
  type        = string
  default     = "STANDARD"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "uniform_bucket_level_access" {
  description = "Enable uniform bucket-level access"
  type        = bool
  default     = true
}

variable "public_access_prevention" {
  description = "Public access prevention mode"
  type        = string
  default     = "enforced"
}

variable "force_destroy" {
  description = "Allow bucket destruction with objects"
  type        = bool
  default     = false
}

variable "prevent_destroy" {
  description = "Prevent bucket destruction in lifecycle"
  type        = bool
  default     = true
}

variable "enable_versioning" {
  description = "Enable object versioning"
  type        = bool
  default     = true
}

variable "enable_soft_delete" {
  description = "Enable soft delete"
  type        = bool
  default     = true
}

variable "soft_delete_duration_seconds" {
  description = "Soft delete retention duration in seconds"
  type        = number
  default     = 604800  # 7 days
}

variable "retention_period" {
  description = "Retention period in seconds (0 = disabled)"
  type        = number
  default     = 0
}

variable "lock_retention_policy" {
  description = "Lock retention policy (IRREVERSIBLE)"
  type        = bool
  default     = false
}

variable "kms_key_name" {
  description = "KMS key for default encryption"
  type        = string
  default     = ""
}

variable "cors_rules" {
  description = "CORS configuration rules"
  type = list(object({
    origins         = list(string)
    methods         = optional(list(string), [])
    response_headers = optional(list(string), [])
    max_age_seconds = optional(number, 3600)
  }))
  default = []
}

variable "website_config" {
  description = "Website configuration"
  type = object({
    main_page_suffix = string
    not_found_page   = string
  })
  default = null
}

variable "logging_bucket" {
  description = "Bucket for access logs"
  type        = string
  default     = ""
}

variable "logging_object_prefix" {
  description = "Prefix for log objects"
  type        = string
  default     = ""
}

variable "lifecycle_rules" {
  description = "Lifecycle management rules"
  type = list(object({
    action = object({
      type          = string
      storage_class = optional(string)
    })
    condition = object({
      age                    = optional(number)
      created_before         = optional(string)
      with_state             = optional(string)
      matches_storage_class  = optional(list(string))
      num_newer_versions     = optional(number)
      days_since_custom_time = optional(number)
    })
  }))
  default = []
}

variable "iam_bindings" {
  description = "IAM role bindings"
  type = map(object({
    role   = string
    member = string
  }))
  default = {}
}

variable "use_random_suffix" {
  description = "Append random suffix to bucket name"
  type        = bool
  default     = false
}

variable "labels" {
  description = "Additional labels"
  type        = map(string)
  default     = {}
}
```

### modules/gcs-bucket/iam.tf

```hcl
resource "google_storage_bucket_iam_member" "bindings" {
  for_each = var.iam_bindings
  
  bucket = google_storage_bucket.this.name
  role   = each.value.role
  member = each.value.member
}
```

### modules/gcs-bucket/lifecycle.tf

```hcl
resource "google_storage_bucket_lifecycle_rule" "rules" {
  for_each = { for idx, rule in var.lifecycle_rules : idx => rule }
  
  bucket = google_storage_bucket.this.name
  
  action {
    type          = each.value.action.type
    storage_class = lookup(each.value.action, "storage_class", null)
  }
  
  condition {
    age                    = lookup(each.value.condition, "age", null)
    created_before         = lookup(each.value.condition, "created_before", null)
    with_state             = lookup(each.value.condition, "with_state", null)
    matches_storage_class  = lookup(each.value.condition, "matches_storage_class", null)
    num_newer_versions     = lookup(each.value.condition, "num_newer_versions", null)
    days_since_custom_time = lookup(each.value.condition, "days_since_custom_time", null)
  }
}
```

### modules/gcs-bucket/outputs.tf

```hcl
output "bucket_name" {
  description = "Name of the bucket"
  value       = google_storage_bucket.this.name
}

output "bucket_url" {
  description = "gsutil URL of the bucket"
  value       = "gs://${google_storage_bucket.this.name}"
}

output "bucket_self_link" {
  description = "Self link of the bucket"
  value       = google_storage_bucket.this.self_link
}

output "bucket_id" {
  description = "ID of the bucket"
  value       = google_storage_bucket.this.id
}
```

### Using the Module

```hcl
module "production_bucket" {
  source = "./modules/gcs-bucket"
  
  name          = "my-app-prod-data"
  location      = "US-CENTRAL1"
  environment   = "production"
  use_random_suffix = true
  
  # Security
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  
  # Versioning & Recovery
  enable_versioning          = true
  enable_soft_delete         = true
  soft_delete_duration_seconds = 604800
  
  # Lifecycle
  lifecycle_rules = [
    {
      action = {
        type          = "SetStorageClass"
        storage_class = "NEARLINE"
      }
      condition = {
        age = 90
      }
    },
    {
      action = {
        type = "Delete"
      }
      condition = {
        age = 365
      }
    }
  ]
  
  # IAM
  iam_bindings = {
    app_writer = {
      role   = "roles/storage.objectAdmin"
      member = "serviceAccount:my-app@my-project.iam.gserviceaccount.com"
    }
    team_reader = {
      role   = "roles/storage.objectViewer"
      member = "group:team@example.com"
    }
  }
  
  labels = {
    application = "my-app"
    team        = "platform"
  }
}

output "bucket_name" {
  value = module.production_bucket.bucket_name
}
```

---

## Multi-Environment Setup

### Directory Structure

```
environments/
├── dev/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   └── backend.tf
├── staging/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   └── backend.tf
└── prod/
    ├── main.tf
    ├── variables.tf
    ├── terraform.tfvars
    └── backend.tf
```

### environments/dev/main.tf

```hcl
module "gcs_buckets" {
  source = "../../modules/gcs-bucket"
  
  for_each = var.buckets
  
  name          = "${each.key}-dev"
  location      = each.value.location
  environment   = "dev"
  storage_class = each.value.storage_class
  
  enable_versioning = each.value.enable_versioning
  force_destroy     = true  # OK for dev
  prevent_destroy   = false
  
  lifecycle_rules = each.value.lifecycle_rules
  iam_bindings    = each.value.iam_bindings
}
```

### environments/dev/terraform.tfvars

```hcl
project_id = "my-project-dev"
region     = "us-central1"

buckets = {
  app_data = {
    location          = "US-CENTRAL1"
    storage_class     = "STANDARD"
    enable_versioning = false
    
    lifecycle_rules = [
      {
        action = {
          type = "Delete"
        }
        condition = {
          age = 30
        }
      }
    ]
    
    iam_bindings = {
      dev_team = {
        role   = "roles/storage.objectAdmin"
        member = "group:dev-team@example.com"
      }
    }
  }
  
  logs = {
    location          = "US-CENTRAL1"
    storage_class     = "STANDARD"
    enable_versioning = false
    
    lifecycle_rules = [
      {
        action = {
          type = "Delete"
        }
        condition = {
          age = 7
        }
      }
    ]
  }
}
```

### environments/prod/terraform.tfvars

```hcl
project_id = "my-project-prod"
region     = "us-central1"

buckets = {
  app_data = {
    location          = "US-CENTRAL1"
    storage_class     = "STANDARD"
    enable_versioning = true
    
    lifecycle_rules = [
      {
        action = {
          type          = "SetStorageClass"
          storage_class = "NEARLINE"
        }
        condition = {
          age = 90
        }
      },
      {
        action = {
          type = "Delete"
        }
        condition = {
          age = 365
        }
      }
    ]
    
    iam_bindings = {
      prod_app = {
        role   = "roles/storage.objectAdmin"
        member = "serviceAccount:my-app-prod@my-project-prod.iam.gserviceaccount.com"
      }
    }
  }
}
```

### Workspace-Based Approach

```bash
# Initialize
terraform init

# Create workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Select workspace
terraform workspace select dev

# Deploy to dev
terraform apply -var-file="environments/dev/terraform.tfvars"

# Deploy to prod
terraform workspace select prod
terraform apply -var-file="environments/prod/terraform.tfvars"
```

---

## State Management

### Remote State with GCS

```hcl
# backend.tf
terraform {
  backend "gcs" {
    bucket = "terraform-state-my-project"
    prefix = "env/dev"
  }
}
```

### Create State Bucket

```hcl
# Create state bucket (run once, manually)
resource "google_storage_bucket" "terraform_state" {
  name     = "terraform-state-${var.project_id}"
  location = "US-CENTRAL1"
  
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  versioning {
    enabled = true
  }
  
  lifecycle {
    prevent_destroy = true
  }
}

# Enable bucket-level access logging
resource "google_storage_bucket" "terraform_state_logs" {
  name     = "terraform-state-logs-${var.project_id}"
  location = "US-CENTRAL1"
  
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}
```

### State Locking

GCS backend supports **implicit locking** via generation numbers:

```bash
# State locking is automatic
terraform apply  # Acquires lock

# Force unlock (if lock stuck)
terraform force-unlock LOCK_ID
```

### State Import

```bash
# Import existing bucket
terraform import google_storage_bucket.existing my-bucket-name

# Import with provider
terraform import module.gcs.google_storage_bucket.this my-bucket-name
```

---

## IAM with Terraform

### Individual Bindings

```hcl
resource "google_storage_bucket_iam_member" "viewer" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectViewer"
  member = "user:jane@example.com"
}

resource "google_storage_bucket_iam_member" "admin" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:app@project.iam.gserviceaccount.com"
}
```

### Bulk Bindings

```hcl
locals {
  iam_members = {
    viewer_user = {
      role   = "roles/storage.objectViewer"
      member = "user:jane@example.com"
    }
    viewer_group = {
      role   = "roles/storage.objectViewer"
      member = "group:team@example.com"
    }
    admin_sa = {
      role   = "roles/storage.objectAdmin"
      member = "serviceAccount:app@project.iam.gserviceaccount.com"
    }
  }
}

resource "google_storage_bucket_iam_member" "members" {
  for_each = local.iam_members
  
  bucket = google_storage_bucket.main.name
  role   = each.value.role
  member = each.value.member
}
```

### IAM Policy (Authoritative)

```hcl
# WARNING: This REPLACES all existing IAM bindings
resource "google_storage_bucket_iam_policy" "policy" {
  bucket = google_storage_bucket.main.name
  
  policy_data = jsonencode({
    version = 3
    bindings = [
      {
        role = "roles/storage.objectViewer"
        members = [
          "user:jane@example.com",
          "group:team@example.com"
        ]
      },
      {
        role = "roles/storage.objectAdmin"
        members = [
          "serviceAccount:app@project.iam.gserviceaccount.com"
        ]
      }
    ]
  })
}
```

### Conditional IAM

```hcl
resource "google_storage_bucket_iam_member" "time_limited" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectViewer"
  member = "user:contractor@example.com"
  
  condition {
    title       = "expires_2025"
    description = "Access expires end of 2025"
    expression  = "request.time < timestamp('2025-12-31T23:59:59Z')"
  }
}
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/terraform.yml
name: Terraform GCS

on:
  push:
    branches: [main]
    paths: ['infrastructure/**']
  pull_request:
    branches: [main]
    paths: ['infrastructure/**']

env:
  TF_VAR_project_id: ${{ secrets.GCP_PROJECT_ID }}

jobs:
  terraform:
    name: Terraform
    runs-on: ubuntu-latest
    
    permissions:
      contents: read
      id-token: write  # For OIDC auth
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123456789/locations/global/workloadIdentityPools/github/providers/my-provider
          service_account: terraform@my-project.iam.gserviceaccount.com
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0
      
      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/gcs
      
      - name: Terraform Format
        run: terraform fmt -check
        working-directory: infrastructure/gcs
      
      - name: Terraform Validate
        run: terraform validate
        working-directory: infrastructure/gcs
      
      - name: Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: infrastructure/gcs
      
      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply tfplan
        working-directory: infrastructure/gcs
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - plan
  - apply

variables:
  TF_VAR_project_id: $GCP_PROJECT_ID

.terraform_base:
  image: hashicorp/terraform:1.6.0
  before_script:
    - gcloud auth activate-service-account --key-file=$GOOGLE_CREDENTIALS
    - gcloud config set project $GCP_PROJECT_ID
    - terraform init

validate:
  extends: .terraform_base
  stage: validate
  script:
    - terraform validate
    - terraform fmt -check
  rules:
    - changes:
        - infrastructure/gcs/**/*

plan:
  extends: .terraform_base
  stage: plan
  script:
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - infrastructure/gcs/tfplan
  rules:
    - changes:
        - infrastructure/gcs/**/*

apply:
  extends: .terraform_base
  stage: apply
  script:
    - terraform apply tfplan
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      changes:
        - infrastructure/gcs/**/*
      when: manual
```

---

## Policy-as-Code

### Sentinel Policies (Terraform Cloud/Enterprise)

```hcl
# policies/gcs-enforce-security.sentinel
import "tfplan/v2" as tfplan

# Enforce uniform bucket-level access
uniform_access = filter tfplan.resource_changes as _, rc {
  rc.type is "google_storage_bucket" and
  rc.change.after.uniform_bucket_level_access is true
}

main = rule {
  length(uniform_access) is length(filter tfplan.resource_changes as _, rc {
    rc.type is "google_storage_bucket"
  })
}

# Enforce public access prevention
public_prevention = filter tfplan.resource_changes as _, rc {
  rc.type is "google_storage_bucket" and
  rc.change.after.public_access_prevention is "enforced"
}

main = main and rule {
  length(public_prevention) is length(filter tfplan.resource_changes as _, rc {
    rc.type is "google_storage_bucket"
  })
}
```

### OPA/Conftest

```rego
# policy/gcs.rego
package gcs

deny[msg] {
  input.resource_changes[_].type == "google_storage_bucket"
  input.resource_changes[_].change.after.uniform_bucket_level_access == false
  msg := "Uniform bucket-level access must be enabled"
}

deny[msg] {
  input.resource_changes[_].type == "google_storage_bucket"
  input.resource_changes[_].change.after.public_access_prevention != "enforced"
  msg := "Public access prevention must be enforced"
}

deny[msg] {
  input.resource_changes[_].type == "google_storage_bucket"
  input.resource_changes[_].change.after.versioning.enabled == false
  msg := "Versioning must be enabled for production buckets"
}
```

Run with conftest:
```bash
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json
conftest test tfplan.json -p policy/
```

---

## Drift Detection

### Manual Drift Check

```bash
# Check for drift
terraform plan -detailed-exitcode

# Exit codes:
# 0 = No drift
# 1 = Error
# 2 = Drift detected
```

### Automated Drift Detection (GitHub Actions)

```yaml
name: Drift Detection

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.TERRAFORM_SA }}
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
      
      - name: Terraform Init
        run: terraform init
      
      - name: Terraform Plan
        run: terraform plan -detailed-exitcode
        continue-on-error: true
        id: plan
      
      - name: Alert on Drift
        if: steps.plan.outcome == 'failure'
        run: |
          echo "Drift detected!"
          # Send Slack/PagerDuty notification
```

---

## Testing Terraform

### Terratest

```go
// test/gcs_test.go
package test

import (
  "testing"
  
  "github.com/gruntwork-io/terratest/modules/terraform"
  "github.com/stretchr/testify/assert"
)

func TestGcsBucketModule(t *testing.T) {
  t.Parallel()
  
  opts := &terraform.Options{
    TerraformDir: "../examples/basic",
    Vars: map[string]interface{}{
      "name":     "test-bucket",
      "location": "US-CENTRAL1",
    },
  }
  
  defer terraform.Destroy(t, opts)
  
  // Run terraform init and apply
  terraform.InitAndApply(t, opts)
  
  // Validate outputs
  bucketName := terraform.Output(t, opts, "bucket_name")
  assert.Contains(t, bucketName, "test-bucket")
}
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint
      - id: terraform_docs
      - id: terraform_tfsec
```

---

## Common Pitfalls

### 1. Forgetting `prevent_destroy`

```hcl
# ❌ BAD - Can accidentally delete production
resource "google_storage_bucket" "prod" {
  name = "production-data"
}

# ✅ GOOD - Protected from deletion
resource "google_storage_bucket" "prod" {
  name = "production-data"
  
  lifecycle {
    prevent_destroy = true
  }
}
```

### 2. Not Using Random Suffixes

```hcl
# ❌ BAD - Name collision on recreate
resource "google_storage_bucket" "main" {
  name = "my-unique-bucket-name"
}

# ✅ GOOD - Unique name
resource "random_id" "suffix" {
  byte_length = 4
}

resource "google_storage_bucket" "main" {
  name = "my-bucket-${random_id.suffix.hex}"
}
```

### 3. Missing IAM Bindings

```hcl
# ❌ BAD - No one can access the bucket
resource "google_storage_bucket" "main" {
  name = "my-bucket"
}

# ✅ GOOD - Explicit IAM bindings
resource "google_storage_bucket" "main" {
  name = "my-bucket"
}

resource "google_storage_bucket_iam_member" "app_access" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:app@project.iam.gserviceaccount.com"
}
```

### 4. Not Testing in Non-Prod

```
❌ Deploy directly to production
✅ dev → staging → production pipeline
```

### 5. Ignoring State Security

```hcl
# ❌ BAD - State file might contain secrets
# Store state in local file

# ✅ GOOD - Secure remote state
terraform {
  backend "gcs" {
    bucket = "terraform-state-secure"
    prefix = "state"
  }
}
```

---

## Quick Reference Commands

```bash
# Initialize
terraform init

# Format code
terraform fmt -recursive

# Validate syntax
terraform validate

# Preview changes
terraform plan

# Apply changes
terraform apply

# Destroy (if allowed)
terraform destroy

# Import existing resource
terraform import google_storage_bucket.main my-bucket

# State management
terraform state list
terraform state show google_storage_bucket.main
terraform state mv old_location new_location

# Workspace management
terraform workspace list
terraform workspace new prod
terraform workspace select prod
```

---

*"Terraform is your infrastructure. Treat it like production code: test it, version it, and review changes carefully."* — Infrastructure Engineer Mantra
