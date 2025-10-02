import json
import argparse

from data_models import AffectedDependency, Severity

parser = argparse.ArgumentParser(description="Build summary CSV from Trivy results")
parser.add_argument("trivy_json", help="File with postprocessed Trivy JSON results")
args = parser.parse_args()

# choices from Trivy: lang-pkgs, os-pkgs
IMPORTANT_VULN_CLASSES = ['lang-pkgs']
IMPORTANT_VULN_SEVERITIES = [Severity.CRITICAL, Severity.HIGH]

vulns = []
with open(args.trivy_json, 'r') as f:
    data = json.load(f)
    for obj_dict in data:
        dep = AffectedDependency(**obj_dict)
        vulns.append(dep)

vulns = sorted(vulns, key=lambda v: (v.severity, v.age), reverse=True)

vulns_important_fixable = [
    vuln for vuln in vulns
    if (
            vuln.vuln_class in IMPORTANT_VULN_CLASSES
            and vuln.severity in IMPORTANT_VULN_SEVERITIES
            and vuln.fix is not None
    )
]
important_rows_fixable = "\n".join(
    f"| {vuln.vuln_class} | {vuln.vuln_type} | {vuln.name} | {vuln.version} | {vuln.severity.name} | {vuln.age} | {vuln.fix} | "
    f"[{vuln.cve}]({vuln.cve_url}) | {vuln.title} |"
    for vuln in vulns_important_fixable
)

important_rows_unfixable = "\n".join(
    f"| {vuln.vuln_class} | {vuln.vuln_type} | {vuln.name} | {vuln.version} | {vuln.severity.name} | "
    f"[{vuln.cve}]({vuln.cve_url}) | {vuln.title} |"
    for vuln in vulns
    if (
            vuln.vuln_class in IMPORTANT_VULN_CLASSES
            and vuln.severity in IMPORTANT_VULN_SEVERITIES
            and vuln.fix is None
    )
)

minor_rows = "\n".join(
    f"| {vuln.vuln_class} | {vuln.vuln_type} | {vuln.name} | {vuln.version} | {vuln.severity.name} | "
    f"[{vuln.cve}]({vuln.cve_url}) | {vuln.title} |"
    for vuln in vulns
    if (
            vuln.vuln_class not in IMPORTANT_VULN_CLASSES
            or vuln.severity not in IMPORTANT_VULN_SEVERITIES
    )
)

important_fixable_section = ""
if important_rows_fixable:
    important_fixable_section = f"""
### :exclamation: Important vulnerabilities

- Total: {len(vulns_important_fixable)}
- Critical: {len([vuln for vuln in vulns_important_fixable if vuln.severity == Severity.CRITICAL])}
- High: {len([vuln for vuln in vulns_important_fixable if vuln.severity == Severity.HIGH])}

| Class | Type | Dep. name | Version | Severity | Vuln. age (days) | Fix | CVE ID | Title |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{important_rows_fixable}
"""

important_unfixable_section = ""
if important_rows_unfixable:
    important_unfixable_section = f"""
<details>

<summary>:warning: Important, but not fixable</summary>

<br>

| Class | Type | Dep. name | Version | Severity | CVE ID | Title |
| --- | --- | --- | --- | --- | --- | --- |
{important_rows_unfixable}

</details>
"""

minor_section = ""
if minor_rows:
    minor_section = f"""
### :information_source: Other vulnerabilities

<details>

<summary>Minor packages vulnerabilities</summary>

<br>

| Class | Type | Dep. name | Version | Severity | CVE ID | Title |
| --- | --- | --- | --- | --- | --- | --- |
{minor_rows}

</details>
"""

strtpl = f"""

{important_fixable_section}
{important_unfixable_section}
{minor_section}
"""
print(strtpl)

