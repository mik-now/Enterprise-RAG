"""
This script processes Trivy JSON to form that will be used
for per-image results and summary.
"""

import json
import argparse

from data_models import AffectedDependency, Severity

parser = argparse.ArgumentParser(description="Process Trivy JSON results.")
parser.add_argument("input_file", help="Input Trivy JSON filename")
parser.add_argument("output_file", help="Output processed JSON filename")
args = parser.parse_args()

with open(args.input_file, 'r') as f:
    data = json.load(f)

deps = []

for r in data["Results"]:
    if "Vulnerabilities" not in r:
        continue

    for vuln in r["Vulnerabilities"]:
        fix = None
        if vuln["Status"] == "fixed":
            fix = vuln["FixedVersion"]
        dep = AffectedDependency(
            r["Class"],
            r["Type"],
            vuln["PkgName"],
            vuln["InstalledVersion"],
            Severity[vuln["Severity"]],
            vuln.get("PublishedDate"),
            fix,
            vuln["VulnerabilityID"],
            vuln["PrimaryURL"],
            vuln["Title"]
        )
        deps.append(dep)

# Remove duplicates
deps = set(deps)
deps = list(deps)
deps_dicted = [d.to_dict() for d in deps]

with open(args.output_file, 'w') as f:
    f.write(json.dumps(deps_dicted, indent=4))
