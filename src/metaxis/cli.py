"""METAXIS operator commands."""

from __future__ import annotations

import argparse
import os

from . import __version__


def _status() -> int:
    print(f"METAXIS {__version__}")
    print("phase: 0 — local application development")
    print("production inference: not activated")
    print("endpoint spending: not authorized")
    print("HIGH/NOFORN processing: blocked")
    print("approved development data: synthetic/public only")
    print("brain contract: provider-neutral scaffold")
    print("PROTOS-4 capabilities: 4 loaded; 2 active; writes denied")
    return 0


def _serve(host: str, port: int) -> int:
    from .server import serve

    serve(host=host, port=port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="metaxis")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="show honest Phase 0 posture")
    serve_parser = subparsers.add_parser("serve", help="run the local METAXIS service")
    serve_parser.add_argument(
        "--host", default=os.environ.get("METAXIS_HOST", "127.0.0.1")
    )
    serve_parser.add_argument(
        "--port", type=int, default=int(os.environ.get("METAXIS_PORT", "4310"))
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "status":
        return _status()
    if args.command == "serve":
        return _serve(args.host, args.port)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
