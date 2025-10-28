#!/usr/bin/env python3
"""
Simple validation script for Kuzu MCP configuration.

Run this to validate that Kuzu support is correctly integrated.
"""

import os
import sys

# Set environment for testing
os.environ['DATABASE_TYPE'] = 'kuzu'
os.environ['KUZU_DB'] = ':memory:'
os.environ['OPENAI_API_KEY'] = 'test-key-for-validation'

# Import MCP server components
from graphiti_mcp_server import (
    GraphitiConfig,
    KuzuConfig,
    create_graph_driver,
)


def test_kuzu_config():
    """Test KuzuConfig parsing."""
    print('✓ Testing KuzuConfig...')
    
    # Test default
    config = KuzuConfig()
    assert config.db == ':memory:', f'Expected :memory:, got {config.db}'
    print('  ✓ KuzuConfig default value')
    
    # Test from_env
    config = KuzuConfig.from_env()
    assert config.db == ':memory:', f'Expected :memory:, got {config.db}'
    print('  ✓ KuzuConfig.from_env()')
    
    # Test with custom path
    os.environ['KUZU_DB'] = './test.kuzu'
    config = KuzuConfig.from_env()
    assert config.db == './test.kuzu', f'Expected ./test.kuzu, got {config.db}'
    print('  ✓ KuzuConfig with custom path')
    
    # Reset
    os.environ['KUZU_DB'] = ':memory:'


def test_graphiti_config():
    """Test GraphitiConfig with Kuzu."""
    print('\n✓ Testing GraphitiConfig...')
    
    config = GraphitiConfig.from_env()
    assert config.database_type == 'kuzu', f'Expected kuzu, got {config.database_type}'
    assert config.kuzu.db == ':memory:', f'Expected :memory:, got {config.kuzu.db}'
    print('  ✓ GraphitiConfig.from_env() with DATABASE_TYPE=kuzu')


def test_driver_factory():
    """Test create_graph_driver factory."""
    print('\n✓ Testing create_graph_driver...')
    
    config = GraphitiConfig.from_env()
    driver = create_graph_driver(config)
    
    from graphiti_core.driver.kuzu_driver import KuzuDriver
    assert isinstance(driver, KuzuDriver), f'Expected KuzuDriver, got {type(driver)}'
    print('  ✓ create_graph_driver returns KuzuDriver')
    
    return driver


def test_cli_precedence():
    """Test CLI argument precedence over environment."""
    print('\n✓ Testing CLI precedence...')
    
    import argparse
    
    # Set env to neo4j
    os.environ['DATABASE_TYPE'] = 'neo4j'
    os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
    os.environ['NEO4J_USER'] = 'neo4j'
    os.environ['NEO4J_PASSWORD'] = 'password'
    
    # CLI overrides to kuzu
    args = argparse.Namespace(
        database_type='kuzu',
        group_id='test',
        use_custom_entities=False,
        destroy_graph=False,
        model=None,
        small_model=None,
        temperature=None,
    )
    
    config = GraphitiConfig.from_cli_and_env(args)
    assert config.database_type == 'kuzu', f'Expected kuzu, got {config.database_type}'
    print('  ✓ CLI --database-type=kuzu overrides env DATABASE_TYPE=neo4j')
    
    # Reset
    os.environ['DATABASE_TYPE'] = 'kuzu'


def main():
    """Run all validation tests."""
    print('=' * 60)
    print('Kuzu MCP Configuration Validation')
    print('=' * 60)
    
    try:
        test_kuzu_config()
        test_graphiti_config()
        driver = test_driver_factory()
        test_cli_precedence()
        
        print('\n' + '=' * 60)
        print('✓ All validation tests passed!')
        print('=' * 60)
        print('\nKuzu support is correctly integrated.')
        print('\nTo use Kuzu with the MCP server:')
        print('  export DATABASE_TYPE=kuzu')
        print('  export KUZU_DB=":memory:"  # or "./data/graphiti.kuzu"')
        print('  export OPENAI_API_KEY="your-key"')
        print('  python graphiti_mcp_server.py --transport stdio --database-type kuzu')
        
        return 0
        
    except AssertionError as e:
        print(f'\n✗ Validation failed: {e}')
        return 1
    except Exception as e:
        print(f'\n✗ Unexpected error: {e}')
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

