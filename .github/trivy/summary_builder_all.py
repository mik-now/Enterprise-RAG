import os
import json
import csv
from data_models import AffectedDependency
import argparse

parser = argparse.ArgumentParser(description="Build summary CSV from Trivy results")
parser.add_argument("results_dir", help="Directory containing Trivy results")
parser.add_argument("output_csv", help="Output CSV file name")
args = parser.parse_args()

results_dir = args.results_dir
output_csv = args.output_csv


fieldnames = [
    "image",
    "vuln_class",
    "vuln_type",
    "name",
    "version",
    "severity",
    "published_date",
    "fix",
    "cve",
    "cve_url",
    "title"
]

with open(output_csv, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for img_dir in os.listdir(results_dir):
        full_path = os.path.join(results_dir, img_dir)
        if os.path.isdir(full_path):
            json_path = os.path.join(full_path, "trivy-postprocessed.json")
            if os.path.isfile(json_path):
                with open(json_path, "r") as f:
                    data = json.load(f)
                for obj_dict in data:
                    dep = AffectedDependency(**obj_dict)
                    row = dep.to_dict()
                    row["image"] = img_dir.split("trivy-reports-", 1)[-1]
                    # If severity is an enum, convert to string
                    if hasattr(row["severity"], "name"):
                        row["severity"] = row["severity"].name
                    writer.writerow(row)
