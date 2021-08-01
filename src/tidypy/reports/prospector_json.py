from datetime import datetime

import basicserial

from ..config import get_tools
from .base import Report


class ProspectorJsonReport(Report):
    """
    Formats the report in Prospector JSON format.
    """

    def execute(self, collector):
        issues = collector.get_issues(sortby=("filename", "line", "character"))
        result_json = {
            "summary": {
                "started": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "libraries": [],
                "strictness": "from profile",
                "profiles": "tidypy",
                "tools": list(get_tools().keys()),
                "message_count": collector.issue_count(),
                "completed": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "time_taken": "0",
                "formatter": "json",
            },
            "messages": [
                {
                    "source": issue.tool,
                    "code": issue.code,
                    "location": {
                        "path": self.relative_filename(issue.filename),
                        "module": None,
                        "function": None,
                        "line": issue.line,
                        "character": issue.character or 0,
                    },
                    "message": issue.message,
                }
                for issue in issues
            ],
        }
        self.output(basicserial.to_json(result_json, pretty=True))
