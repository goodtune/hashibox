job "bar" {
  region = "us"
  type   = "service"
  group "foo" {
    task "bar" {
      driver = "raw_exec"
      config {
        command = "/bin/sleep"
        args    = ["23h"]
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
