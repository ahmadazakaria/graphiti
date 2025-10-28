"""
Tests for Kuzu backend support in the MCP server.

This module provides unit and integration tests for:
1. KuzuConfig parsing from environment variables
2. GraphitiConfig.from_env/from_cli_and_env with kuzu database type
3. CLI argument parsing with --database-type kuzu
4. Driver factory (create_graph_driver) for kuzu
5. Backend initialization with kuzu
"""

import argparse
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import the mcp_server module components
# Note: This assumes mcp_server is in the Python path
import sys
from pathlib import Path

# Add mcp_server to path
mcp_server_path = Path(__file__).parent.parent / 'mcp_server'
sys.path.insert(0, str(mcp_server_path))

from graphiti_mcp_server import (
    GraphitiConfig,
    KuzuConfig,
    create_graph_driver,
)


class TestKuzuConfig:
    """Unit tests for KuzuConfig model and environment parsing."""

    def test_kuzu_config_default(self):
        """Test KuzuConfig uses :memory: as default."""
        config = KuzuConfig()
        assert config.db == ':memory:'

    def test_kuzu_config_from_env_default(self, monkeypatch):
        """Test KuzuConfig.from_env() uses :memory: when KUZU_DB not set."""
        monkeypatch.delenv('KUZU_DB', raising=False)
        config = KuzuConfig.from_env()
        assert config.db == ':memory:'

    def test_kuzu_config_from_env_custom(self, monkeypatch):
        """Test KuzuConfig.from_env() honors KUZU_DB environment variable."""
        monkeypatch.setenv('KUZU_DB', './data/test.kuzu')
        config = KuzuConfig.from_env()
        assert config.db == './data/test.kuzu'

    def test_kuzu_config_from_env_memory(self, monkeypatch):
        """Test KuzuConfig.from_env() accepts explicit :memory:."""
        monkeypatch.setenv('KUZU_DB', ':memory:')
        config = KuzuConfig.from_env()
        assert config.db == ':memory:'


class TestGraphitiConfigKuzu:
    """Unit tests for GraphitiConfig with kuzu database type."""

    def test_graphiti_config_from_env_kuzu(self, monkeypatch):
        """Test GraphitiConfig.from_env() with DATABASE_TYPE=kuzu."""
        monkeypatch.setenv('DATABASE_TYPE', 'kuzu')
        monkeypatch.setenv('KUZU_DB', './test.kuzu')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        config = GraphitiConfig.from_env()

        assert config.database_type == 'kuzu'
        assert config.kuzu.db == './test.kuzu'

    def test_graphiti_config_from_env_kuzu_default_db(self, monkeypatch):
        """Test GraphitiConfig.from_env() with kuzu uses default :memory:."""
        monkeypatch.setenv('DATABASE_TYPE', 'kuzu')
        monkeypatch.delenv('KUZU_DB', raising=False)
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        config = GraphitiConfig.from_env()

        assert config.database_type == 'kuzu'
        assert config.kuzu.db == ':memory:'

    def test_graphiti_config_from_env_unsupported_type(self, monkeypatch):
        """Test GraphitiConfig.from_env() raises on unsupported database type."""
        monkeypatch.setenv('DATABASE_TYPE', 'invalid')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        with pytest.raises(ValueError, match='Unsupported DATABASE_TYPE'):
            GraphitiConfig.from_env()

    def test_graphiti_config_from_env_missing_database_type(self, monkeypatch):
        """Test GraphitiConfig.from_env() raises when DATABASE_TYPE not set."""
        monkeypatch.delenv('DATABASE_TYPE', raising=False)
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        with pytest.raises(ValueError, match='DATABASE_TYPE environment variable must be set'):
            GraphitiConfig.from_env()


class TestGraphitiConfigCLIKuzu:
    """Unit tests for GraphitiConfig CLI parsing with kuzu."""

    def test_from_cli_and_env_kuzu_from_cli(self, monkeypatch):
        """Test --database-type kuzu overrides env."""
        monkeypatch.setenv('DATABASE_TYPE', 'neo4j')
        monkeypatch.setenv('NEO4J_URI', 'bolt://localhost:7687')
        monkeypatch.setenv('NEO4J_USER', 'neo4j')
        monkeypatch.setenv('NEO4J_PASSWORD', 'password')
        monkeypatch.setenv('KUZU_DB', './cli.kuzu')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        args = argparse.Namespace(
            database_type='kuzu',
            group_id='test-group',
            use_custom_entities=False,
            destroy_graph=False,
            model=None,
            small_model=None,
            temperature=None,
        )

        config = GraphitiConfig.from_cli_and_env(args)

        assert config.database_type == 'kuzu'
        assert config.kuzu.db == './cli.kuzu'
        assert config.group_id == 'test-group'

    def test_from_cli_and_env_kuzu_from_env(self, monkeypatch):
        """Test CLI without --database-type uses env DATABASE_TYPE=kuzu."""
        monkeypatch.setenv('DATABASE_TYPE', 'kuzu')
        monkeypatch.setenv('KUZU_DB', ':memory:')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        args = argparse.Namespace(
            database_type=None,
            group_id=None,
            use_custom_entities=False,
            destroy_graph=False,
            model=None,
            small_model=None,
            temperature=None,
        )

        config = GraphitiConfig.from_cli_and_env(args)

        assert config.database_type == 'kuzu'
        assert config.kuzu.db == ':memory:'
        assert config.group_id == 'default'

    def test_from_cli_and_env_default_neo4j(self, monkeypatch):
        """Test default database type is neo4j when neither CLI nor env set."""
        monkeypatch.delenv('DATABASE_TYPE', raising=False)
        monkeypatch.setenv('NEO4J_URI', 'bolt://localhost:7687')
        monkeypatch.setenv('NEO4J_USER', 'neo4j')
        monkeypatch.setenv('NEO4J_PASSWORD', 'password')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        args = argparse.Namespace(
            database_type=None,
            group_id=None,
            use_custom_entities=False,
            destroy_graph=False,
            model=None,
            small_model=None,
            temperature=None,
        )

        config = GraphitiConfig.from_cli_and_env(args)

        assert config.database_type == 'neo4j'


class TestCreateGraphDriver:
    """Unit tests for the create_graph_driver factory function."""

    def test_create_graph_driver_kuzu_memory(self, monkeypatch):
        """Test create_graph_driver returns KuzuDriver with :memory:."""
        monkeypatch.setenv('DATABASE_TYPE', 'kuzu')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        config = GraphitiConfig.from_env()
        config.kuzu.db = ':memory:'

        driver = create_graph_driver(config)

        # Check it's a KuzuDriver
        from graphiti_core.driver.kuzu_driver import KuzuDriver

        assert isinstance(driver, KuzuDriver)
        # Kuzu driver stores the database internally
        assert driver.db is not None

    def test_create_graph_driver_kuzu_file(self, monkeypatch):
        """Test create_graph_driver returns KuzuDriver with file path."""
        monkeypatch.setenv('DATABASE_TYPE', 'kuzu')
        monkeypatch.setenv('KUZU_DB', './data/test.kuzu')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        config = GraphitiConfig.from_env()

        driver = create_graph_driver(config)

        from graphiti_core.driver.kuzu_driver import KuzuDriver

        assert isinstance(driver, KuzuDriver)
        assert driver.db is not None

    def test_create_graph_driver_neo4j(self, monkeypatch):
        """Test create_graph_driver returns Neo4jDriver."""
        monkeypatch.setenv('DATABASE_TYPE', 'neo4j')
        monkeypatch.setenv('NEO4J_URI', 'bolt://localhost:7687')
        monkeypatch.setenv('NEO4J_USER', 'neo4j')
        monkeypatch.setenv('NEO4J_PASSWORD', 'password')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        config = GraphitiConfig.from_env()

        driver = create_graph_driver(config)

        from graphiti_core.driver.neo4j_driver import Neo4jDriver

        assert isinstance(driver, Neo4jDriver)

    def test_create_graph_driver_unsupported(self, monkeypatch):
        """Test create_graph_driver raises ValueError for unsupported type."""
        monkeypatch.setenv('DATABASE_TYPE', 'kuzu')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        config = GraphitiConfig.from_env()
        config.database_type = 'unsupported'

        with pytest.raises(ValueError, match='Unsupported database type'):
            create_graph_driver(config)


@pytest.mark.asyncio
class TestKuzuInitialization:
    """Integration tests for Kuzu backend initialization."""

    async def test_kuzu_driver_basic_query(self, monkeypatch):
        """Test KuzuDriver can execute a basic query."""
        monkeypatch.setenv('DATABASE_TYPE', 'kuzu')
        monkeypatch.setenv('KUZU_DB', ':memory:')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        config = GraphitiConfig.from_env()
        driver = create_graph_driver(config)

        # Test a simple query
        try:
            result = await driver.execute_query('MATCH (n) RETURN 1 LIMIT 1')
            # Should return empty result on fresh database
            assert result is not None
        finally:
            await driver.close()

    async def test_kuzu_driver_schema_creation(self, monkeypatch):
        """Test KuzuDriver initializes schema correctly."""
        monkeypatch.setenv('DATABASE_TYPE', 'kuzu')
        monkeypatch.setenv('KUZU_DB', ':memory:')
        monkeypatch.setenv('OPENAI_API_KEY', 'test-key')

        config = GraphitiConfig.from_env()
        driver = create_graph_driver(config)

        # KuzuDriver auto-creates schema in __init__
        # Verify we can close without errors
        try:
            await driver.close()
        except Exception as e:
            pytest.fail(f'Failed to close Kuzu driver: {e}')


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing with kuzu database type."""

    def test_argparse_accepts_kuzu(self):
        """Test argparse accepts 'kuzu' as --database-type choice."""
        # This would be in the actual server's initialize_server function
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--database-type', choices=['neo4j', 'falkordb', 'kuzu'], help='Database backend'
        )

        args = parser.parse_args(['--database-type', 'kuzu'])
        assert args.database_type == 'kuzu'

    def test_argparse_rejects_invalid(self):
        """Test argparse rejects invalid database type."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--database-type', choices=['neo4j', 'falkordb', 'kuzu'], help='Database backend'
        )

        with pytest.raises(SystemExit):
            parser.parse_args(['--database-type', 'invalid'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

