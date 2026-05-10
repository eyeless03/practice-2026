from __future__ import annotations

import mimetypes
import socket
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import unquote


CRLF = "\r\n"


@dataclass
class Request:
    method: str
    path: str
    version: str


@dataclass
class Response:
    status: int
    reason: str
    body: bytes
    content_type: str = "text/html; charset=utf-8"


class SimpleHTTPServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self.public_dir = Path(__file__).resolve().parent / "public"
        self.routes: dict[str, Callable[[], Response]] = {
            "/": lambda: self._html_file("index.html"),
            "/about": lambda: self._html_file("about.html"),
        }

    def serve_forever(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen()

            print(f"Server started on http://{self.host}:{self.port}")
            print("Press Ctrl+C to stop.")

            while True:
                client_socket, client_address = server_socket.accept()
                with client_socket:
                    self._handle_client(client_socket, client_address[0])

    def _handle_client(self, client_socket: socket.socket, client_ip: str) -> None:
        raw_request = client_socket.recv(4096)
        request = self._parse_request(raw_request)

        if request is None:
            response = self._plain_text(400, "Bad Request", "Bad Request")
            log_method = "-"
            log_path = "-"
        elif request.method != "GET":
            response = self._plain_text(405, "Method Not Allowed", "Method Not Allowed")
            log_method = request.method
            log_path = request.path
        else:
            response = self._route(request.path)
            log_method = request.method
            log_path = request.path

        client_socket.sendall(self._build_response(response))
        self._log(client_ip, log_method, log_path, response.status)

    def _parse_request(self, raw_request: bytes) -> Request | None:
        try:
            first_line = raw_request.decode("iso-8859-1").splitlines()[0]
            method, path, version = first_line.split()
        except (IndexError, ValueError, UnicodeDecodeError):
            return None

        return Request(method=method.upper(), path=path, version=version)

    def _route(self, raw_path: str) -> Response:
        path = unquote(raw_path.split("?", 1)[0])

        if path in self.routes:
            return self.routes[path]()

        if path.startswith("/static/"):
            relative_path = path.removeprefix("/static/")
            return self._static_file(relative_path)

        return self._html_file("404.html", status=404, reason="Not Found")

    def _html_file(self, filename: str, status: int = 200, reason: str = "OK") -> Response:
        file_path = self.public_dir / filename

        if not file_path.exists():
            return self._plain_text(500, "Internal Server Error", f"Missing file: {filename}")

        return Response(
            status=status,
            reason=reason,
            body=file_path.read_bytes(),
            content_type="text/html; charset=utf-8",
        )

    def _static_file(self, relative_path: str) -> Response:
        requested = (self.public_dir / relative_path).resolve()

        if not self._is_inside_public(requested) or not requested.is_file():
            return self._html_file("404.html", status=404, reason="Not Found")

        content_type, _ = mimetypes.guess_type(requested.name)
        return Response(
            status=200,
            reason="OK",
            body=requested.read_bytes(),
            content_type=content_type or "application/octet-stream",
        )

    def _is_inside_public(self, file_path: Path) -> bool:
        public_root = self.public_dir.resolve()
        return file_path == public_root or public_root in file_path.parents

    def _plain_text(self, status: int, reason: str, message: str) -> Response:
        return Response(
            status=status,
            reason=reason,
            body=message.encode("utf-8"),
            content_type="text/plain; charset=utf-8",
        )

    def _build_response(self, response: Response) -> bytes:
        headers = [
            f"HTTP/1.1 {response.status} {response.reason}",
            f"Content-Type: {response.content_type}",
            f"Content-Length: {len(response.body)}",
            "Connection: close",
            "",
            "",
        ]
        return CRLF.join(headers).encode("utf-8") + response.body

    def _log(self, client_ip: str, method: str, path: str, status: int) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{now} {client_ip} {method} {path} {status}")
