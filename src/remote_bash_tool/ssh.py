from __future__ import annotations

import asyncio
import fnmatch
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RemoteCommandResult:
    exit_status: int
    stdout: str
    stderr: str
    started_at: datetime
    finished_at: datetime


def _load_asyncssh():
    import asyncssh

    return asyncssh


def _load_ssh_config(ssh_config_path: Path, host_alias: str) -> dict[str, Any]:
    if not ssh_config_path.exists():
        raise FileNotFoundError(f"SSH config not found: {ssh_config_path}")
    config: dict[str, Any] = {}
    current_matches = False
    with ssh_config_path.open("r", encoding="utf-8") as config_file:
        for raw_line in config_file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower().startswith("host "):
                patterns = line.split()[1:]
                current_matches = any(
                    fnmatch.fnmatchcase(host_alias, pattern) for pattern in patterns
                )
                continue
            if not current_matches:
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            key, value = parts[0].lower(), parts[1].strip()
            if key == "identityfile":
                config.setdefault("identityfile", []).append(value)
            elif key not in config and key in (
                "hostname",
                "user",
                "port",
                "proxycommand",
            ):
                config[key] = value
    return config


async def connect_via_ssh_config(
    host_alias: str,
    *,
    ssh_config_path: Path | None = None,
    timeout: float = 10.0,
) -> Any:
    ssh_config_path = ssh_config_path or (Path.home() / ".ssh" / "config")
    config = _load_ssh_config(ssh_config_path, host_alias)
    asyncssh = _load_asyncssh()
    import re

    # Determine the actual host to connect to.
    # If 'hostname' is specified in the SSH config, use that.
    # Otherwise, use the provided host_alias, but validate it first for safety.
    _host = config.get("hostname")
    if _host is None:
        # Validate host_alias to prevent shell injection if it's used directly
        # as the host in ProxyCommand expansion.
        # Allow alphanumeric characters, hyphens, and dots.
        if not re.fullmatch(r"^[a-zA-Z0-9.-]+$", host_alias):
            raise ValueError(
                f"Untrusted host alias '{host_alias}' contains invalid characters. "
                "Only alphanumeric characters, hyphens, and dots are allowed."
            )
        _host = host_alias

    return await asyncssh.connect(
        host=_host,
        port=int(config.get("port", 22)),
        username=config.get("user"),
        client_keys=config.get("identityfile"),
        proxy_command=config.get("proxycommand"),
        connect_timeout=timeout,
    )


async def _stream_reader(reader: Any, sink, buffer: list[str]) -> None:
    async for line in reader:
        text = line.decode("utf-8") if isinstance(line, bytes) else str(line)
        buffer.append(text)
        sink.write(text)
        sink.flush()


async def run_remote_command(
    host_alias: str,
    command: str,
    *,
    timeout: float = 10.0,
    stream_output: bool = True,
) -> RemoteCommandResult:
    started_at = datetime.now(timezone.utc)
    connection = await connect_via_ssh_config(host_alias, timeout=timeout)
    try:
        process = await connection.create_process(command)
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []
        if stream_output:
            await asyncio.gather(
                _stream_reader(process.stdout, sys.stdout, stdout_lines),
                _stream_reader(process.stderr, sys.stderr, stderr_lines),
            )
        else:
            stdout_lines.append(await process.stdout.read())
            stderr_lines.append(await process.stderr.read())
        result = await process.wait()
    finally:
        connection.close()
        await connection.wait_closed()
    finished_at = datetime.now(timezone.utc)
    return RemoteCommandResult(
        exit_status=result.exit_status,
        stdout="".join(stdout_lines),
        stderr="".join(stderr_lines),
        started_at=started_at,
        finished_at=finished_at,
    )
