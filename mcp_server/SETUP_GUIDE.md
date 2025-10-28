# Complete Setup Guide: Graphiti MCP Server with Kuzu

This guide provides complete step-by-step instructions for setting up and using the Graphiti MCP server with Kuzu database.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Testing Your Setup](#testing-your-setup)
5. [Integrating with Cursor](#integrating-with-cursor)
6. [Integrating with Claude Desktop](#integrating-with-claude-desktop)
7. [Verifying It Works](#verifying-it-works)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

---

## Prerequisites

### Required

- **Python 3.10 or higher**
  ```bash
  python3 --version  # Should show 3.10+
  ```

- **uv package manager** (recommended)
  ```bash
  # Install uv
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Or with pip
  pip install uv
  
  # Verify installation
  uv --version
  ```

- **OpenAI API Key**
  - Get one from: https://platform.openai.com/api-keys

### Optional

- **Cursor IDE** or **Claude Desktop** (for MCP integration)

---

## Installation

### Step 1: Clone or Navigate to Graphiti Project

```bash
cd /home/a3zak/projects/graphiti
```

### Step 2: Install Dependencies

Install the MCP server with Kuzu support:

```bash
cd mcp_server
uv sync --extra kuzu
```

This will:
- Install all required dependencies
- Install the Kuzu graph database
- Set up the development environment

**Alternative (using pip):**
```bash
pip install graphiti-core[kuzu]
```

### Step 3: Verify Installation

```bash
# Check that uv can find the packages
uv pip list | grep -E "(graphiti|kuzu|mcp)"
```

You should see:
- `graphiti-core`
- `kuzu`
- `mcp`

---

## Configuration

### Step 1: Set Up Environment Variables

Create a `.env` file in `/home/a3zak/projects/graphiti/mcp_server/`:

```bash
cd /home/a3zak/projects/graphiti/mcp_server
nano .env
```

Add the following content:

```bash
# Required
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Database Configuration
DATABASE_TYPE=kuzu
KUZU_DB=./data/graphiti.kuzu

# Optional Settings
MODEL_NAME=gpt-4o-mini
SMALL_MODEL_NAME=gpt-4o-mini
LLM_TEMPERATURE=0.0
GRAPHITI_TELEMETRY_ENABLED=false
SEMAPHORE_LIMIT=10
```

**Important:** Replace `sk-your-actual-openai-api-key-here` with your real OpenAI API key!

### Step 2: Create Data Directory

```bash
cd /home/a3zak/projects/graphiti/mcp_server
mkdir -p data
```

This is where Kuzu will store your database files.

---

## Testing Your Setup

### Step 1: Run the Verification Script

```bash
cd /home/a3zak/projects/graphiti/mcp_server

# Set environment variables
export OPENAI_API_KEY="your-key-here"
export DATABASE_TYPE="kuzu"
export KUZU_DB=":memory:"

# Run the test script
python test_mcp_setup.py
```

This script will:
- ✓ Check all dependencies
- ✓ Verify environment configuration
- ✓ Test Kuzu driver creation
- ✓ Test Graphiti initialization
- ✓ Generate MCP configuration

### Step 2: Manual Server Test

Test starting the server manually:

```bash
cd /home/a3zak/projects/graphiti/mcp_server

# Set your API key
export OPENAI_API_KEY="your-key-here"

# Start server in stdio mode
uv run graphiti_mcp_server.py --transport stdio --database-type kuzu --group-id test

# You should see:
# INFO - Graphiti client initialized successfully with kuzu
# INFO - Starting MCP server with transport: stdio
```

Press `Ctrl+C` to stop the server.

If you see the success messages, your setup is working! 

---

## Integrating with Cursor

### Step 1: Find Your uv Binary Path

```bash
which uv
# Example output: /home/a3zak/.local/bin/uv
```

### Step 2: Open Cursor MCP Configuration

In Cursor:
1. Open Settings (Ctrl+,)
2. Search for "MCP"
3. Click "Edit in settings.json" or navigate to MCP configuration

Alternatively, edit directly:
```bash
# Linux/WSL
nano ~/.cursor/config/mcp.json

# macOS
nano ~/Library/Application\ Support/Cursor/User/globalStorage/settings.json
```

### Step 3: Add Graphiti MCP Configuration

Add this to your MCP configuration:

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
        "OPENAI_API_KEY": "sk-your-actual-openai-api-key-here",
        "MODEL_NAME": "gpt-4o-mini",
        "KUZU_DB": "/home/a3zak/projects/graphiti/mcp_server/data/graphiti.kuzu",
        "GRAPHITI_TELEMETRY_ENABLED": "false"
      }
    }
  }
}
```

**Important Updates:**
- Replace `sk-your-actual-openai-api-key-here` with your actual API key
- Verify the `uv` path matches your `which uv` output
- Use absolute paths for `KUZU_DB`

### Step 4: Restart Cursor

Close Cursor completely and reopen it to load the new configuration.

### Step 5: Verify MCP is Connected

In Cursor's chat panel, you should see MCP tools available. Look for:
- `add_memory`
- `search_memory_nodes`
- `search_memory_facts`
- `get_status`

---

## Integrating with Claude Desktop

### Step 1: Locate Claude Configuration File

```bash
# macOS
~/Library/Application Support/Claude/claude_desktop_config.json

# Windows
%APPDATA%\Claude\claude_desktop_config.json

# Linux (if available)
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Edit Configuration

```bash
# macOS example
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Step 3: Add Graphiti Configuration

Use the same configuration as for Cursor (see Step 3 above).

### Step 4: Restart Claude Desktop

Quit Claude Desktop completely and restart it.

---

## Verifying It Works

### Test 1: Check Server Status

In Cursor or Claude, send:

```
Can you check the status of the Graphiti memory server?
```

**Expected Response:**
```
The Graphiti MCP server is running and connected to kuzu.
```

### Test 2: Add Memory

```
Add this to my memory: "I'm working on the Graphiti project. It uses Kuzu as a lightweight embedded graph database that doesn't require Docker or a separate server."
```

**Expected Response:**
```
Episode queued for processing successfully.
```

### Test 3: Search Memory

```
What database am I using in my project?
```

**Expected Response:**
```
You're using Kuzu, a lightweight embedded graph database...
```

### Test 4: Verify Database Files

```bash
ls -la /home/a3zak/projects/graphiti/mcp_server/data/
```

You should see a `graphiti.kuzu/` directory with database files inside.

---

## Troubleshooting

### Issue: "Module 'mcp' not found"

**Solution:**
```bash
cd /home/a3zak/projects/graphiti/mcp_server
uv sync --extra kuzu
```

### Issue: "OPENAI_API_KEY must be set"

**Solution:**
1. Get API key from: https://platform.openai.com/api-keys
2. Add to MCP config under `"env"`
3. Restart your MCP client

### Issue: "uv command not found"

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify
which uv
```

### Issue: MCP Server Not Starting in Cursor

**Debug Steps:**

1. **Check Cursor logs:**
   - Open Output panel (Ctrl+Shift+U)
   - Look for MCP-related errors

2. **Test manually:**
   ```bash
   cd /home/a3zak/projects/graphiti/mcp_server
   export OPENAI_API_KEY="your-key"
   uv run graphiti_mcp_server.py --transport stdio --database-type kuzu
   ```

3. **Verify paths:**
   - Ensure `command` path points to your `uv` binary
   - Ensure `--directory` path is correct
   - Use absolute paths

4. **Check permissions:**
   ```bash
   chmod +x /home/a3zak/.local/bin/uv
   ```

### Issue: Database Files Growing Too Large

**Solution - Clean up old data:**
```bash
# Stop the MCP server first
rm -rf /home/a3zak/projects/graphiti/mcp_server/data/graphiti.kuzu

# Or use the clear_graph tool in your MCP client:
"Clear all data from the knowledge graph"
```

### Issue: Search Returns No Results

**Possible causes:**
1. Data not yet processed (async operation)
2. Wrong group_id
3. Search query too specific

**Solutions:**
- Wait a few seconds after adding data
- Verify group_id matches
- Try broader search terms

---

## Advanced Configuration

### Using In-Memory Mode (Development)

For testing/development where you don't need persistence:

```json
"env": {
  "KUZU_DB": ":memory:",
  ...
}
```

**Pros:** Faster, no disk usage  
**Cons:** Data lost on restart

### Using SSE Transport (HTTP)

For remote access or when stdio isn't supported:

```bash
# Start server with SSE
uv run graphiti_mcp_server.py --transport sse --port 8000 --database-type kuzu
```

**MCP Config:**
```json
{
  "mcpServers": {
    "graphiti-memory": {
      "transport": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### Multiple Graph Databases

Run multiple instances for different contexts:

**Work projects:**
```bash
uv run graphiti_mcp_server.py \
  --transport sse \
  --port 8000 \
  --database-type kuzu \
  --group-id work
```

**Personal projects:**
```bash
uv run graphiti_mcp_server.py \
  --transport sse \
  --port 8001 \
  --database-type kuzu \
  --group-id personal
```

### Custom LLM Models

Change the model in your MCP config:

```json
"env": {
  "MODEL_NAME": "gpt-4o",  # More powerful
  "SMALL_MODEL_NAME": "gpt-4o-mini",
  ...
}
```

### Adjusting Concurrency

If you hit rate limits:

```json
"env": {
  "SEMAPHORE_LIMIT": "5",  # Lower = fewer concurrent operations
  ...
}
```

---

## Next Steps

Now that your MCP server is running:

1. **Read the Advanced Usage Guide:**
   - See `ADVANCED_USAGE.md` for complex patterns
   - Learn about structured data and temporal queries

2. **Explore Available Tools:**
   - `add_memory` - Add information
   - `search_memory_nodes` - Find entities
   - `search_memory_facts` - Find relationships
   - `get_episodes` - Retrieve recent memories
   - `delete_episode` - Remove data
   - `clear_graph` - Reset everything

3. **Build Your Knowledge Graph:**
   - Add project documentation
   - Store meeting notes
   - Track decisions and context
   - Build a personal knowledge base

4. **Monitor Performance:**
   - Check database size: `du -sh data/graphiti.kuzu/`
   - Review logs for errors
   - Adjust concurrency if needed

---

## Support & Resources

- **Graphiti Documentation:** https://github.com/getzep/graphiti
- **MCP Documentation:** https://modelcontextprotocol.io
- **Research Paper:** https://arxiv.org/abs/2501.13956
- **Community:** https://discord.com/invite/W8Kw6bsgXQ

---

## Summary Checklist

- [ ] Installed Python 3.10+
- [ ] Installed uv package manager
- [ ] Installed Graphiti with Kuzu support
- [ ] Created `.env` file with API key
- [ ] Ran verification script successfully
- [ ] Added MCP configuration to Cursor/Claude
- [ ] Restarted MCP client
- [ ] Tested `get_status`
- [ ] Tested `add_memory`
- [ ] Tested `search_memory`
- [ ] Verified database files created

If all items are checked, you're ready to use Graphiti MCP! 🎉

