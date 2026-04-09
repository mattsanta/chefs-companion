output "dev_cluster_id" {
  value = google_container_cluster.dev.id
}

output "prod_cluster_id" {
  value = google_container_cluster.prod.id
}

output "repository_uri" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_id}"
}
