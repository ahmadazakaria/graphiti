# Graphiti MCP Quick Reference

## Installation

```bash
cd /home/a3zak/projects/graphiti/mcp_server
uv sync --extra kuzu
```

## Quick Start

```bash
# 1. Set environment
export OPENAI_API_KEY="your-key-here"

# 2. Test server
uv run graphiti_mcp_server.py --transport stdio --database-type kuzu

# 3. Run verification
python test_mcp_setup.py
```

## MCP Configuration (Copy/Paste)

```json
{
  "mcpServers": {
    "graphiti-memory": {
      "transport": "stdio",
      "command": "/home/a3zak/.local/bin/uv",
      "args": [
        "run",
        "--directory",
        "/home/a3zak/projects/graphiti/mcp_server",
        "--extra",
        "kuzu",
        "graphiti_mcp_server.py",
        "--transport",
        "stdio",
        "--database-type",
        "kuzu"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-XXX",
        "MODEL_NAME": "gpt-4o-mini",
        "KUZU_DB": "/home/a3zak/projects/graphiti/mcp_server/data/graphiti.kuzu",
        "GRAPHITI_TELEMETRY_ENABLED": "false"
      }
    }
  }
}
```

**Config locations:**
- Cursor: `~/.cursor/config/mcp.json`
- Claude: `~/Library/Application Support/Claude/claude_desktop_config.json`

## Common Commands (in Cursor/Claude)

```
# Status check
Check the Graphiti memory server status

# Add memory
Add to memory: "Your information here"

# Search
What do I know about [topic]?

# Clear
Clear all data from the knowledge graph
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | `uv sync --extra kuzu` |
| API key error | Set `OPENAI_API_KEY` in config |
| Server won't start | Check logs, verify paths |
| No search results | Wait a few seconds, data is processed async |

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...
DATABASE_TYPE=kuzu

# Optional
KUZU_DB=./data/graphiti.kuzu  # or :memory:
MODEL_NAME=gpt-4o-mini
GRAPHITI_TELEMETRY_ENABLED=false
```

## Useful Files

- `SETUP_GUIDE.md` - Complete installation guide
- `ADVANCED_USAGE.md` - Complex usage patterns
- `test_mcp_setup.py` - Verification script
- `KUZU_INTEGRATION.md` - Implementation details

## Database Management

```bash
# Check size
du -sh data/graphiti.kuzu/

# Backup
cp -r data/graphiti.kuzu data/backup-$(date +%Y%m%d)

# Clean up
rm -rf data/graphiti.kuzu  # Will recreate on next start
```

## Performance Tips

1. Use `:memory:` for development/testing
2. Lower `SEMAPHORE_LIMIT` if hitting rate limits
3. Use `group_id` to organize different contexts
4. Structured JSON for important data

