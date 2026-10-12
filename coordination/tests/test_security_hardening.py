"""
Automated Security & Hardening Tests (P0)
Verifies path containment, DNS rebinding defenses, CORS removal,
defensive security headers, 413 payload quotas, and loopback defaults.
"""

import unittest
import socket
import threading
import urllib.request
import urllib.error
import urllib.parse
import json
import time
import tempfile
from pathlib import Path
from coordination.coordination_ui import is_safe_contained_path, ApiHandler, UI_DIR, HERE, scan_tab, scan_project


class TestPathContainmentHelper(unittest.TestCase):

    def setUp(self):
        self.root = HERE.resolve()

    def test_contained_path_allowed(self):
        child = self.root / "ui" / "index.html"
        self.assertTrue(is_safe_contained_path(child, self.root))

    def test_traversal_parent_rejected(self):
        escaped = self.root / ".." / "AGENTS.md"
        self.assertFalse(is_safe_contained_path(escaped, self.root))

    def test_double_traversal_rejected(self):
        escaped = self.root / ".." / ".." / "Windows"
        self.assertFalse(is_safe_contained_path(escaped, self.root))

    def test_prefix_trick_rejected(self):
        # A directory with same prefix name but not inside root
        fake_neighbor = Path(str(self.root) + "_fake") / "secret.txt"
        self.assertFalse(is_safe_contained_path(fake_neighbor, self.root))


class TestSecurityHttpServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start a test server on loopback with ephemeral port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        cls.port = sock.getsockname()[1]
        sock.close()

        import socketserver
        class TestBoundHandler(ApiHandler):
            pass
        TestBoundHandler.config = {
            "projects": [
                {
                    "id": "common",
                    "name": "Common",
                    "coordination_dir": str(HERE),
                    "repo_url": "https://github.com/reallakshman19/Common"
                }
            ],
            "server": {
                "max_file_read_bytes": 1024,  # Small 1 KB quota to test 413
                "allowed_origins": ["https://trusted.internal"]
            }
        }
        TestBoundHandler.server_host = "127.0.0.1"

        socketserver.TCPServer.allow_reuse_address = True
        cls.httpd = socketserver.TCPServer(("127.0.0.1", cls.port), TestBoundHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_no_wildcard_cors(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/status")
        with urllib.request.urlopen(req) as resp:
            headers = dict(resp.headers)
            self.assertNotIn("Access-Control-Allow-Origin", headers)
            self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(headers.get("X-Frame-Options"), "DENY")
            self.assertIn("Content-Security-Policy", headers)

    def test_even_configured_origin_cannot_read_local_files_cross_origin(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/status")
        req.add_header("Origin", "https://trusted.internal")
        with urllib.request.urlopen(req) as resp:
            headers = dict(resp.headers)
            self.assertNotIn("Access-Control-Allow-Origin", headers)

    def test_untrusted_cors_origin_not_reflected(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/status")
        req.add_header("Origin", "https://evil-attacker.com")
        with urllib.request.urlopen(req) as resp:
            headers = dict(resp.headers)
            self.assertNotIn("Access-Control-Allow-Origin", headers)

    def test_dns_rebinding_host_header_blocked(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/status")
        req.add_header("Host", "attacker-rebinding.com")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)

    def test_api_file_path_traversal_blocked(self):
        # Attempt traversal to parent
        url = f"http://127.0.0.1:{self.port}/api/file?project=common&path=../../AGENTS.md"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url)
        self.assertEqual(ctx.exception.code, 403)

    def test_ui_path_traversal_blocked(self):
        # Attempt traversal via /ui/ route
        url = f"http://127.0.0.1:{self.port}/ui/../../coordination_ui.py"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url)
        self.assertEqual(ctx.exception.code, 403)

    def test_tab_path_escape_is_forbidden(self):
        for value in ("..", "../..", "../outside", "anything/../../"):
            url = (f"http://127.0.0.1:{self.port}/api/tab?project=common"
                   f"&session={urllib.parse.quote(value)}&tab=Tab1")
            with self.subTest(value=value):
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(url)
                self.assertEqual(ctx.exception.code, 403)

    def test_decoded_null_byte_file_path_rejected(self):
        url = f"http://127.0.0.1:{self.port}/api/file?project=common&path=%00abc"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url)
        self.assertEqual(ctx.exception.code, 400)

    def test_non_loopback_is_refused_even_with_override(self):
        from coordination.coordination_ui import run_server
        for flag in (False, True):
            with self.subTest(flag=flag):
                with self.assertRaises(SystemExit) as ctx:
                    run_server(self.httpd.RequestHandlerClass.config, self.port,
                               host="0.0.0.0", open_browser=False,
                               allow_remote_unauthenticated=flag)
                self.assertEqual(ctx.exception.code, 1)

    def test_read_quota_exceeded_returns_413(self):
        # The test server set max_file_read_bytes = 1024 (1 KB)
        # README.md is ~7 KB, so it must return 413 TOO_LARGE
        url = f"http://127.0.0.1:{self.port}/api/file?project=common&path=README.md"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url)
        self.assertEqual(ctx.exception.code, 413)
        body = json.loads(ctx.exception.read().decode())
        self.assertEqual(body.get("code"), "TOO_LARGE")

    def test_api_v3_snapshot_returns_valid_snapshot(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/v3/snapshot")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertEqual(data.get("visibility"), "INTERNAL")  # PUBLIC remains blocked until WP4 privacy allowlist
            self.assertIn("projects", data)
            self.assertIn("source_watermarks", data)



class TestScannerPathAndQuota(unittest.TestCase):

    def test_known_document_symlink_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / "project"
            tab = root / "Session_One" / "Tab1"
            tab.mkdir(parents=True)
            outside = Path(base) / "private.txt"
            outside.write_text("2026-01-01 | private | D-1-1 | SECRET", encoding="utf-8")
            try:
                (tab / "DECISIONS.md").symlink_to(outside)
            except OSError as e:
                if getattr(e, "winerror", None) == 1314:
                    self.skipTest("Symlink creation requires elevated privileges on Windows")
                raise
            result = scan_tab(root, "Session_One", "Tab1")
            self.assertEqual(result["decisions"], [])
            self.assertIn({"file": "DECISIONS.md", "code": "OUTSIDE_PROJECT"},
                          result["scan_warnings"])

    def test_oversized_receipt_visible_without_reading_payload(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            tab = root / "Session_One" / "Tab1"
            tab.mkdir(parents=True)
            (tab / "huge.json").write_bytes(b"x" * (1024 * 1024 + 8))
            result = scan_tab(root, "Session_One", "Tab1")
            receipt = next(r for r in result["json_receipts"] if r["filename"] == "huge.json")
            self.assertEqual(receipt["parse_status"], "TOO_LARGE")
            self.assertIsNone(receipt["data"])
            self.assertIn({"file": "huge.json", "code": "RECEIPT_TOO_LARGE"},
                          result["scan_warnings"])

    def test_external_session_symlink_not_scanned(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / "project"
            root.mkdir()
            outside = Path(base) / "Session_Outside"
            (outside / "Tab1").mkdir(parents=True)
            try:
                (root / "Session_Outside").symlink_to(outside, target_is_directory=True)
            except OSError as e:
                if getattr(e, "winerror", None) == 1314:
                    self.skipTest("Symlink creation requires elevated privileges on Windows")
                raise
            result = scan_project({"id": "fixture", "name": "fixture",
                                   "coordination_dir": str(root)})
            self.assertEqual(result["sessions"], [])

    def test_external_handover_symlink_not_scanned(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base) / "project"
            tab = root / "Session_One" / "Tab1"
            tab.mkdir(parents=True)
            outside = Path(base) / "private_handovers"
            outside.mkdir()
            (outside / "secret.md").write_text("private evidence", encoding="utf-8")
            try:
                (tab / "handovers").symlink_to(outside, target_is_directory=True)
            except OSError as e:
                if getattr(e, "winerror", None) == 1314:
                    self.skipTest("Symlink creation requires elevated privileges on Windows")
                raise
            result = scan_tab(root, "Session_One", "Tab1")
            self.assertEqual(result["handovers"], [])


if __name__ == "__main__":
    unittest.main()
