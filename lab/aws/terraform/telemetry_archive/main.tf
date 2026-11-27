# Telemetry archive bucket with tiering, mirroring the ClickHouse TTL idea
# (book ch14: hot -> cheaper storage at 90 days -> delete at 365) and Retriever's
# "closed segments go to S3" (ch13). Also an SLO-style CloudWatch alarm on the
# collector's own export failures: observability of observability (ch24).
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
}

variable "bucket_name" { type = string }
variable "collector_namespace" {
  type    = string
  default = "otelcol"
}

resource "aws_s3_bucket" "telemetry" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_public_access_block" "telemetry" {
  bucket                  = aws_s3_bucket.telemetry.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "telemetry" {
  bucket = aws_s3_bucket.telemetry.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "aws:kms" }
    bucket_key_enabled = true # one data key per bucket, not per object: far fewer KMS calls
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "telemetry" {
  bucket = aws_s3_bucket.telemetry.id
  rule {
    id     = "tier-and-expire"
    status = "Enabled"
    filter { prefix = "telemetry/" }
    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }
    expiration { days = 365 }
    abort_incomplete_multipart_upload { days_after_initiation = 7 }
  }
  # Only useful if a second awss3 exporter writes sampled-in error traces under this prefix.
  rule {
    id     = "keep-errors-longer"
    status = "Enabled"
    filter { prefix = "telemetry-errors/" }
    transition {
      days          = 90
      storage_class = "GLACIER_IR"
    }
    expiration { days = 730 }
  }
}

# Alert on the pipeline failing to deliver telemetry, not on host CPU.
# These metrics are the Collector's own telemetry. They only exist in CloudWatch if you
# ship them there, so set var.collector_namespace to wherever they land.
resource "aws_cloudwatch_metric_alarm" "collector_export_failures" {
  alarm_name          = "otelcol-export-failures"
  namespace           = var.collector_namespace
  metric_name         = "otelcol_exporter_send_failed_spans"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 3
  threshold           = 1000
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
}

# The opposite failure: a dead Collector reports no failures at all. Missing data on
# "spans accepted" is the signal, so here missing data counts as breaching.
resource "aws_cloudwatch_metric_alarm" "collector_silent" {
  alarm_name          = "otelcol-no-spans-accepted"
  namespace           = var.collector_namespace
  metric_name         = "otelcol_receiver_accepted_spans"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 3
  threshold           = 1
  comparison_operator = "LessThanThreshold"
  treat_missing_data  = "breaching"
}

output "bucket_arn" { value = aws_s3_bucket.telemetry.arn }
