"""Simple command-line tarot ledger for recording readings.

Usage examples::

    python tarot_ledger.py add --question "What should I focus on this week?" \\
        --cards "The Fool, The Lovers, Ten of Cups" --spread "Three Card" --notes "Good energy"
    
    python tarot_ledger.py list --from 2024-01-01 --to 2024-12-31
    python tarot_ledger.py summary

Entries are stored in JSON so the file can be synced or inspected easily.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional

DEFAULT_LEDGER = Path("ledger.json")


@dataclass
class TarotEntry:
    """Represents a single tarot reading entry."""

    date: str
    question: str
    cards: List[str]
    spread: str
    notes: str

    @classmethod
    def from_payload(cls, payload: dict) -> "TarotEntry":
        return cls(
            date=payload["date"],
            question=payload["question"],
            cards=payload.get("cards", []),
            spread=payload.get("spread", ""),
            notes=payload.get("notes", ""),
        )


class TarotLedger:
    """Handles persistence and retrieval of tarot readings."""

    def __init__(self, path: Path = DEFAULT_LEDGER):
        self.path = path
        self._entries: List[TarotEntry] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self._entries = []
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            self._entries = [TarotEntry.from_payload(entry) for entry in payload]
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"Failed to load ledger {self.path}: {exc}") from exc

    def save(self) -> None:
        data = [asdict(entry) for entry in self._entries]
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_entry(self, entry: TarotEntry) -> None:
        self._entries.append(entry)
        self._entries.sort(key=lambda e: e.date)
        self.save()

    def entries(self) -> List[TarotEntry]:
        return list(self._entries)

    def entries_in_range(self, start: Optional[date], end: Optional[date]) -> Iterable[TarotEntry]:
        for entry in self._entries:
            entry_date = datetime.strptime(entry.date, "%Y-%m-%d").date()
            if start and entry_date < start:
                continue
            if end and entry_date > end:
                continue
            yield entry

    def card_frequency(self) -> Counter:
        counter: Counter = Counter()
        for entry in self._entries:
            counter.update(entry.cards)
        return counter


def parse_cards(raw_cards: str) -> List[str]:
    if not raw_cards:
        return []
    return [card.strip() for card in raw_cards.split(",") if card.strip()]


def parse_date(raw_date: Optional[str]) -> str:
    if not raw_date:
        return date.today().isoformat()
    try:
        parsed = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must be in YYYY-MM-DD format") from exc
    return parsed.isoformat()


def entry_from_args(args: argparse.Namespace) -> TarotEntry:
    return TarotEntry(
        date=parse_date(args.date),
        question=args.question,
        cards=parse_cards(args.cards),
        spread=args.spread,
        notes=args.notes or "",
    )


def add_command(args: argparse.Namespace) -> None:
    ledger = TarotLedger(Path(args.file))
    entry = entry_from_args(args)
    ledger.add_entry(entry)
    print(f"Added reading on {entry.date} with {len(entry.cards)} card(s). Saved to {ledger.path}.")


def list_command(args: argparse.Namespace) -> None:
    ledger = TarotLedger(Path(args.file))
    start = datetime.strptime(args.date_from, "%Y-%m-%d").date() if args.date_from else None
    end = datetime.strptime(args.date_to, "%Y-%m-%d").date() if args.date_to else None

    entries = list(ledger.entries_in_range(start, end))
    if not entries:
        print("No readings found for the specified range.")
        return

    for entry in entries:
        cards = ", ".join(entry.cards)
        print(f"[{entry.date}] {entry.spread or 'Spread'} - {entry.question}\n  Cards: {cards}\n  Notes: {entry.notes}\n")


def summary_command(args: argparse.Namespace) -> None:
    ledger = TarotLedger(Path(args.file))
    entries = ledger.entries()
    if not entries:
        print("No readings recorded yet.")
        return

    counter = ledger.card_frequency()
    common = counter.most_common(3)
    print(f"Total readings: {len(entries)}")
    if common:
        print("Most frequent cards:")
        for card, freq in common:
            print(f"  - {card}: {freq}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Command-line tarot ledger")
    parser.add_argument(
        "--file",
        default=str(DEFAULT_LEDGER),
        help="Path to the ledger JSON file (defaults to ledger.json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new tarot reading")
    add_parser.add_argument("--question", required=True, help="Question or focus of the reading")
    add_parser.add_argument("--cards", required=True, help="Comma-separated list of cards drawn")
    add_parser.add_argument("--spread", default="Three Card", help="Spread or layout used")
    add_parser.add_argument("--notes", default="", help="Any observations or insights")
    add_parser.add_argument("--date", help="Date of the reading in YYYY-MM-DD (defaults to today)")
    add_parser.set_defaults(func=add_command)

    list_parser = subparsers.add_parser("list", help="List readings, optionally filtered by date range")
    list_parser.add_argument("--from", dest="date_from", help="Start date YYYY-MM-DD")
    list_parser.add_argument("--to", dest="date_to", help="End date YYYY-MM-DD")
    list_parser.set_defaults(func=list_command)

    summary_parser = subparsers.add_parser("summary", help="Show a summary of readings")
    summary_parser.set_defaults(func=summary_command)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
