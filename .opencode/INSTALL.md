# Installation Guide for OpenCode

## Quick Install

Copy and paste this into OpenCode:

```
Install the remote-ssh tool from https://github.com/blizhan/remote-bash-tool
```

The AI will automatically:
1. Clone the repository
2. Copy the tool to the appropriate location
3. Verify the installation

## Manual Installation

### Step 1: Download the Repository

```bash
git clone https://github.com/blizhan/remote-bash-tool.git
cd remote-bash-tool
```

### Step 2: Install the Tool

```bash
# Copy to global tools directory
cp .opencode/tools/remote-bash.ts ~/.config/opencode/tools/remote-bash.ts

# Or for project-specific installation
mkdir -p .opencode/tools
cp .opencode/tools/remote-bash.ts .opencode/tools/remote-bash.ts
```

### Step 3: Verify Installation

Start OpenCode and run:

```
List available tools
```

You should see `remote-bash` in the list.

## Quick Download (without git)

```bash
curl -L https://github.com/blizhan/remote-bash-tool/archive/refs/heads/main.zip -o remote-bash-tool.zip
unzip remote-bash-tool.zip
cp remote-bash-tool-main/.opencode/tools/remote-bash.ts ~/.config/opencode/tools/remote-bash.ts
rm -rf remote-bash-tool.zip remote-bash-tool-main
```

## Using the Tool

Once installed, you can use it in OpenCode with a tool call:

```
Run remote-bash with host_alias=prod-db and command="uptime"
```

## Troubleshooting

**Tool not loading?**

1. Check the tool file exists:
   ```bash
   ls ~/.config/opencode/tools/remote-bash.ts
   ```

2. Restart OpenCode

**Still having issues?**

Open an issue at https://github.com/blizhan/remote-bash-tool/issues

## What's Included

The `.opencode/tools/` directory contains:
- `remote-bash.ts` - OpenCode tool definition (TypeScript)

## Uninstalling

```bash
rm -f ~/.config/opencode/tools/remote-bash.ts
```
