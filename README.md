# remote-bash-tool

OpenCode 自定义工具：通过 SSH（读取 `~/.ssh/config`）在远程机器执行 bash 命令，基于 `asyncssh` 支持异步调用。

## 安装与依赖（uv）

```bash
uv venv
uv sync
```

## 使用方式

示例：在 Python 代码中直接调用工具方法。

```python
import asyncio

from remote_bash_tool.tool import run


async def main() -> None:
    result = await run(
        {"host_alias": "prod-db", "command": "uptime", "stream_output": True}
    )
    print(result["stdout"])


asyncio.run(main())
```

## OpenCode 安装与配置

1. 安装 OpenCode（按你的环境选择一种方式）：

   ```bash
   uv tool install opencode
   # 或者
   pipx install opencode
   ```

2. 将工具模块挂载到 OpenCode（示例配置，参考 OpenCode 自定义工具指南进行调整）：

   ```yaml
   tools:
     - name: remote_bash
       module: remote_bash_tool.tool
       entrypoint: run
   ```

3. 在 OpenCode 中调用工具：

   ```json
   {
     "host_alias": "prod-db",
     "command": "df -h",
     "timeout": 10,
     "stream_output": true
   }
   ```
