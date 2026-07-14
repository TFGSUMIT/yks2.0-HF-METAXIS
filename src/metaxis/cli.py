"""Minimal operator readback for the METAXIS research scaffold."""

from __future__ import annotations

import argparse

from . import __version__


def _status() -> int:
    print(f"METAXIS {__version__}")
    print("phase: 0 — Hugging Face research/discovery")
    print("production inference: not activated")
    print("endpoint spending: not authorized")
    print("brain contract: provider-neutral scaffold")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="metaxis")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="show honest Phase 0 posture")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "status":
        return _status()
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

