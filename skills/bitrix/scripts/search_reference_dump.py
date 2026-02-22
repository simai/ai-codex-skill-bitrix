#!/usr/bin/env python3
"""Search Bitrix knowledge dumps (json/jsonl/md/txt) with ranked snippets."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


TEXT_EXTENSIONS = {".md", ".txt"}
JSON_EXTENSIONS = {".json", ".jsonl"}


@dataclass
class Document:
    source: str
    content: str


@dataclass
class Match:
    source: str
    score: int
    snippet: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search external Bitrix docs dumps and return ranked matches."
    )
    parser.add_argument("--root", required=True, help="Root directory with docs dump.")
    parser.add_argument("--query", required=True, help="Search query.")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results to print. Default: 10",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=1,
        help="Minimum score threshold. Default: 1",
    )
    return parser.parse_args()


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def query_terms(query: str) -> list[str]:
    terms = [token for token in normalize(query).split(" ") if token]
    return sorted(set(terms))


def iter_documents(root: Path) -> Iterator[Document]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue

        suffix = path.suffix.lower()
        if suffix in TEXT_EXTENSIONS:
            content = read_text_safe(path)
            if content:
                yield Document(source=str(path), content=content)
            continue

        if suffix == ".json":
            yield from iter_json_documents(path)
            continue

        if suffix == ".jsonl":
            yield from iter_jsonl_documents(path)


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def iter_json_documents(path: Path) -> Iterator[Document]:
    raw = read_text_safe(path)
    if not raw:
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return

    if isinstance(data, dict):
        # Known format in Bitrix dumps: {"<doc-path>": {"content": "..."}}
        for key, value in data.items():
            if isinstance(value, dict) and isinstance(value.get("content"), str):
                source = f"{path}::{key}"
                yield Document(source=source, content=value["content"])
        return

    if isinstance(data, list):
        for index, item in enumerate(data):
            content = extract_json_text(item)
            if content:
                source = f"{path}::[{index}]"
                yield Document(source=source, content=content)


def iter_jsonl_documents(path: Path) -> Iterator[Document]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for index, line in enumerate(handle):
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                content = extract_json_text(item)
                if content:
                    source = f"{path}::line:{index + 1}"
                    yield Document(source=source, content=content)
    except OSError:
        return


def extract_json_text(item: object) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        chunks: list[str] = []
        for key in ("content", "text", "body", "title", "description"):
            value = item.get(key)
            if isinstance(value, str):
                chunks.append(value)
        return "\n".join(chunks)
    return ""


def score_document(content: str, terms: list[str]) -> tuple[int, int]:
    normalized = normalize(content)
    if not normalized:
        return 0, -1

    score = 0
    first_pos = -1
    for term in terms:
        count = normalized.count(term)
        if count:
            score += count
            pos = normalized.find(term)
            if first_pos == -1 or (pos != -1 and pos < first_pos):
                first_pos = pos
    return score, first_pos


def build_snippet(content: str, first_pos: int, width: int = 240) -> str:
    compact = " ".join(content.split())
    if not compact:
        return ""
    if first_pos < 0:
        return compact[:width]
    start = max(0, first_pos - width // 3)
    end = min(len(compact), start + width)
    return compact[start:end]


def search(root: Path, terms: list[str], limit: int, min_score: int) -> list[Match]:
    results: list[Match] = []
    for doc in iter_documents(root):
        score, first_pos = score_document(doc.content, terms)
        if score < min_score:
            continue
        snippet = build_snippet(doc.content, first_pos)
        results.append(Match(source=doc.source, score=score, snippet=snippet))

    results.sort(key=lambda item: (-item.score, item.source))
    return results[:limit]


def print_results(matches: Iterable[Match]) -> None:
    for index, match in enumerate(matches, start=1):
        print(f"{index}. [{match.score}] {match.source}")
        print(f"   {match.snippet}")


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root path does not exist or is not a directory: {root}")

    terms = query_terms(args.query)
    if not terms:
        raise SystemExit("Query must contain at least one searchable term.")

    matches = search(root=root, terms=terms, limit=args.limit, min_score=args.min_score)
    print_results(matches)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
