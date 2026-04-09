variable "project_id" {
  type        = string
  description = "The GCP project ID"
  default     = "mattsanta-new-project"
}

variable "region" {
  type        = string
  description = "The GCP region"
  default     = "us-central1"
}

variable "repository_id" {
  type        = string
  description = "The Artifact Registry repository ID"
  default     = "chefs-comp-app"
}

variable "pipeline_id" {
  type        = string
  description = "The Cloud Deploy pipeline ID"
  default     = "chefs-companion"
}
