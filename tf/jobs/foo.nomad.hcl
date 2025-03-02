job "foo" {
  region = "us"
  type   = "service"

  constraint {
    attribute = "${attr.unique.hostname}"
    operator  = "="
    value     = "node-client-1" # Ensure only one instance runs on a specific node
  }

  group "foo" {
    task "foo" {
      driver = "raw_exec"

      config {
        command = "/bin/sleep"
        args    = ["23h"]
      }

      // I've manually added the user 'operat' to each of the clients for now
      user = "operat"

      resources {
        cpu    = 20
        memory = 10
      }

      logs {
        max_files     = 3
        max_file_size = 10
      }
    }
  }
}
