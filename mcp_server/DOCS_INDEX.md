# Graphiti MCP with Kuzu - Complete Documentation

Welcome! This directory contains everything you need to use Graphiti MCP server with Kuzu.

## 📚 Documentation Index

### Getting Started

1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ⭐ START HERE
   - Quick installation commands
   - Copy/paste MCP configuration
   - Common commands and troubleshooting

2. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** 📖 COMPLETE GUIDE
   - Step-by-step installation
   - Cursor integration
   - Claude Desktop integration
   - Troubleshooting section

3. **[test_mcp_setup.py](test_mcp_setup.py)** ✅ VERIFICATION
   - Automated setup verification
   - Dependency checks
   - Configuration validation

### Advanced Usage

4. **[ADVANCED_USAGE.md](ADVANCED_USAGE.md)** 🚀 POWER USER
   - Complex usage patterns
   - Structured data examples
   - Temporal queries
   - Multi-project organization

5. **[KUZU_INTEGRATION.md](KUZU_INTEGRATION.md)** 🔧 TECHNICAL
   - Implementation details
   - Architecture and design patterns
   - Testing information

6. **[README.md](README.md)** 📋 OFFICIAL DOCS
   - MCP server documentation
   - All database backends (Neo4j, FalkorDB, Kuzu)
   - Docker deployment

## 🚀 Quick Start (5 Minutes)

### 1. Install

```bash
cd /home/a3zak/projects/graphiti/mcp_server
uv sync --extra kuzu
```

### 2. Verify Setup

```bash
export OPENAI_API_KEY="your-key-here"
python test_mcp_setup.py
```

### 3. Configure MCP Client

Copy this to your Cursor MCP config (`~/.cursor/config/mcp.json`):

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
        "OPENAI_API_KEY": "sk-your-key-here",
        "MODEL_NAME": "gpt-4o-mini",
        "KUZU_DB": "/home/a3zak/projects/graphiti/mcp_server/data/graphiti.kuzu"
      }
    }
  }
}
```

### 4. Restart Cursor and Test

```
Check the Graphiti memory server status
```

**Success!** You're now using Graphiti MCP with Kuzu! 🎉

## 💡 Why Kuzu?

- ✅ **Zero setup** - No Docker, no separate server
- ✅ **In-memory mode** - Perfect for dev/test
- ✅ **Lightweight** - Minimal resource usage
- ✅ **Fast** - Direct in-process access
- ✅ **Local** - Database files in your project

## 📖 Documentation Paths

### If you're new to MCP:
1. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. Follow [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. Run `test_mcp_setup.py`
4. Try examples in [ADVANCED_USAGE.md](ADVANCED_USAGE.md)

### If you're migrating from Neo4j:
1. Check [KUZU_INTEGRATION.md](KUZU_INTEGRATION.md) for differences
2. Update your MCP config to use `--database-type kuzu`
3. Set `KUZU_DB` environment variable
4. Restart your MCP client

### If you want to contribute:
1. Read [KUZU_INTEGRATION.md](KUZU_INTEGRATION.md) for architecture
2. Check `tests/test_mcp_kuzu.py` for test patterns
3. Follow the design patterns (Strategy, Factory, DI)

## 🛠️ Key Files

| File | Purpose |
|------|---------|
| `graphiti_mcp_server.py` | Main MCP server implementation |
| `test_mcp_setup.py` | Setup verification script |
| `pyproject.toml` | Dependencies (includes kuzu extra) |
| `SETUP_GUIDE.md` | Complete installation guide |
| `ADVANCED_USAGE.md` | Complex usage examples |
| `KUZU_INTEGRATION.md` | Technical implementation docs |

## 🔧 Common Tasks

### Run Verification Tests
```bash
python test_mcp_setup.py
```

### Start Server Manually
```bash
export OPENAI_API_KEY="your-key"
uv run graphiti_mcp_server.py --transport stdio --database-type kuzu
```

### Check Database Size
```bash
du -sh data/graphiti.kuzu/
```

### Clear Database
```bash
rm -rf data/graphiti.kuzu
# Or use the MCP tool: "Clear all data from the knowledge graph"
```

### Switch to In-Memory Mode
In your MCP config, change:
```json
"KUZU_DB": ":memory:"
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | `uv sync --extra kuzu` |
| API key missing | Set in MCP config under `env` |
| Server won't start | Check paths in config, run manual test |
| Search no results | Data processed async, wait a few seconds |

See [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting) for detailed troubleshooting.

## 📝 Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...        # Your OpenAI API key
DATABASE_TYPE=kuzu            # Use Kuzu backend

# Optional
KUZU_DB=./data/graphiti.kuzu # Database path (default: :memory:)
MODEL_NAME=gpt-4o-mini        # LLM model (default: gpt-4.1-mini)
SEMAPHORE_LIMIT=10            # Concurrency limit
GRAPHITI_TELEMETRY_ENABLED=false  # Disable telemetry
```

## 🎯 Next Steps

After setup:

1. **Build Your Knowledge Graph**
   - Add project documentation
   - Store meeting notes  
   - Track decisions and context

2. **Explore Advanced Features**
   - Temporal queries
   - Structured data
   - Multi-project organization

3. **Integrate into Workflow**
   - Daily standups → memory
   - Code reviews → memory
   - Learning → memory

## 🌟 Features

- **Temporal Knowledge Graphs** - Track how information evolves
- **Semantic Search** - Natural language queries
- **Structured Data** - JSON support with auto-extraction
- **Multi-Project** - Organize with group_ids
- **Persistent Memory** - Database survives restarts
- **Low Latency** - Sub-second queries

## 📚 Additional Resources

- **Research Paper:** https://arxiv.org/abs/2501.13956
- **Main Repo:** https://github.com/getzep/graphiti
- **MCP Protocol:** https://modelcontextprotocol.io
- **Discord:** https://discord.com/invite/W8Kw6bsgXQ

## ✅ Checklist

Before asking for help, verify:

- [ ] Ran `uv sync --extra kuzu`
- [ ] Set `OPENAI_API_KEY` in config
- [ ] Ran `test_mcp_setup.py` successfully
- [ ] Restarted MCP client after config change
- [ ] Checked paths are absolute in config
- [ ] Verified `uv` path with `which uv`

## 🤝 Support

If you encounter issues:

1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting)
2. Run `test_mcp_setup.py` for diagnostics
3. Check logs in Cursor output panel
4. Ask on Discord: https://discord.com/invite/W8Kw6bsgXQ

---

**Happy knowledge graphing! 🎉**

