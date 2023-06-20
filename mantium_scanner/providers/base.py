import re
from abc import ABC


class BaseProvider(ABC):
    """Base provider class."""

    def search(self, scan: dict) -> list[str]:
        """Query documents by embedding."""
        raise NotImplementedError

    def match_pattern(self, doc_text: list[str], pattern: str) -> list[str]:
        """Match pattern in document text."""
        matches = []
        for text in doc_text:
            matches.extend(re.findall(re.compile(pattern), text))

        return matches
