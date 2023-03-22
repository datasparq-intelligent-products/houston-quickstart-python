variable "houston_zone" {
  type = string
  description = "GCP zone that the Houston server will be deployed"
  default = "europe-west2-a"
}

variable "houston_compute_name"{
  type = string
  description = "Name for the compute instance used by the houston server"
  default = "houston-quickstart-server"
}

variable "houston_key_name" {
  type = string
  description = "Name for the Houston API Key and secret for your project"
  default = "houston-default"
}