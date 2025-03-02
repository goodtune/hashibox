job "caddy" {
  region = "us"
  type   = "system" # Ensures it runs on all clients

  group "reverse-proxy" {
    network {
      port "http" {
        to = 80
      }
      port "https" {
        to = 443
      }
    }

    task "caddy" {
      driver = "docker"

      config {
        image = "caddy:latest"
        ports = ["http", "https"]
        volumes = [
          "local/caddy/Caddyfile:/etc/caddy/Caddyfile"
        ]
      }

      resources {
        cpu    = 100
        memory = 128
      }

      service {
        name = "caddy"
        port = "http"
        tags = ["reverse-proxy"]
      }

      service {
        name = "caddy-https"
        port = "https"
        tags = ["reverse-proxy", "secure"]
      }

      template {
        data = <<-EOF
          {
            auto_https disable_redirects
          }

          :80 {
            respond "Hello, world!"
          }

          :443 {
            respond "Hello, world! Secure edition."
          }
          EOF

        destination = "local/caddy/Caddyfile"
      }
    }
  }
}
