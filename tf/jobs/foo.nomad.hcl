job "foo" {
  datacenters = ["us-west-1", "us-east-1", "us-west-2"]
  type        = "service"
  group "foo" {
    task "foo" {
      driver = "raw_exec"

      config {
        command = "/bin/sleep"
        args    = ["5m"]
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
