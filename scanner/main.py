from typing import Any

from scanner.scanner import Scanner


def run_scan(vector_database: Any, profile_name: str = 'employee.json') -> None:
    """
    Run scan

    Iterate over queries in profile and run them against the index.
    """
    # Create a scanner
    scanner = Scanner(vector_database)

    # Run queries
    results = scanner.run_queries(profile_name)

    print(results)
