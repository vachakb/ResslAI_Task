"""Simple file keyword search tool.

API:
- search_in_file(path: str, keyword: str, case_insensitive: bool=False, use_regex: bool=False) -> list[dict]

Returns a list of dicts: {"line": int, "text": str} for each line matching the keyword or regex.
By default the search is a case-sensitive substring search. You can enable case-insensitive
matching and/or regular-expression matching with the optional flags.
"""
from typing import List, Dict
import re


def search_in_file(path: str, keyword: str, case_insensitive: bool = False, use_regex: bool = False) -> List[Dict]:
    """Search for `keyword` in file at `path`.

    Args:
        path: Path to the file to search.
        keyword: Substring or regex pattern to search for in each line.
        case_insensitive: If True, performs case-insensitive matching.
        use_regex: If True, interpret `keyword` as a regular expression.

    Returns:
        A list of dicts with keys `line` (1-based line number) and `text` (the full line without trailing newline).

    Raises:
        FileNotFoundError: If the file does not exist.
        UnicodeDecodeError: If the file cannot be decoded with UTF-8.
        ValueError: If `use_regex` is True and the provided pattern is invalid.
    """
    matches = []

    if use_regex:
        flags = re.IGNORECASE if case_insensitive else 0
        try:
            pattern = re.compile(keyword, flags)
        except re.error as e:
            raise ValueError(f"invalid regex pattern: {e}")

        def _matches(line: str) -> bool:
            return bool(pattern.search(line))
    else:
        if case_insensitive:
            needle = keyword.lower()

            def _matches(line: str) -> bool:
                return needle in line.lower()
        else:
            def _matches(line: str) -> bool:
                return keyword in line

    with open(path, 'r', encoding='utf-8') as fh:
        for idx, raw_line in enumerate(fh, start=1):
            if _matches(raw_line):
                matches.append({'line': idx, 'text': raw_line.rstrip('\n')})

    return matches
