from __future__ import annotations

import argparse

from server import SimpleHTTPServer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple educational HTTP server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", default=8080, type=int, help="Port to listen on")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = SimpleHTTPServer(host=args.host, port=args.port)
    server.serve_forever()


if __name__ == "__main__":
    main()
