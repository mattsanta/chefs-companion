locals {
  apis = [
    "container.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "clouddeploy.googleapis.com",
    "developerconnect.googleapis.com",
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(local.apis)
  project  = var.project_id
  service  = each.key

  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "app_repo" {
  location      = var.region
  repository_id = var.repository_id
  description   = "Docker repository for Chefs Companion"
  format        = "DOCKER"

  depends_on = [google_project_service.apis["artifactregistry.googleapis.com"]]
}

resource "google_container_cluster" "dev" {
  name     = "dev-cluster"
  location = var.region
  enable_autopilot = true

  depends_on = [google_project_service.apis["container.googleapis.com"]]
}

resource "google_container_cluster" "prod" {
  name     = "prod-cluster"
  location = var.region
  enable_autopilot = true

  depends_on = [google_project_service.apis["container.googleapis.com"]]
}

resource "google_clouddeploy_delivery_pipeline" "main" {
  location = var.region
  name     = var.pipeline_id

  serial_pipeline {
    stages {
      target_id = google_clouddeploy_target.dev.target_id
    }
    stages {
      target_id = google_clouddeploy_target.prod.target_id
    }
  }

  depends_on = [google_project_service.apis["clouddeploy.googleapis.com"]]
}

resource "google_clouddeploy_target" "dev" {
  location = var.region
  name     = "${var.pipeline_id}-dev"

  gke {
    cluster = google_container_cluster.dev.id
  }
}

resource "google_clouddeploy_target" "prod" {
  location = var.region
  name     = "${var.pipeline_id}-prod"

  gke {
    cluster = google_container_cluster.prod.id
  }
}

resource "google_clouddeploy_automation" "rollback" {
  location          = var.region
  delivery_pipeline = google_clouddeploy_delivery_pipeline.main.name
  name              = "rollback-on-failure"
  service_account   = "360003442539-compute@developer.gserviceaccount.com"

  selector {
    targets {
      id = "*"
    }
  }

  rules {
    repair_rollout_rule {
      id = "repair-rule"
      repair_phases {
        rollback {}
      }
    }
  }
}

resource "google_clouddeploy_automation" "promote" {
  location          = var.region
  delivery_pipeline = google_clouddeploy_delivery_pipeline.main.name
  name              = "promote-to-prod"
  service_account   = "360003442539-compute@developer.gserviceaccount.com"

  selector {
    targets {
      id = google_clouddeploy_target.dev.name
    }
  }

  rules {
    promote_release_rule {
      id                  = "promote-rule"
      destination_target_id = "@next"
    }
  }
}

resource "google_cloudbuild_trigger" "main" {
  name     = "chefs-companion-main"
  location = var.region

  developer_connect_event_config {
    git_repository_link = "projects/${var.project_id}/locations/${var.region}/connections/5d5e5445-9cb1-4a1d-ab12-e83e8c7b12b5/gitRepositoryLinks/mattsanta-chefs-companion"
    push {
      branch = "^main$"
    }
  }

  filename = "cloudbuild.yaml"
  service_account = "projects/${var.project_id}/serviceAccounts/cloudbuild-trigger-sa@${var.project_id}.iam.gserviceaccount.com"

  depends_on = [google_project_service.apis["cloudbuild.googleapis.com"]]
}

# IAM Permissions
resource "google_project_iam_member" "cloudbuild_deploy" {
  project = var.project_id
  role    = "roles/clouddeploy.releaser"
  member  = "serviceAccount:360003442539@cloudbuild.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_service_agent" {
  project = var.project_id
  role    = "roles/clouddeploy.serviceAgent"
  member  = "serviceAccount:360003442539@cloudbuild.gserviceaccount.com"
}

resource "google_project_iam_member" "clouddeploy_job_runner" {
  project = var.project_id
  role    = "roles/clouddeploy.jobRunner"
  member  = "serviceAccount:360003442539-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "clouddeploy_container_admin" {
  project = var.project_id
  role    = "roles/container.admin"
  member  = "serviceAccount:360003442539-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_devconnect_user" {
  project = var.project_id
  role    = "roles/developerconnect.admin"
  member  = "serviceAccount:360003442539-compute@developer.gserviceaccount.com"
}
