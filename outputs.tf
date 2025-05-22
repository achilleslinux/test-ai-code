output "secret_name" {
  value       = google_secret_manager_secret.secret.name
  description = "Name of the created secret"
}
