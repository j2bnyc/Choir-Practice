# MCP Configuration

## Workspace Config (`.kiro/settings/mcp.json`)

Tracked in git. Contains shared MCP servers that all devs use (git, philips-hue, ollama). These point to shared infrastructure on the local network.

## User Config (`~/.kiro/settings/mcp.json`)

NOT tracked. Contains personal credentials and machine-specific servers (hass-mcp, postgres-hank, github, brave-search, etc.). Each dev creates their own.

The network-detect hook toggles network-dependent user-level servers automatically. See `scripts/kiro-network-aware.sh`.
