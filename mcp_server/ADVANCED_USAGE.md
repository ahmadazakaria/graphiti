# Advanced MCP Usage Examples

This guide shows advanced usage patterns for the Graphiti MCP server with Kuzu.

## Table of Contents

1. [Basic Memory Operations](#basic-memory-operations)
2. [Structured Data Management](#structured-data-management)
3. [Temporal Queries](#temporal-queries)
4. [Multi-Project Organization](#multi-project-organization)
5. [Search & Retrieval Patterns](#search--retrieval-patterns)
6. [Integration Patterns](#integration-patterns)

---

## Basic Memory Operations

### Adding Simple Facts

```
Add to memory: "I prefer using VSCode with the Vim extension for coding."
```

### Adding Context-Rich Information

```
Add this to memory with source "meeting notes":
"In today's standup, we decided to migrate from Neo4j to Kuzu for our development environment because it's lighter weight and doesn't require Docker. John will handle the migration, Sarah will update the docs."
```

### Searching Memory

```
What do I remember about my code editor preferences?
```

```
Search my memory for information about database migrations.
```

---

## Structured Data Management

### Adding JSON Data

The MCP server can process structured JSON and automatically extract entities and relationships:

```
Add this customer data to memory:
{
  "customer": {
    "name": "Acme Corp",
    "industry": "Technology",
    "size": "Enterprise",
    "contact": {
      "name": "Jane Smith",
      "role": "CTO",
      "email": "jane@acme.com"
    }
  },
  "products": [
    {"id": "P001", "name": "CloudSync", "status": "active"},
    {"id": "P002", "name": "DataMiner", "status": "trial"}
  ],
  "last_interaction": "2025-01-15",
  "notes": "Interested in enterprise plan, needs SAML SSO"
}
```

### Tracking Project Requirements

```
Add this requirement to memory for project "GraphitiMCP":
{
  "requirement": {
    "id": "REQ-001",
    "title": "Kuzu Database Integration",
    "description": "Integrate Kuzu as a lightweight embedded graph database alternative",
    "priority": "high",
    "status": "completed",
    "assignee": "Development Team"
  },
  "dependencies": ["REQ-000: Core MCP Server"],
  "acceptance_criteria": [
    "KuzuDriver implementation",
    "Configuration support",
    "Documentation complete"
  ]
}
```

---

## Temporal Queries

Graphiti maintains temporal metadata for all facts, allowing you to track how information evolves over time.

### Adding Time-Sensitive Information

```
Add to memory: "As of today, our production database is Neo4j. We're evaluating Kuzu for development environments."
```

Later:
```
Add to memory: "We've successfully migrated our development environment to Kuzu. The setup is much simpler - no Docker required!"
```

### Searching Temporal Facts

```
What was our database strategy before the migration?
```

```
Show me the evolution of our database decisions.
```

---

## Multi-Project Organization

Use `group_id` to organize memories by project or context.

### Setting Up Multiple Contexts

When configuring MCP, you can specify different group IDs:

```json
{
  "mcpServers": {
    "graphiti-work": {
      "transport": "stdio",
      "command": "/home/user/.local/bin/uv",
      "args": [
        "run",
        "--directory", "/home/user/projects/graphiti/mcp_server",
        "--extra", "kuzu",
        "graphiti_mcp_server.py",
        "--transport", "stdio",
        "--database-type", "kuzu",
        "--group-id", "work-projects"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "KUZU_DB": "./data/work.kuzu"
      }
    },
    "graphiti-personal": {
      "transport": "stdio",
      "command": "/home/user/.local/bin/uv",
      "args": [
        "run",
        "--directory", "/home/user/projects/graphiti/mcp_server",
        "--extra", "kuzu",
        "graphiti_mcp_server.py",
        "--transport", "stdio",
        "--database-type", "kuzu",
        "--group-id", "personal"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "KUZU_DB": "./data/personal.kuzu"
      }
    }
  }
}
```

### Using Group-Based Queries

```
@graphiti-work Add to work memory: "Sprint planning is every Monday at 10am."
```

```
@graphiti-personal Add to personal memory: "Gym sessions on Tuesday, Thursday, Saturday."
```

---

## Search & Retrieval Patterns

### Entity-Based Search

```
Find all entities related to "Kuzu database".
```

### Fact-Based Search

```
What facts do we have about database performance?
```

### Node Search with Filtering

```
Search for all "Requirement" entities in the knowledge graph.
```

### Center Node Reranking

When you have a specific entity, you can use it to rerank results:

```
Find information about databases, focusing on what's related to the Kuzu entity.
```

---

## Integration Patterns

### Daily Standup Integration

```
Add today's standup notes to memory:
{
  "meeting": "Daily Standup",
  "date": "2025-10-28",
  "attendees": ["Alice", "Bob", "Carol"],
  "updates": [
    {
      "person": "Alice",
      "completed": "Finished Kuzu integration tests",
      "working_on": "Documentation updates",
      "blockers": "None"
    },
    {
      "person": "Bob",
      "completed": "Code review for MCP server",
      "working_on": "Performance benchmarks",
      "blockers": "Waiting for test data"
    }
  ],
  "action_items": [
    "Alice: Complete docs by EOD",
    "Bob: Share benchmark results by Wednesday"
  ]
}
```

### Knowledge Base Building

```
Add this technical concept to our knowledge base:
{
  "concept": "Graph Database",
  "definition": "A database that uses graph structures with nodes, edges, and properties to represent and store data",
  "examples": ["Neo4j", "Kuzu", "Amazon Neptune"],
  "use_cases": [
    "Knowledge graphs",
    "Social networks",
    "Recommendation engines",
    "Fraud detection"
  ],
  "related_concepts": ["Cypher query language", "Property graphs", "RDF"]
}
```

### Code Review Memory

```
Add code review notes to memory:
{
  "pr": "feat: Add Kuzu support to MCP server",
  "reviewer": "Senior Dev",
  "date": "2025-10-28",
  "feedback": [
    "Great use of factory pattern for driver selection",
    "Tests are comprehensive",
    "Documentation is clear"
  ],
  "suggestions": [
    "Consider adding performance benchmarks",
    "Add comparison table in main README"
  ],
  "status": "approved"
}
```

---

## Advanced Configuration Patterns

### In-Memory Mode (Development)

Perfect for testing and development - data is lost when server restarts:

```bash
export KUZU_DB=":memory:"
```

### Persistent Mode (Production)

Data is saved to disk and persists across restarts:

```bash
export KUZU_DB="./data/graphiti.kuzu"
```

### Multiple Databases

Run multiple MCP servers with different databases:

```bash
# Development database
export KUZU_DB="./data/dev.kuzu"
uv run graphiti_mcp_server.py --transport sse --port 8000 --group-id dev

# Production database (different terminal)
export KUZU_DB="./data/prod.kuzu"
uv run graphiti_mcp_server.py --transport sse --port 8001 --group-id prod
```

---

## Tips & Best Practices

### 1. Use Descriptive Names

When adding episodes, use descriptive names:

```
# Bad
Add to memory: "Update"

# Good
Add to memory with name "Q4 Planning - Database Migration Decision":
"We decided to use Kuzu for development environments..."
```

### 2. Structure Important Data

For critical information, use JSON format:

```
Add this structured data about our production incident:
{
  "incident": {
    "id": "INC-2025-001",
    "severity": "high",
    "component": "Database",
    "description": "Connection pool exhausted",
    "resolution": "Increased pool size from 20 to 50",
    "root_cause": "Traffic spike from new feature launch"
  }
}
```

### 3. Use Group IDs for Organization

Separate different contexts:
- `dev` - Development work
- `prod` - Production issues
- `meetings` - Meeting notes
- `learning` - Technical learning

### 4. Regular Searches

Use search to refresh your memory:

```
What are the open action items from this week's meetings?
```

### 5. Clean Up Old Data

```
Delete episode with UUID: abc-123-def-456
```

---

## Troubleshooting Advanced Usage

### Memory Not Persisting

Check your `KUZU_DB` setting:
```bash
echo $KUZU_DB
# Should show a file path, not :memory:
```

### Search Not Finding Results

Try different search terms or use node search:

```
Search nodes for "database"
# vs
Search facts for "database migration"
```

### JSON Parsing Errors

Ensure JSON is properly escaped when passing through MCP:

```json
{
  "name": "value with \"quotes\"",
  "nested": {"key": "value"}
}
```

---

## Next Steps

- Explore the [MCP Tools Reference](https://github.com/getzep/graphiti/blob/main/mcp_server/README.md#available-tools)
- Read about [Temporal Knowledge Graphs](https://arxiv.org/abs/2501.13956)
- Check out the [Graphiti Core Documentation](https://github.com/getzep/graphiti)

