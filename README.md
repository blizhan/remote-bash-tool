# remote-bash-tool

OpenCode 自定义工具：通过 SSH（读取 `~/.ssh/config`）在远程机器执行 bash 命令，基于 `asyncssh` 支持异步调用。

## 安装与依赖（uv）

```bash
uv venv
uv sync
```

## 使用方式

示例：在终端中直接执行（无需单独脚本文件）：

```bash
# 发布到包后（使用 uvx 直接运行）
uvx run remote-bash --host-alias prod-db --command "uptime"

# 在项目内（使用 uv）
uv run remote-bash --host-alias prod-db --command "uptime"

# 或者安装到环境后
remote-bash --host-alias prod-db --command "uptime"

# 如果想要 JSON 输出
remote-bash --host-alias prod-db --command "df -h" --json
```

也支持模块方式运行：

```bash
python -m remote_bash_tool --host-alias prod-db --command "uptime"
```

查看帮助：

```bash
remote-bash --help
```

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

## OpenCode 配置（可选）

1. 将工具模块挂载到 OpenCode（示例配置，参考 OpenCode 自定义工具指南进行调整）：

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

## CI 与发布到 PyPI

- CI：`.github/workflows/ci.yml` 会在 push/PR 时运行测试。
- 发布：`.github/workflows/publish.yml` 会在推送 `v*` 标签时构建并发布到 PyPI（使用 Trusted Publishing）。

发布步骤示例：

```bash
git tag v0.1.0
git push origin v0.1.0
```
