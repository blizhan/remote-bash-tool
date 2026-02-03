import { tool } from "@opencode-ai/plugin"

type RemoteBashArgs = {
  host_alias: string
  command: string
  timeout?: number
  stream_output?: boolean
}

type SpawnedProcess = {
  stdout: ReadableStream<Uint8Array> | null
  stderr: ReadableStream<Uint8Array> | null
  exited: Promise<number>
  exitCode: number | null
}

type BunRuntime = {
  spawn: (
    command: string[],
    options: { stdout: "pipe"; stderr: "pipe" }
  ) => SpawnedProcess
}

declare const Bun: BunRuntime

type StreamResult = {
  stdout: string
  stderr: string
  exitCode: number
}

const stripAnsi = (value: string): string =>
  value.replace(
    /[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nq-uy=><]/g,
    ""
  )

const writeChunk = (chunk: string, isErr: boolean): void => {
  if (isErr) {
    process.stderr.write(chunk)
  } else {
    process.stdout.write(chunk)
  }
}

const readStream = async (
  stream: ReadableStream<Uint8Array> | null,
  isErr: boolean,
  onChunk: (chunk: string, isErr: boolean) => void
): Promise<string> => {
  if (!stream) {
    return ""
  }
  const reader = stream.getReader()
  const decoder = new TextDecoder()
  let buffer = ""
  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }
    const chunk = stripAnsi(decoder.decode(value, { stream: true }))
    buffer += chunk
    onChunk(chunk, isErr)
  }
  return buffer
}

const runStreaming = async (
  command: string[],
  onChunk: (chunk: string, isErr: boolean) => void
): Promise<StreamResult> => {
  const proc = Bun.spawn(command, {
    stdout: "pipe",
    stderr: "pipe",
  })
  const [stdout, stderr] = await Promise.all([
    readStream(proc.stdout, false, onChunk),
    readStream(proc.stderr, true, onChunk),
    proc.exited,
  ]).then(([out, err]) => [out, err])
  return {
    stdout,
    stderr,
    exitCode: proc.exitCode ?? 0,
  }
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
  async execute(args: RemoteBashArgs): Promise<string> {
    const timeout = args.timeout ?? 10
    const streamOutput = args.stream_output ?? true
    const streamFlag = streamOutput ? "--stream-output" : "--no-stream-output"
    const command = [
      "uvx",
      "--from",
      "remote-bash-tool==0.2.0",
      "remote-bash",
      "--host-alias",
      args.host_alias,
      "--command",
      args.command,
      "--timeout",
      String(timeout),
      streamFlag,
    ]
    const result = await runStreaming(
      command,
      streamOutput ? writeChunk : () => {}
    )
    const stdout = result.stdout.trim()
    const stderr = result.stderr.trim()
    if (stdout) {
      return stdout
    }
    if (stderr) {
      return stderr
    }
    return ""
  },
})
