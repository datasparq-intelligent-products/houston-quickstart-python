module "houston" {
  source  = "datasparq-ai/houston/google"
  version = "0.2.0"
  zone = "europe-west2-a"
}

module "houston-key" {
  source  = "datasparq-ai/houston-key/google"
  version = "0.1.0"
  name = "houston-key"
  houston_base_url = module.houston.houston_base_url
  houston_password = module.houston.houston_password
}

