# Minimal MCP set for VoiceStudio (Cursor)

VoiceStudio is a **WinUI 3 desktop** app; it does not rely on MCPs for UI rendering.  
MCPs are optional tooling helpers. If “most MCPs show errors”, it usually means your `mcp.json`
contains servers that do not exist on npm (404) or require API keys.

## Recommended minimal set (stop error spam)

Keep only:

- `mcp-interactive` (simple interactive prompts inside Cursor)
- `GitKraken` (git/issue operations via the GitLens/GitKraken bridge)

Everything else should be added intentionally *only when you actually need it* and have the required credentials.

## Minimal `mcp.json` content (copy/paste)

```json
{
  "mcpServers": {
    "mcp-interactive": {
      "command": "mcp-interactive",
      "args": []
    },
    "GitKraken": {
      "env": {},
      "name": "GitKraken",
      "args": [
        "mcp",
        "--host=cursor",
        "--source=gitlens",
        "--scheme=cursor"
      ],
      "type": "stdio",
      "command": "c:\\\\Users\\\\Tyler\\\\AppData\\\\Roaming\\\\Cursor\\\\User\\\\globalStorage\\\\eamodio.gitlens\\\\gk.exe"
    }
  }
}
```

## What to do in Cursor

1. Open Cursor → **Settings** → search **“MCP”**.
2. Open your MCP config (`mcp.json`) and keep only the minimal block above.
3. Restart Cursor.

## Common error causes (what you saw in logs)

- **npm E404 Not Found**: the configured MCP package name doesn’t exist or is private.
- **Access token expired or revoked**: npm is trying to use a stale auth token (often from an old npm login or enterprise registry config).

