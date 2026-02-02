from __future__ import annotations

from typing import TypedDict

from remote_bash_tool.ssh import run_remote_command


class RemoteBashInput(TypedDict, total=False):
    host_alias: str
    command: str
    timeout: float
    stream_output: bool


class RemoteBashOutput(TypedDict):
    exit_status: int
    stdout: str
    stderr: str


TOOL_SPEC = {
    "name": "remote_bash",
    "description": (
        "Run a bash command on a remote host using ~/.ssh/config settings."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "host_alias": {
                "type": "string",
                "description": "Host alias from ~/.ssh/config.",
            },
            "command": {
                "type": "string",
                "description": "Bash command to run on the remote host.",
            },
            "timeout": {
                "type": "number",
                "description": "SSH connection timeout in seconds.",
                "default": 10,
            },
            "stream_output": {
                "type": "boolean",
                "description": "Stream stdout/stderr to local output as the command runs.",
                "default": True,
            },
        },
        "required": ["host_alias", "command"],
    },
}


async def run(payload: RemoteBashInput) -> RemoteBashOutput:
    result = await run_remote_command(
        payload["host_alias"],
        payload["command"],
        timeout=payload.get("timeout", 10.0),
        stream_output=payload.get("stream_output", True),
    )
    return {
        "exit_status": result.exit_status,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
