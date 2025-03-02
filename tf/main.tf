locals {
  job_files = fileset("jobs", "*.nomad.hcl")
  jobspecs  = { for job in local.job_files : trimsuffix(job, ".nomad.hcl") => file("${path.module}/jobs/${job}") }
}

resource "nomad_job" "this" {
  for_each = local.jobspecs
  jobspec  = each.value
}
