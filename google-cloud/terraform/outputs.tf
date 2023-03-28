
output "houston-base-url" {
  value = module.houston.houston_base_url
  sensitive = true
}

output "houston-key" {
  value = module.houston-key.id
  sensitive = true
}