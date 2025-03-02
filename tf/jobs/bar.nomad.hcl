job "bar" {
  datacenters = ["us-west-1", "us-west-2"]
  type        = "service"
  group "foo" {
    task "bar" {
      driver = "raw_exec"
      config {
        command = "/bin/sleep"
        args    = ["15m"]
      }

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
