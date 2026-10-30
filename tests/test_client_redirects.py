"""Regression tests for authenticated HTTP redirects in the Dify API client."""

import json
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from figranium_client import FigraniumClient, FigraniumError


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class _Destination(_Handler):
    requests = []

    def do_GET(self):
        self._record()

    def do_POST(self):
        self._record()

    def _record(self):
        type(self).requests.append(dict(self.headers))
        body = json.dumps({"tasks": []}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class _Redirect(_Handler):
    destination = ""

    def do_GET(self):
        self._redirect()

    def do_POST(self):
        self._redirect()

    def _redirect(self):
        self.send_response(302)
        self.send_header("Location", type(self).destination)
        self.end_headers()


class _Success(_Handler):
    def do_GET(self):
        body = b'{"tasks":[]}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@contextmanager
def _server(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


class AuthenticatedRedirectTests(unittest.TestCase):
    def test_cross_origin_redirect_never_receives_api_key(self):
        for method in ("GET", "POST"):
            with self.subTest(method=method):
                _Destination.requests = []
                with _server(_Destination) as destination:
                    _Redirect.destination = destination + "/capture"
                    with _server(_Redirect) as origin:
                        client = FigraniumClient(origin, "private-api-key", 5)
                        with self.assertRaisesRegex(FigraniumError, "Redirects are blocked"):
                            if method == "GET":
                                client.list_tasks()
                            else:
                                client.execute_task("task-1", {})
                self.assertEqual(_Destination.requests, [])

    def test_non_redirected_requests_still_succeed(self):
        with _server(_Success) as origin:
            client = FigraniumClient(origin, "private-api-key", 5)
            self.assertEqual(client.list_tasks(), {"tasks": []})


if __name__ == "__main__":
    unittest.main()
