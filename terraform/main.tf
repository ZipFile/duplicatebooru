terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.33"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 3.13"
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}

provider "cloudflare" {
  email   = var.cloudflare_email
  api_key = var.cloudflare_api_key
}

data "cloudflare_ip_ranges" "cloudflare" {}

resource "hcloud_firewall" "duplicatebooru" {
  name = "duplicatebooru"

  rule {
    direction   = "in"
    protocol    = "icmp"
    description = "PING"
    source_ips  = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction   = "in"
    protocol    = "tcp"
    port        = "22"
    description = "SSH"
    source_ips  = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction   = "in"
    protocol    = "tcp"
    port        = "80"
    description = "HTTP"
    source_ips  = data.cloudflare_ip_ranges.cloudflare.cidr_blocks
  }

  rule {
    direction   = "in"
    protocol    = "tcp"
    port        = "443"
    description = "HTTPS"
    source_ips  = data.cloudflare_ip_ranges.cloudflare.cidr_blocks
  }
}

resource "hcloud_firewall_attachment" "duplicatebooru" {
  firewall_id = hcloud_firewall.duplicatebooru.id
  server_ids  = [hcloud_server.duplicatebooru.id]
}

resource "hcloud_server" "duplicatebooru" {
  name        = "duplicatebooru"
  image       = var.hcloud_image
  server_type = var.hcloud_server_type
  location    = var.hcloud_location
  ssh_keys    = var.hcloud_ssh_keys
}

output "ipv4" {
  value = hcloud_server.duplicatebooru.ipv4_address
}

output "ipv6" {
  value = hcloud_server.duplicatebooru.ipv6_address
}

resource "cloudflare_record" "duplicatebooru_dns_a" {
  zone_id = var.cloudflare_zone_id
  name    = "duplicatebooru"
  proxied = true
  value   = hcloud_server.duplicatebooru.ipv4_address
  type    = "A"
  ttl     = 1
}

resource "cloudflare_record" "duplicatebooru_dns_aaaa" {
  zone_id = var.cloudflare_zone_id
  name    = "duplicatebooru"
  proxied = true
  value   = hcloud_server.duplicatebooru.ipv6_address
  type    = "AAAA"
  ttl     = 1
}
