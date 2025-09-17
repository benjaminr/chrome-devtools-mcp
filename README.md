# Chrome DevTools MCP

A Model Context Protocol (MCP) server that provides Chrome DevTools Protocol integration through MCP. This allows you to debug web applications by connecting to Chrome's developer tools.

**Available as a Claude Desktop Extension (.dxt)** for easy one-click installation!

## What This Does

This MCP server acts as a bridge between Claude and Chrome's debugging capabilities. Once installed in Claude Desktop, you can:
- Connect Claude to any web application running in Chrome
- Debug network requests, console errors, and performance issues
- Inspect JavaScript objects and execute code in the browser context
- Monitor your application in real-time through natural conversation with Claude

**Note**: This is an MCP server that runs within Claude Desktop - you don't need to run any separate servers or processes.

## Features

- **Network Monitoring**: Capture and analyse HTTP requests/responses with filtering options
- **Console Integration**: Read browser console logs, analyse errors, and execute JavaScript
- **Performance Metrics**: Timing data, resource loading, and memory utilisation
- **Page Inspection**: DOM information, page metrics, and multi-frame support
- **Storage Access**: Read cookies, localStorage, and sessionStorage
- **Real-time Monitoring**: Live console output tracking
- **Object Inspection**: Inspect JavaScript objects and variables

## Installation

### Option 1: Claude Desktop Extension (Easiest)

**Download the pre-built extension:**
1. Download the latest `.dxt` file from [Releases](https://github.com/benjaminr/chrome-devtools-mcp/releases)
2. Open Claude Desktop
3. Go to Extensions and install the downloaded `.dxt` file
4. Configure Chrome path if needed in extension settings

The extension includes all dependencies and is ready to use immediately!

### Option 2: MCP CLI (Advanced)

**Quick Install (most common):**
```bash
git clone https://github.com/benjaminr/chrome-devtools-mcp.git
cd chrome-devtools-mcp
mcp install server.py -n "Chrome DevTools MCP" --with-editable .
```

> **Note**: The `mcp` command is part of the [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk). Install it with `pip install mcp` if not already available.

**All Installation Options:**

```bash
# Clone the repository
git clone https://github.com/benjaminr/chrome-devtools-mcp.git
cd chrome-devtools-mcp

# The --with-editable flag uses pyproject.toml to install dependencies

# Basic installation with local dependencies
mcp install server.py --with-editable .

# Install with custom name
mcp install server.py -n "Chrome DevTools MCP" --with-editable .

# Install with environment variables
mcp install server.py -n "Chrome DevTools MCP" --with-editable . -v CHROME_DEBUG_PORT=9222

# Install with additional packages if needed
mcp install server.py -n "Chrome DevTools MCP" --with-editable . --with websockets --with aiohttp

# Install with environment file (copy .env.example to .env first)
cp .env.example .env
# Edit .env with your settings
mcp install server.py -n "Chrome DevTools MCP" --with-editable . -f .env
```

### Option 3: Claude Code Integration

**For Claude Code CLI users:**

#### Quick Install (Easiest - no cloning required)

```bash
claude mcp add chrome-devtools-mcp -- uvx --from git+https://github.com/benjaminr/chrome-devtools-mcp chrome-devtools-mcp
```

This single command will:
- Install the server directly from GitHub
- Handle all dependencies automatically
- Configure it for use with Claude Code

#### Manual Install (if you want to modify the code)

1. **Clone this repository**
```bash
git clone https://github.com/benjaminr/chrome-devtools-mcp.git
cd chrome-devtools-mcp
```

2. **Install dependencies with UV (creates venv)**
```bash
uv sync  # Creates .venv and installs dependencies
```

3. **Add MCP server using Claude CLI with absolute paths**

**IMPORTANT**: Claude Code needs absolute paths to both the Python interpreter and the server script to work correctly.

**Recommended setup using absolute paths:**
```bash
# Get the absolute paths
SERVER_PATH="$(pwd)/server.py"
PYTHON_PATH="$(pwd)/.venv/bin/python"

# Add the server with absolute paths
claude mcp add chrome-devtools "$PYTHON_PATH" "$SERVER_PATH" -e CHROME_DEBUG_PORT=9222
```

**Alternative: Using the system Python (if dependencies are installed globally):**
```bash
# Only if you've installed dependencies globally
claude mcp add chrome-devtools python "$(pwd)/server.py" -e CHROME_DEBUG_PORT=9222
```

**With custom scope:**
```bash
# Add to user scope (available across all projects)
claude mcp add chrome-devtools "$(pwd)/.venv/bin/python" "$(pwd)/server.py" -s user -e CHROME_DEBUG_PORT=9222

# Add to project scope (only for this project)
claude mcp add chrome-devtools "$(pwd)/.venv/bin/python" "$(pwd)/server.py" -s project -e CHROME_DEBUG_PORT=9222
```

4. **Verify installation**
```bash
# List configured MCP servers
claude mcp list

# Get details about the server (check that paths are absolute)
claude mcp get chrome-devtools

# The output should show absolute paths like:
# Command: /Users/you/chrome-devtools-mcp/.venv/bin/python
# Args: ["/Users/you/chrome-devtools-mcp/server.py"]
```

**Common Path Issues and Solutions:**
- **Problem**: "python: command not found" or "server.py not found"
  - **Solution**: Use absolute paths as shown above
- **Problem**: "ModuleNotFoundError" when server starts
  - **Solution**: Use the venv Python interpreter that has dependencies installed
- **Problem**: Server doesn't start or shows as disconnected
  - **Solution**: Test the command manually: `/path/to/.venv/bin/python /path/to/server.py`

### Option 4: Manual Claude Desktop Setup

1. **Clone this repository**
```bash
git clone https://github.com/benjaminr/chrome-devtools-mcp.git
cd chrome-devtools-mcp
```

2. **Install dependencies**

**With uv (recommended):**
```bash
uv sync
```

**With pip:**
```bash
pip install -r requirements.txt
```

3. **Add to Claude Desktop configuration**

Edit your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "python",
      "args": ["/absolute/path/to/chrome-devtools-mcp/server.py"],
      "env": {
        "CHROME_DEBUG_PORT": "9222"
      }
    }
  }
}
```

4. **Restart Claude Desktop**

### Verify Installation

After installation (either method), verify the server is available:
1. Open Claude Desktop
2. Look for MCP tools in the conversation
3. Try a simple command: `get_connection_status()`

### Alternative MCP Clients

For other MCP clients, run the server directly:
```bash
# Using uvx (recommended - handles dependencies automatically)
uvx --from . chrome-devtools-mcp

# Or using Python directly
python server.py
```

## Quick Start

Once installed in Claude Desktop, you can start debugging any web application:

### Debug Your Web Application

**One-step setup (recommended):**
```
start_chrome_and_connect("localhost:3000")
```
*Replace `localhost:3000` with your application's URL*

**If Chrome isn't found automatically:**
```
start_chrome_and_connect("localhost:3000", chrome_path="/path/to/chrome")
```
*Use the `chrome_path` parameter to specify a custom Chrome location*

This command will:
- Start Chrome with debugging enabled
- Navigate to your application
- Connect the MCP server to Chrome

**Manual setup (if you prefer step-by-step):**
```
start_chrome()
navigate_to_url("localhost:3000")
connect_to_browser()
```

### Start Debugging

Once connected, use these commands:
- `get_network_requests()` - View HTTP traffic
- `get_console_error_summary()` - Analyse JavaScript errors  
- `inspect_console_object("window")` - Inspect any JavaScript object

## Available MCP Tools

### Chrome Management
- `start_chrome(port?, url?, headless?, chrome_path?, auto_connect?)` - Start Chrome with remote debugging and optional auto-connection
- `start_chrome_and_connect(url, port?, headless?, chrome_path?)` - Start Chrome, connect, and navigate in one step
- `connect_to_browser(port?)` - Connect to existing Chrome instance
- `navigate_to_url(url)` - Navigate to a specific URL
- `disconnect_from_browser()` - Disconnect from browser
- `get_connection_status()` - Check connection status

### Network Monitoring
- `get_network_requests(filter_domain?, filter_status?, limit?)` - Get network requests with filtering
- `get_network_response(request_id)` - Get detailed response data including body

### Console Tools
- `get_console_logs(level?, limit?)` - Get browser console logs
- `get_console_error_summary()` - Get organized summary of errors and warnings
- `execute_javascript(code)` - Execute JavaScript in browser context
- `clear_console()` - Clear the browser console
- `inspect_console_object(expression)` - Deep inspect any JavaScript object
- `monitor_console_live(duration_seconds)` - Monitor console output in real-time

### Page Analysis
- `get_page_info()` - Get comprehensive page metrics and performance data
- `evaluate_in_all_frames(code)` - Execute JavaScript in all frames/iframes
- `get_performance_metrics()` - Get detailed performance metrics and resource timing

### Storage & Data
- `get_storage_usage_and_quota(origin)` - Get storage usage and quota information
- `clear_storage_for_origin(origin, storage_types?)` - Clear storage by type and origin
- `get_all_cookies()` - Get all browser cookies
- `clear_all_cookies()` - Clear all browser cookies
- `set_cookie(name, value, domain, path?, expires?, http_only?, secure?, same_site?)` - Set a cookie
- `get_cookies(domain?)` - Get browser cookies with optional domain filtering
- `get_storage_key_for_frame(frame_id)` - Get storage key for a specific frame
- `track_cache_storage(origin, enable?)` - Enable/disable cache storage tracking
- `track_indexeddb(origin, enable?)` - Enable/disable IndexedDB tracking
- `override_storage_quota(origin, quota_size_mb?)` - Override storage quota

## Use Cases

### Debugging API Calls in Your Web Application

When your web application makes API calls that fail or return unexpected data:

**Easy setup:** Use the one-step command to start Chrome and navigate to your app:

**Example workflow:**
```
You: "I need to debug my React app at localhost:3000"
Claude: I'll start Chrome with debugging enabled and navigate to your app.

start_chrome_and_connect("localhost:3000")

Perfect! Chrome is now running with debugging enabled and connected to your app. Let me check for any failed network requests:

get_network_requests(filter_status=500)

I can see there are 3 failed requests to your API. Let me get the details of the first one:

get_network_response("request-123")
```

**Manual setup (if you prefer):**
1. **Start Chrome**: Use `start_chrome()` 
2. **Navigate to your app**: Use `navigate_to_url("localhost:3000")`
3. **Connect**: Use `connect_to_browser()`
4. **Monitor network traffic**: Use `get_network_requests()` to see all API calls

### Checking JavaScript Console Errors

When your web application has JavaScript errors or unexpected behaviour:

1. **Navigate to your application** in the connected Chrome instance
2. **Check for console errors**: Use `get_console_error_summary()` to see all errors
3. **Monitor live errors**: Use `monitor_console_live(10)` to watch for new errors as you interact
4. **Inspect variables**: Use `inspect_console_object("myVariable")` to examine application state

**Example workflow:**
```
You: "My React component isn't updating properly"
Claude: Let me check the JavaScript console for any errors.

get_console_error_summary()

I can see there are 2 JavaScript errors. Let me also monitor the console while you interact with the component:

monitor_console_live(15)

Now try clicking the component that isn't working. I'll watch for any new errors or warnings.
```

### Performance Debugging

When your web application loads slowly or uses too much memory:

1. **Load your application** in the connected browser
2. **Check page metrics**: Use `get_page_info()` to see load times and resource counts
3. **Analyse performance**: Use `get_performance_metrics()` to see detailed timing data
4. **Monitor memory usage**: Check the memory information in the performance metrics

**Example workflow:**
```
You: "My application takes too long to load"
Claude: Let me analyse the performance of your application.

get_page_info()

I can see your page has 47 scripts and took 3.2 seconds to load. Let me get more detailed performance data:

get_performance_metrics()

The main bottleneck is the initial JavaScript bundle which is 2.1MB. The DOM processing also takes 800ms.
```

### Debugging Authentication Issues

When login or session management isn't working:

1. **Navigate to your login page**
2. **Check cookies**: Use `get_cookies()` to see authentication cookies
3. **Monitor network during login**: Use `monitor_console_live()` and `get_network_requests()` during the login process
4. **Examine stored data**: Use JavaScript execution to check localStorage/sessionStorage

**Example workflow:**
```
You: "Users can't stay logged in"
Claude: Let me check the authentication setup.

get_cookies()

I can see the auth cookie is present. Let me check what happens during login by monitoring the network:

get_network_requests(filter_domain="your-api.com")

I notice the login request returns a 200 but no Set-Cookie header. Let me also check localStorage:

execute_javascript("Object.keys(localStorage)")
```

### DOM Element Inspection
- `get_document(depth?, pierce?)` - Retrieve DOM document structure
- `query_selector(node_id, selector)` - Find single element by CSS selector
- `query_selector_all(node_id, selector)` - Find multiple elements by CSS selector
- `get_element_attributes(node_id)` - Get all attributes of an element
- `get_element_outer_html(node_id)` - Get outer HTML of an element
- `get_element_box_model(node_id)` - Get layout information
- `describe_element(node_id, depth?)` - Get detailed element description
- `get_element_at_position(x, y)` - Get element at screen position
- `search_elements(query)` - Search DOM elements by text/attributes
- `focus_element(node_id)` - Focus a DOM element

### CSS Style Analysis
- `get_computed_styles(node_id)` - Get computed CSS styles
- `get_inline_styles(node_id)` - Get inline styles
- `get_matched_styles(node_id)` - Get all CSS rules matching an element
- `get_stylesheet_text(stylesheet_id)` - Get stylesheet content
- `get_background_colors(node_id)` - Get background colors and fonts
- `get_platform_fonts(node_id)` - Get platform font information
- `get_media_queries()` - Get all media queries
- `collect_css_class_names(stylesheet_id)` - Collect CSS class names
- `start_css_coverage_tracking()` - Start CSS coverage tracking
- `stop_css_coverage_tracking()` - Stop and get CSS coverage results

## Common Commands

| Task | Command |
|------|---------|
| Start Chrome and connect to app | `start_chrome_and_connect("localhost:3000")` |
| Start Chrome (manual setup) | `start_chrome()` |
| Navigate to page | `navigate_to_url("localhost:3000")` |
| Connect to browser | `connect_to_browser()` |
| See all network requests | `get_network_requests()` |
| Find failed API calls | `get_network_requests(filter_status=404)` |
| Check for JavaScript errors | `get_console_error_summary()` |
| Watch console in real-time | `monitor_console_live(10)` |
| Check page load performance | `get_page_info()` |
| Examine a variable | `inspect_console_object("window.myApp")` |
| View cookies | `get_cookies()` |
| Run JavaScript | `execute_javascript("document.title")` |

## Configuration

### Environment Variables
- `CHROME_DEBUG_PORT` - Chrome remote debugging port (default: 9222)

### MCP Compatibility
- **MCP Protocol Version**: 2024-11-05
- **Minimum Python Version**: 3.10+
- **Supported MCP Clients**: Claude Desktop, any MCP-compatible client
- **Package Manager**: uv (recommended) or pip

## Usage Workflow

### Prerequisites (Your Development Environment)
- Have your web application running (e.g., `npm run dev`, `python -m http.server`, etc.)
- Note the URL where your application is accessible

### Debugging Session
1. **Connect to your application** via Claude Desktop:
   ```
   start_chrome_and_connect("localhost:3000")
   ```
   *Replace with your application's URL*

2. **Debug your application** using the MCP tools:
   - Monitor network requests
   - Check console errors
   - Inspect JavaScript objects
   - Analyse performance

3. **Make changes to your code** in your editor
4. **Refresh or interact** with your application
5. **Continue debugging** with real-time data

### Manual Connection (Alternative)
If you prefer step-by-step control:
1. `start_chrome()` - Launch Chrome with debugging
2. `navigate_to_url("your-app-url")` - Navigate to your application
3. `connect_to_browser()` - Connect the MCP server
4. Use debugging tools as needed

## Security Notes

- Only use with development environments
- Never connect to production Chrome instances
- The server is designed for localhost debugging only
- No data is stored permanently - all data is session-based

## Troubleshooting

### Server Shows as "Disabled" in Claude Desktop

If the server appears in Claude but shows as "disabled", try these steps:

1. **Check Claude Desktop logs**:
   - **macOS**: `~/Library/Logs/Claude/mcp*.log`
   - **Windows**: `%APPDATA%/Claude/logs/mcp*.log`

2. **Common fixes**:
   ```bash
   # Reinstall with verbose output
   mcp remove "Chrome DevTools MCP"
   mcp install server.py -n "Chrome DevTools MCP" --with-editable . -v CHROME_DEBUG_PORT=9222
   
   # Check installation status
   mcp list
   
   # Test the server manually
   python3 server.py
   ```

3. **Check dependencies**:
   ```bash
   # Ensure all dependencies are available
   pip install mcp websockets aiohttp
   
   # Test imports
   python3 -c "from server import mcp; print('OK')"
   ```

4. **Restart Claude Desktop** completely (quit and reopen)

### Installation Issues
- **MCP CLI not found**: Install MCP CLI from the [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk) with `pip install mcp`
- **Server not appearing in Claude**: 
  - For MCP CLI: Run `mcp list` to verify the server is installed
  - For manual setup: Check Claude Desktop configuration file path and JSON syntax
- **Import errors**: 
  - For MCP CLI: Use `--with-editable .` to install local dependencies
  - For manual setup: Run `pip install -r requirements.txt`
- **Permission errors**: Use absolute paths in configuration
- **Environment variables not working**: Verify `.env` file format or `-v` flag syntax
- **Module not found**: Ensure you're using `--with-editable .` flag for local package installation

### Debugging Steps

**Step 1: Check MCP CLI Status**
```bash
# List all installed servers
mcp list

# Check specific server status
mcp status "Chrome DevTools MCP"
```

**Step 2: Test Server Manually**
```bash
# Test if server starts without errors
python3 server.py

# Test imports
python3 -c "from server import mcp; print(f'Server: {mcp.name}')"
```

**Step 3: Check Configuration**

**For Claude Desktop:**
```bash
# View current configuration (macOS)
cat "~/Library/Application Support/Claude/claude_desktop_config.json"

# View current configuration (Windows)
type "%APPDATA%/Claude/claude_desktop_config.json"
```

**For Claude Code:**
```bash
# List configured MCP servers
claude mcp list

# Get details about a specific server
claude mcp get chrome-devtools

# IMPORTANT: Verify paths are absolute, not relative
# Good example output:
#   Command: /Users/you/chrome-devtools-mcp/.venv/bin/python
#   Args: ["/Users/you/chrome-devtools-mcp/server.py"]
# Bad example output:
#   Command: python
#   Args: ["server.py"]

# Test the exact command Claude Code will use
/path/to/.venv/bin/python /path/to/server.py

# Check if server is working
claude mcp serve --help
```

**Step 3.5: Fix Path Issues (Claude Code specific)**
```bash
# If paths are relative, remove and re-add with absolute paths
claude mcp remove chrome-devtools

# Re-add with absolute paths
SERVER_PATH="$(pwd)/server.py"
PYTHON_PATH="$(pwd)/.venv/bin/python"
claude mcp add chrome-devtools "$PYTHON_PATH" "$SERVER_PATH" -e CHROME_DEBUG_PORT=9222
```

**Step 4: Reinstall if Needed**

**For MCP CLI:**
```bash
# Clean reinstall
mcp remove "Chrome DevTools MCP"
mcp install server.py -n "Chrome DevTools MCP" --with-editable .

# Restart Claude Desktop completely
```

**For Claude Code:**
```bash
# Remove and re-add the server
claude mcp remove chrome-devtools
claude mcp add chrome-devtools python server.py -e CHROME_DEBUG_PORT=9222

# Or update with different scope
claude mcp add chrome-devtools python server.py -s user -e CHROME_DEBUG_PORT=9222
```

### Common Error Messages

| Error | Solution |
|-------|----------|
| "Module not found" | Use `--with-editable .` flag |
| "No server object found" | Server should export `mcp` object (already fixed) |
| "Import error" | Check `pip install mcp websockets aiohttp` |
| "Permission denied" | Use absolute paths in config |
| "Server disabled" | Check Claude Desktop logs, restart Claude |
| "python: command not found" (Claude Code) | Use absolute path to venv Python: `/path/to/.venv/bin/python` |
| "server.py: No such file" (Claude Code) | Use absolute path to server: `/path/to/server.py` |
| "ModuleNotFoundError" (Claude Code) | Use venv Python that has dependencies installed |

### Manual Configuration Fallback

**For Claude Desktop:**
If MCP CLI isn't working, add this to Claude Desktop config manually:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "python3",
      "args": ["/absolute/path/to/chrome-devtools-mcp/server.py"],
      "env": {
        "CHROME_DEBUG_PORT": "9222"
      }
    }
  }
}
```

**For Claude Code:**
If the `claude mcp add` command isn't working, you can use the JSON format with absolute paths:

```bash
# Get absolute paths first
SERVER_PATH="$(pwd)/server.py"
PYTHON_PATH="$(pwd)/.venv/bin/python"

# Add server using JSON configuration with absolute paths
claude mcp add-json chrome-devtools "{
  \"command\": \"$PYTHON_PATH\",
  \"args\": [\"$SERVER_PATH\"],
  \"env\": {
    \"CHROME_DEBUG_PORT\": \"9222\"
  }
}"

# Or if you have it working in Claude Desktop, import from there
claude mcp add-from-claude-desktop
```

**Example of correct Claude Code configuration (with absolute paths):**
```json
{
  "command": "/Users/you/chrome-devtools-mcp/.venv/bin/python",
  "args": ["/Users/you/chrome-devtools-mcp/server.py"],
  "env": {
    "CHROME_DEBUG_PORT": "9222"
  }
}
```

### Connection Issues
- **Chrome won't start**: The MCP server will start Chrome automatically when you use `start_chrome()`
- **Can't connect**: Try `get_connection_status()` to check the connection
- **Tools not working**: Ensure you've called `connect_to_browser()` or used `start_chrome_and_connect()`

### Common Misconceptions
- **This is not a web server**: The MCP server runs inside Claude Desktop, not as a separate web service
- **No separate installation needed**: Once configured in Claude Desktop, the server starts automatically
- **Your app runs separately**: This tool connects to your existing web application, it doesn't run it

## Development & Testing

*This section is for developers who want to test or modify the MCP server itself.*

### Development Setup

**With uv (recommended):**
```bash
git clone https://github.com/benjaminr/chrome-devtools-mcp.git
cd chrome-devtools-mcp
uv sync
```

**With pip:**
```bash
git clone https://github.com/benjaminr/chrome-devtools-mcp.git
cd chrome-devtools-mcp
pip install -e ".[dev]"
```

### Running the Server During Development

```bash
# Using uvx (recommended - automatically handles dependencies)
uvx --from . chrome-devtools-mcp

# Using uv run
uv run python server.py

# Or directly with Python (if dependencies installed)
python server.py
```

### Code Quality Tools

```bash
# Format code
uv run ruff format .

# Lint code  
uv run ruff check .

# Type checking
uv run mypy src/
```

### Building the Extension

**Install DXT packaging tools:**
```bash
npm install -g @anthropic-ai/dxt
```

**Build the extension:**
```bash
# Quick build
make package

# Or manually
npx @anthropic-ai/dxt pack
```

**Using Makefile for development:**
```bash
make help           # Show all commands
make install        # Install dependencies
make dev            # Setup development environment + pre-commit
make check          # Run all checks (lint + type + test)
make pre-commit     # Run pre-commit hooks manually
make package        # Build .dxt extension
make release        # Full release build
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:

- **ruff**: Linting and formatting
- **mypy**: Type checking  
- **pytest**: Test validation
- **MCP validation**: Server registration check

Pre-commit hooks run automatically on `git commit` and can be run manually with `make pre-commit`.

## License

MIT License