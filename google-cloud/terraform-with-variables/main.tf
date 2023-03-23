module "houston" {
  source  = "datasparq-ai/houston/google"
  version = "0.2.0"
  zone = var.houston_zone
  instance_name = var.houston_compute_name
}

module "houston-key" {
  source  = "datasparq-ai/houston-key/google"
  version = "0.1.0"
  name = var.houston_key_name
  houston_base_url = module.houston.houston_base_url
  houston_password = module.houston.houston_password
  secret_name = var.houston_key_name
}

