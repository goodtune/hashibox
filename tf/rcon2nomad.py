#!/usr/bin/env python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "jinja2",
# ]
# ///

from pathlib import Path
import jinja2
import hashlib

# Define the Jinja2 template for the Nomad HCL file
nomad_template = """
job "{{ name }}" {
  datacenters = ["{{ datacenter }}"]

  constraint {
    attribute = "${attr.unique.hostname}"
    operator  = "="
    value     = "{{ host }}"
  }

  group "scon" {
    task "server" {
      driver = "raw_exec"

      config {
        command = "local/{{ name }}"
        // Caddy doesn't behave like Optiver C++ apps so
        // I'm adding args to move past that.
        # args = ["run", "--config", "local/{{ config.name }}"]
        args = ["run", "--config", "local/Caddyfile"]
      }

      artifact {
        source      = "http://172.23.210.169:10000/{{ binary }}"
        destination = "local/{{ name }}"
        mode        = "file"
        options {
          checksum = "sha256:{{ checksum }}"
        }
      }

      template {
        data = <<EOF
{{ config.open().read() }}
EOF
        # destination = "local/{{ config.name }}"
        destination = "local/Caddyfile"
      }

      resources {
        cores  = 1
        memory = 256
      }
    }
  }
  ui {
    description = "Optiver : {{ name }}"
    link {
      label = "Learn more about {{ name }}"
      url   = "https://optic.aus.optiver.com/optic/app/nomad"
    }
  }
}
"""


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def extract_values_from_rcon_conf():
    rcon_conf_files = Path("prodconfig/src").glob("*/rcon.conf")

    env = jinja2.Environment(loader=jinja2.BaseLoader)
    template = env.from_string(nomad_template)

    scon = Path("scon").resolve()
    scon.mkdir(exist_ok=True)

    # Very naive home-rolled rcon.conf parsing
    for rcon_conf_file in rcon_conf_files:
        colo = rcon_conf_file.parent
        with rcon_conf_file.open("r") as file:
            for line in file:
                host, name, command, extra = line.strip().split(":")
                symlink = colo / name / name
                binary = symlink.resolve()
                checksum = calculate_sha256(binary)
                config = colo / name / f"{name}.xml"
                job = scon / f"{name}.hcl"
                rendered_hcl = template.render(
                    datacenter=colo.name,
                    host=host,
                    name=name,
                    command=command,
                    extra=extra,
                    binary=binary.relative_to(Path("prodconfig").resolve()),
                    checksum=checksum,
                    config=config,
                )

                with job.open("wt") as hcl:
                    hcl.write(rendered_hcl)


if __name__ == "__main__":
    extract_values_from_rcon_conf()
