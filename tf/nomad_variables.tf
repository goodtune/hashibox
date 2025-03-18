resource "nomad_variable" "tw_config_param" {
  path  = "nomad/jobs"
  items = {
    artifactory = "http://172.20.10.2:10000"
    aba_txo_maxBaseMove = 1.4e-2
    aba_txo_maxError = 2.8e-6
  }
}
