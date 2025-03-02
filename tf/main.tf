locals {
  job_files = fileset("jobs", "*.nomad.hcl")
  jobspecs  = { for job in local.job_files : trimsuffix(job, ".nomad.hcl") => file("${path.module}/jobs/${job}") }
  sconspecs = { for job in fileset("scon", "*.hcl") : trimsuffix(job, ".hcl") => file("${path.module}/scon/${job}") }
}

resource "nomad_job" "this" {
  for_each = local.jobspecs
  jobspec  = each.value
}

resource "nomad_job" "scon" {
  for_each = local.sconspecs
  jobspec  = each.value
}
