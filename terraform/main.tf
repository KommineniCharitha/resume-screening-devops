# ── Terraform: Resume Screener Infrastructure ────────────────────────────────
# Provisions a local Docker container using the Docker provider.
# Compatible with Minikube / local dev environments.
# For cloud, swap the docker provider for aws/gcp/azurerm.
# ─────────────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.6"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  # Defaults to local Docker socket: unix:///var/run/docker.sock
  # For remote Docker: host = "tcp://remote-host:2376"
}

# ── Variables ─────────────────────────────────────────────────────────────────
variable "app_image" {
  description = "Docker image for the resume screener"
  type        = string
  default     = "nginx:latest"
}

variable "container_name" {
  description = "Name for the Docker container"
  type        = string
  default     = "resume-screener"
}

variable "host_port" {
  description = "Host port to expose the app on"
  type        = number
  default     = 5050
}

variable "replicas" {
  description = "Number of containers to run"
  type        = number
  default     = 1
}

# ── Pull / reference the Docker image ────────────────────────────────────────
resource "docker_image" "resume_screener" {
  name         = var.app_image
  keep_locally = true
}

# ── Create container(s) ───────────────────────────────────────────────────────
resource "docker_container" "resume_screener" {
  count = var.replicas
  name  = "${var.container_name}-${count.index}"
  image = docker_image.resume_screener.image_id

  ports {
    internal = 5000
    external = var.host_port + count.index   # 5000, 5001, ... for replicas
  }

  env = [
    "FLASK_ENV=production"
  ]

  restart = "unless-stopped"

  healthcheck {
  test         = ["CMD", "curl", "-f", "http://localhost"]
  interval     = "30s"
  timeout      = "10s"
  retries      = 3
  start_period = "10s"
}

  labels {
    label = "project"
    value = "resume-screener"
  }
  labels {
    label = "managed-by"
    value = "terraform"
  }
}

# ── Outputs ───────────────────────────────────────────────────────────────────
output "container_ids" {
  description = "IDs of provisioned containers"
  value       = [for c in docker_container.resume_screener : c.id]
}

output "app_urls" {
  description = "URLs to access the app"
  value       = [for i in range(var.replicas) : "http://localhost:${var.host_port + i}"]
}
