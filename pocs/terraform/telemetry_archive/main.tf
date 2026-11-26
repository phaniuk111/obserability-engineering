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
  }
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

output "bucket_arn" { value = aws_s3_bucket.telemetry.arn }
