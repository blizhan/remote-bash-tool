from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any

from remote_bash_tool.tool import run


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="remote-bash",
        description="Run a bash command on a remote host using ~/.ssh/config.",
    )
    parser.add_argument("--host-alias", required=True, help="Host alias in ~/.ssh/config.")
    parser.add_argument("--command", required=True, help="Bash command to run.")
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="SSH connection timeout in seconds.",
    )
    parser.add_argument(
        "--stream-output",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Stream stdout/stderr to local output while running.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full result as JSON.",
    )
    return parser


async def _run_from_args(args: argparse.Namespace) -> int:
    result = await run(
        {
            "host_alias": args.host_alias,
            "command": args.command,
            "timeout": args.timeout,
            "stream_output": args.stream_output,
        }
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
        return result["exit_status"]
    if result["stdout"]:
        print(result["stdout"])
    if result["stderr"]:
        print(result["stderr"])
    return result["exit_status"]


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return asyncio.run(_run_from_args(args))


if __name__ == "__main__":
    raise SystemExit(main())
