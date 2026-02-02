import { tool } from "@opencode-ai/plugin"

type RemoteBashArgs = {
  host_alias: string
  command: string
  timeout?: number
  stream_output?: boolean
}

type RemoteBashResult = {
  exit_status: number
  stdout: string
  stderr: string
}

export default tool({
  description: "Run a bash command on a remote host via SSH (~/.ssh/config).",
  args: {
    host_alias: tool.schema.string().describe("Host alias from ~/.ssh/config."),
    command: tool.schema.string().describe("Bash command to run."),
    timeout: tool.schema.number().optional().describe("SSH timeout in seconds."),
    stream_output: tool.schema
      .boolean()
      .optional()
      .describe("Stream stdout/stderr while running."),
  },
  async execute(
    args: RemoteBashArgs
  ): Promise<RemoteBashResult | { error: string; raw: string }> {
    const timeout = args.timeout ?? 10
    const streamOutput = args.stream_output ?? true
    const streamFlag = streamOutput ? "--stream-output" : "--no-stream-output"
    const output =
      await Bun.$`uvx --from remote-bash-tool remote-bash --host-alias ${args.host_alias} --command ${args.command} --timeout ${timeout} ${streamFlag} --json`.text()

    try {
      return JSON.parse(output) as RemoteBashResult
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : "Failed to parse JSON output.",
        raw: output,
      }
    }
  },
})
