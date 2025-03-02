#!/usr/bin/env python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
#     "jinja2",
# ]
# ///

import hashlib
import re
from pathlib import Path

import click
import jinja2

EXTRA_RE = re.compile(r'(\w+)=(?:"([^"]+)"|([^:]+))')

# Define the Jinja2 template for the Nomad HCL file
nomad_template = """
job "{{ name }}" {
  {% if datacenter -%}
  # job will only be allowed to run in this datacenter (swd:colo)
  datacenters = ["{{ datacenter }}"]
  {%- else -%}
  # not pinning to datacenter/s - jobs can roam
  region = "us"
  {%- endif %}

  {% if constraint -%}
  # job will only be allowed to run on this specific host
  constraint {
    attribute = "${attr.unique.hostname}"
    operator  = "="
    value     = "{{ host }}"
  }
  {%- endif %}

  group "{{ name }}" {
    task "{{ name }}" {
      driver = "raw_exec"

      config {
        command = "local/{{ name }}"
        // Caddy doesn't behave like Optiver C++ apps so
        // I'm adding args to move past that.
        # args = ["run", "--config", "local/{{ config.name }}"]
        args = ["run", "--config", "local/Caddyfile"]
      }

      user = "{{ extra.user|default("operat") }}"

      artifact {
        source      = "http://172.23.210.169:10000/{{ binary }}"
        destination = "local/{{ name }}"
        mode        = "file"
        options {
          checksum = "sha256:{{ checksum }}"
        }
      }

      resources {
        {% if extra.memory -%}
        memory = {{ extra.memory }}
        {%- endif %}
      }

      template {
        data = <<EOF
{{ config.open().read() }}
EOF
        # destination = "local/{{ config.name }}"
        destination = "local/Caddyfile"
      }
    }
  }

  ui {
    {% if extra.info -%}
    description = "{{ extra.info }}"
    {%- else -%}
    description = "Optiver : {{ name }}"
    {%- endif %}
    link {
      label = "Learn more about {{ name }}"
      url   = "https://optic.aus.optiver.com/optic/app/{{ name }}"
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


@click.command()
@click.option("--mode", default="datacenter")
@click.option("--constraint/--no-constraint", is_flag=True, default=True)
def rcon2nomad(mode, constraint):
    rcon_conf_files = Path("prodconfig/src").glob("*/rcon.conf")

    env = jinja2.Environment(loader=jinja2.BaseLoader)
    template = env.from_string(nomad_template)

    scon = Path("scon").resolve()
    scon.mkdir(exist_ok=True)

    # Remove all hcl files in scon intermediate directory to ensure we
    # would destroy any job that gets undefined.
    for hcl_file in scon.glob("*.hcl"):
        hcl_file.unlink()

    # Very naive home-rolled rcon.conf parsing
    for rcon_conf_file in rcon_conf_files:
        colo = rcon_conf_file.parent
        with rcon_conf_file.open("r") as file:
            for line in file:
                host, name, command, extra = line.strip().split(":", 3)
                symlink = colo / name / name
                binary = symlink.resolve()
                checksum = calculate_sha256(binary)
                config = colo / name / f"{name}.xml"
                job = scon / f"{name}.hcl"
                extra = [
                    (key, quoted or unquoted)
                    for key, quoted, unquoted in EXTRA_RE.findall(extra)
                ]
                rendered_hcl = template.render(
                    datacenter=colo.name if mode == "datacenter" else None,
                    host=host,
                    name=name,
                    command=command,
                    extra=dict(extra),
                    binary=binary.relative_to(Path("prodconfig").resolve()),
                    checksum=checksum,
                    config=config,
                    constraint=constraint,
                )

                with job.open("wt") as hcl:
                    hcl.write(rendered_hcl)


if __name__ == "__main__":
    rcon2nomad()
