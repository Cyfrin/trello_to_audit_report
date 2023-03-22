import re


class Finding:
    def __init__(
        self,
        description: str = "",
        severity: str = "",
        title: str = "",
        number: int = 1,
    ):
        """A finding in an audit report"""
        self.description = description
        self.severity = severity
        self.title = title
        self.number = number

    def __str__(self):
        return f"""
## [{self.severity}-{self.number}] {self.title}
{self.description}
"""

    def get_summary_title(self) -> str:
        finding_summary_title = (
            self.severity + "-" + str(self.number) + " " + self.title
        )
        return finding_summary_title

    def get_summary_title_hyperlink(self) -> str:
        """Create a hyperlink from a title"""
        summary_title = "#" + self.get_summary_title()
        summary_title = summary_title.lower()
        summary_title = re.sub(r"[\[\]\(\)]", "", summary_title)
        summary_title = re.sub(r"\s+", "-", summary_title)
        summary_title = re.sub(r"[^a-z0-9-_]", "", summary_title)
        return f"#{summary_title}"
