"""Run the private LECTOR service independently from the METAXIS process."""

from __future__ import annotations

import argparse
import os

from .server import serve


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="metaxis-lector")
    parser.add_argument("serve", nargs="?", default="serve")
    parser.add_argument("--host", default=os.environ.get("LECTOR_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("LECTOR_PORT", "4320")))
    args = parser.parse_args(argv)
    serve(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
