#!/usr/bin/env python3
"""
Chrome DevTools MCP Server - Entry Point

A Model Context Protocol server that provides Chrome DevTools Protocol integration
for debugging web applications during development.

This entry point initialises the server and imports all functionality from the
modular implementation in the src/ directory. The server enables Claude to
connect to Chrome browsers for comprehensive web application debugging.

Key Features:
- Browser automation and control
- Network request monitoring and analysis
- DOM inspection and manipulation
- Console log retrieval and filtering
- Performance metrics collection
- CSS computed styles analysis

The server uses the Chrome DevTools Protocol WebSocket interface to communicate
with Chrome instances running with remote debugging enabled.
"""

from __future__ import annotations

import os
import sys

# Ensure we can import from the local directory structure
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function and MCP server object from the modular implementation
from src import main
from src.main import mcp

# Export the MCP server object for MCP CLI detection and tooling
__all__ = ["mcp", "main"]


def main():
    """Entry point for the chrome-devtools-mcp script."""
    from src.main import main as run_server
    run_server()


if __name__ == "__main__":
    main()
