
variable "project_id" {
  description = "Google Cloud Project ID"
#  default = ""  // provide your project ID here or via the command line
}

provider "google" {
  project = var.project_id
}

module "houston" {
  source  = "datasparq-ai/houston/google"
  zone = "europe-west2-a"
#  instance_name = "my-houston-api"  // uncomment this if you don't want to use the default name 'houston'
}

module "houston-key" {
  source  = "datasparq-ai/houston-key/google"
  name = "Houston Quickstart"
  houston_base_url = module.houston.houston_base_url
  houston_password = module.houston.houston_password
#  secret_name = "my-houston-key"  // uncomment this if you don't want to use the default name 'houston-key'

  depends_on = [module.houston]
}
