from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

from remote_bash_tool import tool
from remote_bash_tool.ssh import connect_via_ssh_config, run_remote_command, _load_ssh_config


class FakeResult:
    def __init__(self, exit_status: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.exit_status = exit_status
        self.stdout = stdout
        self.stderr = stderr


class FakeStream:
    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    def __aiter__(self):
        async def generator():
            for line in self._lines:
                yield line

        return generator()

    async def read(self) -> str:
        return "".join(self._lines)


class FakeProcess:
    def __init__(self, stdout_lines: list[str], stderr_lines: list[str]) -> None:
        self.stdout = FakeStream(stdout_lines)
        self.stderr = FakeStream(stderr_lines)

    async def wait(self) -> FakeResult:
        return FakeResult(exit_status=0)


class FakeConnection:
    def __init__(self) -> None:
        self.closed = False
        self.ran_command = None

    async def create_process(self, command: str) -> FakeProcess:
        self.ran_command = command
        return FakeProcess([f"ran:{command}"], [])

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        return None


class RemoteBashToolTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.fake_connection = FakeConnection()
        self.connect_kwargs = None

        async def fake_connect(**kwargs):
            self.connect_kwargs = kwargs
            return self.fake_connection

        fake_asyncssh = types.SimpleNamespace(connect=fake_connect)
        sys.modules["asyncssh"] = fake_asyncssh

    def tearDown(self) -> None:
        sys.modules.pop("asyncssh", None)

    def test_load_ssh_config_reads_config(self) -> None:
        config_path = Path("/tmp/ssh_config_test")
        config_path.write_text(
            "\n".join(
                [
                    "Host demo",
                    "  HostName 10.0.0.1",
                    "  User ubuntu",
                    "  Port 2222",
                    "  IdentityFile ~/.ssh/id_demo",
                    "  ProxyCommand ssh -W %h:%p jump",
                ]
            ),
            encoding="utf-8",
        )
        try:
            config = _load_ssh_config(config_path, "demo")
        finally:
            config_path.unlink(missing_ok=True)

        self.assertEqual(config["hostname"], "10.0.0.1")
        self.assertEqual(config["user"], "ubuntu")
        self.assertEqual(config["port"], "2222")
        self.assertEqual(config["identityfile"], ["~/.ssh/id_demo"])
        self.assertEqual(config["proxycommand"], "ssh -W %h:%p jump")

    async def test_run_remote_command_async(self) -> None:
        module = sys.modules["remote_bash_tool.ssh"]
        original_loader = module._load_ssh_config
        module._load_ssh_config = lambda *_args, **_kwargs: {"hostname": "demo"}
        try:
            result = await run_remote_command("demo", "uptime", stream_output=False)
        finally:
            module._load_ssh_config = original_loader

        self.assertEqual(result.exit_status, 0)
        self.assertEqual(result.stdout, "ran:uptime")
        self.assertEqual(result.stderr, "")
        self.assertTrue(self.fake_connection.closed)

    async def test_tool_run_returns_payload(self) -> None:
        module = sys.modules["remote_bash_tool.ssh"]
        original_loader = module._load_ssh_config
        module._load_ssh_config = lambda *_args, **_kwargs: {"hostname": "demo"}
        try:
            output = await tool.run(
                {"host_alias": "demo", "command": "echo ok", "stream_output": False}
            )
        finally:
            module._load_ssh_config = original_loader

        self.assertEqual(
            output,
            {"exit_status": 0, "stdout": "ran:echo ok", "stderr": ""},
        )


if __name__ == "__main__":
    unittest.main()
