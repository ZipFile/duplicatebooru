variable "hcloud_token" {
  sensitive = true
  type      = string
}

variable "hcloud_ssh_keys" {
  type = list(string)
}

variable "hcloud_image" {
  type    = string
  default = "ubuntu-20.04"
}

variable "hcloud_server_type" {
  type    = string
  default = "cpx11"
}

variable "hcloud_location" {
  type    = string
  default = "hel1"
}

variable "cloudflare_email" {
  type = string
}

variable "cloudflare_api_key" {
  sensitive = true
  type = string
}

variable "cloudflare_token" {
  sensitive = true
  type = string
}

variable "cloudflare_zone_id" {
  type = string
}
