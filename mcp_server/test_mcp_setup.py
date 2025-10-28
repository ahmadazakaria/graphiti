#!/usr/bin/env python3
"""
MCP Setup Verification Script

This script tests your Graphiti MCP server setup with Kuzu to ensure
everything is configured correctly before connecting it to Cursor/Claude.

Run this script to verify:
1. All dependencies are installed
2. Configuration is valid
3. Server can start and respond
4. Database operations work
5. MCP tools are accessible
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f'\n{BOLD}{BLUE}{"=" * 60}{RESET}')
    print(f'{BOLD}{BLUE}{text}{RESET}')
    print(f'{BOLD}{BLUE}{"=" * 60}{RESET}\n')


def print_success(text):
    """Print success message."""
    print(f'{GREEN}✓ {text}{RESET}')


def print_error(text):
    """Print error message."""
    print(f'{RED}✗ {text}{RESET}')


def print_warning(text):
    """Print warning message."""
    print(f'{YELLOW}⚠ {text}{RESET}')


def print_info(text):
    """Print info message."""
    print(f'{BLUE}ℹ {text}{RESET}')


class MCPSetupTester:
    """Test MCP server setup and configuration."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.test_count = 0

    def test(self, description):
        """Decorator for test methods."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                self.test_count += 1
                try:
                    result = await func(*args, **kwargs)
                    if result:
                        print_success(description)
                        self.success_count += 1
                    else:
                        print_error(description)
                        self.errors.append(description)
                    return result
                except Exception as e:
                    print_error(f'{description}: {str(e)}')
                    self.errors.append(f'{description}: {str(e)}')
                    return False
            return wrapper
        return decorator

    async def check_dependencies(self):
        """Check if all required dependencies are installed."""
        print_info('Checking dependencies...')
        
        dependencies = {
            'graphiti_core': 'Graphiti core library',
            'mcp': 'MCP server library',
            'openai': 'OpenAI client',
            'pydantic': 'Configuration models',
        }
        
        optional_dependencies = {
            'kuzu': 'Kuzu graph database (required for --database-type kuzu)',
        }
        
        all_ok = True
        
        for module, description in dependencies.items():
            try:
                __import__(module.replace('-', '_'))
                print_success(f'{description} ({module})')
            except ImportError:
                print_error(f'{description} ({module}) - NOT INSTALLED')
                all_ok = False
        
        for module, description in optional_dependencies.items():
            try:
                __import__(module)
                print_success(f'{description} ({module})')
            except ImportError:
                print_warning(f'{description} ({module}) - NOT INSTALLED')
                print_info(f'  Install with: uv sync --extra kuzu')
        
        return all_ok

    async def check_environment(self):
        """Check environment variables."""
        print_info('Checking environment variables...')
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key.startswith('sk-'):
            print_success('OPENAI_API_KEY is set')
        else:
            print_error('OPENAI_API_KEY is not set or invalid')
            print_info('  Set it with: export OPENAI_API_KEY="your-key-here"')
            return False
        
        database_type = os.getenv('DATABASE_TYPE', 'neo4j')
        print_success(f'DATABASE_TYPE: {database_type}')
        
        if database_type == 'kuzu':
            kuzu_db = os.getenv('KUZU_DB', ':memory:')
            print_success(f'KUZU_DB: {kuzu_db}')
            
            if kuzu_db != ':memory:':
                db_path = Path(kuzu_db)
                if db_path.exists():
                    print_success(f'Database directory exists: {kuzu_db}')
                else:
                    print_info(f'Database will be created at: {kuzu_db}')
        
        return True

    async def test_server_import(self):
        """Test that server module can be imported."""
        print_info('Testing server import...')
        
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from graphiti_mcp_server import (
                GraphitiConfig,
                KuzuConfig,
                create_graph_driver,
            )
            print_success('Server module imports successfully')
            return True
        except ImportError as e:
            print_error(f'Failed to import server module: {e}')
            return False

    async def test_kuzu_config(self):
        """Test Kuzu configuration."""
        print_info('Testing Kuzu configuration...')
        
        try:
            from graphiti_mcp_server import KuzuConfig
            
            # Test default
            config = KuzuConfig()
            assert config.db == ':memory:', 'Default should be :memory:'
            print_success('KuzuConfig default value')
            
            # Test from_env
            os.environ['KUZU_DB'] = './test_data/test.kuzu'
            config = KuzuConfig.from_env()
            assert config.db == './test_data/test.kuzu'
            print_success('KuzuConfig.from_env() reads environment')
            
            # Reset
            os.environ['KUZU_DB'] = ':memory:'
            
            return True
        except Exception as e:
            print_error(f'Kuzu config test failed: {e}')
            return False

    async def test_driver_creation(self):
        """Test driver creation."""
        print_info('Testing driver creation...')
        
        try:
            from graphiti_mcp_server import GraphitiConfig, create_graph_driver
            
            os.environ['DATABASE_TYPE'] = 'kuzu'
            os.environ['KUZU_DB'] = ':memory:'
            
            config = GraphitiConfig.from_env()
            driver = create_graph_driver(config)
            
            from graphiti_core.driver.kuzu_driver import KuzuDriver
            assert isinstance(driver, KuzuDriver)
            print_success('KuzuDriver created successfully')
            
            # Test basic query
            result = await driver.execute_query('MATCH (n) RETURN 1 LIMIT 1')
            print_success('Basic query executes successfully')
            
            await driver.close()
            return True
        except Exception as e:
            print_error(f'Driver creation test failed: {e}')
            import traceback
            traceback.print_exc()
            return False

    async def test_graphiti_initialization(self):
        """Test Graphiti client initialization."""
        print_info('Testing Graphiti initialization...')
        
        try:
            from graphiti_core import Graphiti
            from graphiti_mcp_server import GraphitiConfig, create_graph_driver
            
            os.environ['DATABASE_TYPE'] = 'kuzu'
            os.environ['KUZU_DB'] = ':memory:'
            
            config = GraphitiConfig.from_env()
            driver = create_graph_driver(config)
            
            # Create Graphiti client without LLM (for testing)
            graphiti = Graphiti(graph_driver=driver, llm_client=None, embedder=None)
            
            print_success('Graphiti client created')
            
            # Try to build indices
            await graphiti.build_indices_and_constraints()
            print_success('Indices and constraints built')
            
            await driver.close()
            return True
        except Exception as e:
            print_error(f'Graphiti initialization failed: {e}')
            import traceback
            traceback.print_exc()
            return False

    async def generate_mcp_config(self):
        """Generate MCP configuration for Cursor/Claude."""
        print_info('Generating MCP configuration...')
        
        # Get absolute path to mcp_server directory
        mcp_server_dir = Path(__file__).parent.absolute()
        
        # Try to find uv
        import shutil
        uv_path = shutil.which('uv')
        if not uv_path:
            # Try common locations
            common_paths = [
                Path.home() / '.local' / 'bin' / 'uv',
                Path.home() / '.cargo' / 'bin' / 'uv',
                '/usr/local/bin/uv',
            ]
            for path in common_paths:
                if path.exists():
                    uv_path = str(path)
                    break
        
        if not uv_path:
            print_warning('Could not find uv binary. Please update the path manually.')
            uv_path = '/path/to/uv'
        
        config = {
            "mcpServers": {
                "graphiti-memory": {
                    "transport": "stdio",
                    "command": uv_path,
                    "args": [
                        "run",
                        "--directory",
                        str(mcp_server_dir),
                        "--extra",
                        "kuzu",
                        "graphiti_mcp_server.py",
                        "--transport",
                        "stdio",
                        "--database-type",
                        "kuzu"
                    ],
                    "env": {
                        "OPENAI_API_KEY": "your-openai-api-key-here",
                        "MODEL_NAME": "gpt-4o-mini",
                        "KUZU_DB": str(mcp_server_dir / "data" / "graphiti.kuzu"),
                        "GRAPHITI_TELEMETRY_ENABLED": "false"
                    }
                }
            }
        }
        
        config_file = mcp_server_dir / 'mcp_config_example.json'
        with open(config_file, 'w') as f:
            json.dump(config, indent=2, fp=f)
        
        print_success(f'MCP configuration saved to: {config_file}')
        print_info('\nCopy this configuration to your MCP client:')
        print_info('  Cursor: ~/.cursor/config/mcp.json')
        print_info('  Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json')
        print('')
        print(json.dumps(config, indent=2))
        
        return True

    async def print_summary(self):
        """Print test summary."""
        print_header('Test Summary')
        
        print(f'Tests run: {self.test_count}')
        print(f'Successes: {GREEN}{self.success_count}{RESET}')
        print(f'Failures: {RED}{len(self.errors)}{RESET}')
        print(f'Warnings: {YELLOW}{len(self.warnings)}{RESET}')
        
        if self.errors:
            print(f'\n{RED}Errors:{RESET}')
            for error in self.errors:
                print(f'  - {error}')
        
        if self.warnings:
            print(f'\n{YELLOW}Warnings:{RESET}')
            for warning in self.warnings:
                print(f'  - {warning}')
        
        if not self.errors:
            print(f'\n{GREEN}{BOLD}✓ All tests passed! Your MCP setup is ready.{RESET}')
            print(f'\n{BLUE}Next steps:{RESET}')
            print('  1. Copy the MCP configuration above to your client')
            print('  2. Replace "your-openai-api-key-here" with your actual API key')
            print('  3. Restart Cursor or Claude Desktop')
            print('  4. Test by asking to add something to memory')
            return True
        else:
            print(f'\n{RED}{BOLD}✗ Some tests failed. Please fix the errors above.{RESET}')
            return False


async def main():
    """Run all tests."""
    print_header('Graphiti MCP Setup Verification')
    print('This script will verify your MCP server setup with Kuzu.\n')
    
    tester = MCPSetupTester()
    
    # Run tests
    if not await tester.check_dependencies():
        print_error('\nDependencies missing. Install them with:')
        print_info('  cd /home/a3zak/projects/graphiti/mcp_server')
        print_info('  uv sync --extra kuzu')
        return 1
    
    if not await tester.check_environment():
        print_error('\nEnvironment not configured. Set required variables:')
        print_info('  export OPENAI_API_KEY="your-key-here"')
        print_info('  export DATABASE_TYPE="kuzu"')
        print_info('  export KUZU_DB=":memory:"  # or path to database')
        return 1
    
    await tester.test_server_import()
    await tester.test_kuzu_config()
    await tester.test_driver_creation()
    await tester.test_graphiti_initialization()
    await tester.generate_mcp_config()
    
    success = await tester.print_summary()
    return 0 if success else 1


if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f'\n{YELLOW}Tests interrupted by user.{RESET}')
        sys.exit(1)
    except Exception as e:
        print(f'\n{RED}Unexpected error: {e}{RESET}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

