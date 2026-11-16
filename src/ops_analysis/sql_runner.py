from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

NAME_PATTERN = re.compile(r"^-- name: ([a-z0-9_]+)$", re.MULTILINE)


def parse_named_queries(sql_text: str) -> list[tuple[str, str]]:
    matches = list(NAME_PATTERN.finditer(sql_text))
    if not matches:
        raise ValueError("SQL file contains no '-- name:' query markers")
    queries: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(sql_text)
        block = sql_text[match.end() : end].strip()
        if not block.endswith(";"):
            raise ValueError(f"Query '{match.group(1)}' must end with a semicolon")
        queries.append((match.group(1), block[:-1].strip()))
    return queries


def run_queries(database: Path, sql_file: Path, output_dir: Path) -> dict[str, int]:
    queries = parse_named_queries(sql_file.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    row_counts: dict[str, int] = {}
    with sqlite3.connect(database) as connection:
        for name, query in queries:
            result = pd.read_sql_query(query, connection)
            result.to_csv(output_dir / f"{name}.csv", index=False)
            row_counts[name] = len(result)
    return row_counts
