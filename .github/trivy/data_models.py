from datetime import datetime, timezone
from enum import IntEnum

class Severity(IntEnum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    UNKNOWN = 0


class AffectedDependency:
    """To avoid duplicates of vulnerabilities coming from different
    places of same package, __hash__ and __eq__ are implemented,
    so that objects are suitable to use in sets."""

    def __init__(
            self,
            vuln_class: str,
            vuln_type: str,
            name: str,
            version: str,
            severity: Severity,
            published_date: str,
            fix: str,
            cve: str,
            cve_url: str,
            title: str
    ):
        self.vuln_class = vuln_class
        self.vuln_type = vuln_type
        self.name = name
        self.version = version
        if isinstance(severity, int):
            severity = Severity(severity)
        self.severity = severity
        self.published_date = published_date
        self.fix = fix
        self.cve = cve
        self.cve_url = cve_url
        self.title = title

    def __eq__(self, other):
        if not isinstance(other, AffectedDependency):
            return False
        return self.name == other.name and self.cve == other.cve

    def __hash__(self):
        return hash((self.name, self.cve))

    @property
    def age(self) -> int:
        if self.published_date is None:
            return 0
        # Handle case with and without microseconds
        try:
            published = datetime.strptime(self.published_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            published = datetime.strptime(self.published_date, "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.now(timezone.utc)
        age_days = (now - published.replace(tzinfo=timezone.utc)).days
        return age_days

    def to_dict(self):
        return {
            "vuln_class": self.vuln_class,
            "vuln_type": self.vuln_type,
            "name": self.name,
            "version": self.version,
            "severity": self.severity,
            "published_date": self.published_date,
            "fix": self.fix,
            "cve": self.cve,
            "cve_url": self.cve_url,
            "title": self.title
        }
