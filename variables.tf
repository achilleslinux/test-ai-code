variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "secret_id" {
  description = "The name of the secret"
  type        = string
}

variable "secret_value" {
  description = "The value of the secret"
  type        = string
  sensitive   = true
}
