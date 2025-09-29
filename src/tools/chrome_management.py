#!/usr/bin/env python3
"""Chrome Management Tools

This module provides Chrome browser lifecycle management through the DevTools Protocol.
It handles browser discovery, startup, connection management, and navigation with cross-platform
support for macOS, Windows, and Linux.

The tools support both headless and windowed Chrome modes, automatic executable detection,
and seamless connection to existing Chrome instances. All operations include
error handling and status reporting.

Key Features:
    - Cross-platform Chrome executable detection
    - Automatic browser startup with debugging enabled
    - Connection management with status monitoring
    - URL navigation and session control
    - Integration with existing Chrome instances

Example:
    Starting Chrome and connecting to a website:

    ```python
    # Start Chrome with remote debugging
    result = await start_chrome(port=9222, headless=False)

    # Navigate to a specific URL
    if result['success']:
        await navigate_to_url('https://example.com')
    ```
"""

from __future__ import annotations

import asyncio
import os
import platform
import subprocess
from typing import Any

import aiohttp
from mcp.server.fastmcp import FastMCP

from ..cdp_context import require_cdp_client
from .utils import create_error_response, create_success_response


def get_chrome_executable_path(custom_path: str | None = None) -> str | None:
    """Locate Chrome executable path with cross-platform detection.

    Searches for Chrome or Chromium executables using platform-specific default locations.
    Supports custom paths via parameter or CHROME_PATH environment variable.

    The function prioritises custom paths, then checks standard installation directories
    for each operating system. On macOS, it looks in Applications; on Windows, it checks
    Program Files and user-specific locations; on Linux, it examines common binary paths.

    Args:
        custom_path: Custom Chrome executable path to use instead of system defaults.
                    Takes precedence over environment variable and auto-detection.

    Returns:
        Absolute path to Chrome executable if found, None if no valid executable
        is located on the system.

    Environment Variables:
        CHROME_PATH: Alternative to custom_path parameter for specifying Chrome location.

    Note:
        The function validates that the executable file actually exists before returning
        the path, ensuring reliable browser startup.
    """
    # Check for environment variable first
    if not custom_path:
        custom_path = os.getenv("CHROME_PATH")

    if custom_path and custom_path.strip():
        if os.path.exists(custom_path):
            return custom_path
        else:
            return None

    system = platform.system().lower()

    if system == "darwin":  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    elif system == "windows":
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(
                os.getenv("USERNAME", "")
            ),
        ]
    else:  # Linux and others
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
        ]

    for path in paths:
        if os.path.exists(path):
            return path

    return None


async def check_chrome_running(port: int) -> bool:
    """Verify Chrome remote debugging availability on specified port.

    Performs a lightweight HTTP request to Chrome's debugging endpoint to confirm
    that the browser is running and accepting DevTools Protocol connections.
    Uses a short timeout to avoid blocking operations.

    Args:
        port: TCP port number where Chrome remote debugging should be listening.
              Standard default is 9222.

    Returns:
        True if Chrome is running and responding to debugging requests on the port,
        False if the connection fails, times out, or returns an error status.

    Note:
        This function uses a 2-second timeout to balance responsiveness with
        network reliability. Connection failures are silently handled and
        return False rather than raising exceptions.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://localhost:{port}/json/version", timeout=2) as response:
                return bool(response.status == 200)
    except Exception:
        return False


def register_chrome_tools(mcp: FastMCP) -> None:
    """Register comprehensive Chrome management tools with the MCP server.

    Adds all Chrome lifecycle management functions as MCP tools, including browser
    startup, connection management, navigation, and status monitoring. Each tool
    provides detailed error handling and standardised response formatting.

    The registered tools support the complete Chrome automation workflow:
    - Browser discovery and startup with configurable options
    - Connection establishment and session management
    - URL navigation and page control
    - Status monitoring and disconnection handling

    Args:
        mcp: FastMCP server instance to register tools with. Must be properly
             initialised before calling this function.

    Registered Tools:
        - start_chrome: Launch Chrome with debugging enabled
        - start_chrome_and_connect: Combined startup and connection
        - connect_to_browser: Connect to existing Chrome instance
        - navigate_to_url: Navigate to specific URLs
        - disconnect_from_browser: Clean session termination
        - get_connection_status: Status monitoring and diagnostics

    Note:
        All tools require access to the global CDP client instance for operation.
        Tools will return appropriate error responses if the client is unavailable.
    """

    @mcp.tool()
    async def start_chrome(
        port: int = 9222,
        url: str | None = None,
        headless: bool = False,
        chrome_path: str | None = None,
        auto_connect: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Start Chrome with remote debugging enabled and optionally establish connection.

        Launches Chrome browser with DevTools Protocol debugging enabled on the specified port.
        Supports both headless and windowed modes, with automatic executable detection
        across platforms. Can optionally connect to the started instance and navigate
        to a specific URL in a single operation.

        The function handles existing Chrome instances gracefully, detecting if Chrome
        is already running on the target port and optionally connecting to it rather
        than attempting to start a new instance.

        Args:
            port: TCP port for Chrome remote debugging server (default: 9222).
                  Must be available or already in use by Chrome.
            url: Initial URL to navigate to after starting Chrome. If provided,
                 Chrome will load this page on startup.
            headless: Whether to run Chrome in headless mode without GUI.
                     Useful for automated testing and server environments.
            chrome_path: Custom path to Chrome executable. If not provided,
                        uses automatic detection based on platform.
            auto_connect: Whether to automatically connect to Chrome and enable
                         debugging domains after startup.

        Returns:
            Comprehensive status dictionary containing:
            - success: Boolean indicating operation success
            - message: Human-readable status description
            - data: Detailed information including:
                - port: Port Chrome is running on
                - pid: Process ID of Chrome instance (if started)
                - connected: Whether connection was established
                - navigated: Whether URL navigation succeeded
                - alreadyRunning: Whether Chrome was already running

        Raises:
            The function handles exceptions internally and returns error responses
            rather than raising exceptions. Check the 'success' field in the response.

        Note:
            Uses a temporary user data directory to avoid conflicts with existing
            Chrome profiles. The directory location is platform-specific.
        """
        from .. import main

        cdp_client = main.cdp_client

        try:
            if await check_chrome_running(port):
                result = create_success_response(
                    message=f"Chrome already running on port {port}", port=port, alreadyRunning=True
                )

                # If auto_connect is enabled and Chrome is already running, connect now
                if auto_connect and cdp_client:
                    try:
                        # Ensure client targets the correct port before connecting
                        cdp_client.port = port  # type: ignore[attr-defined]
                        if not cdp_client.connected:
                            connected = await cdp_client.connect()
                            if connected:
                                await cdp_client.enable_domains()
                                result["data"]["connected"] = True

                        if url and cdp_client.connected:
                            await cdp_client.send_command("Page.navigate", {"url": url})
                            await asyncio.sleep(1)
                            result["data"]["navigated"] = True
                            result["data"]["url"] = url

                    except Exception as e:
                        result["data"]["connectionError"] = str(e)

                return result

            # Get Chrome executable path
            chrome_executable = get_chrome_executable_path(chrome_path)
            if not chrome_executable:
                error_msg = (
                    f"Chrome executable not found at: {chrome_path}"
                    if chrome_path
                    else "Chrome executable not found"
                )
                suggestion = (
                    "Please provide a valid chrome_path parameter"
                    if chrome_path
                    else "Please install Google Chrome or Chromium, or provide chrome_path"
                )
                return create_error_response(error_msg, suggestion)

            # Prepare Chrome arguments
            user_data_dir = (
                f"/tmp/chrome-debug-{port}"
                if platform.system() != "Windows"
                else f"C:\\temp\\chrome-debug-{port}"
            )
            chrome_args = [
                chrome_executable,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--disable-default-apps",
            ]

            if headless:
                chrome_args.append("--headless")

            if url:
                chrome_args.append(url)

            # Start Chrome process
            process = subprocess.Popen(
                chrome_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            # Wait for Chrome to start
            await asyncio.sleep(2)

            # Verify Chrome is accessible
            if not await check_chrome_running(port):
                return create_error_response(
                    "Failed to start Chrome with remote debugging",
                    f"Chrome process started but port {port} is not accessible",
                )

            result_data = {
                "port": port,
                "pid": process.pid,
                "headless": headless,
                "chromePath": chrome_executable,
                "alreadyRunning": False,
            }

            if url:
                result_data["initialUrl"] = url

            # Auto-connect if requested
            if auto_connect and cdp_client:
                try:
                    # Ensure client targets the correct port before connecting
                    cdp_client.port = port  # type: ignore[attr-defined]
                    connected = await cdp_client.connect()
                    if connected:
                        await cdp_client.enable_domains()
                        result_data["connected"] = True

                        # Navigate to URL if provided and not already set in chrome_args
                        if url:
                            await cdp_client.send_command("Page.navigate", {"url": url})
                            await asyncio.sleep(1)
                            result_data["navigated"] = True
                            result_data["url"] = url
                    else:
                        result_data["connected"] = False
                        result_data["connectionError"] = "Failed to connect after startup"

                except Exception as e:
                    result_data["connected"] = False
                    result_data["connectionError"] = str(e)

            message = f"Chrome started successfully on port {port}"
            if auto_connect and result_data.get("connected"):
                message += " and connected"
            if url and (result_data.get("navigated") or not auto_connect):
                message += f" with URL {url}"

            return create_success_response(message, **result_data)

        except Exception as e:
            return create_error_response(f"Error starting Chrome: {e}")

    @mcp.tool()
    async def start_chrome_and_connect(
        url: str,
        port: int = 9222,
        headless: bool = False,
        chrome_path: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Start Chrome with debugging, connect, and navigate to URL in one step.

        Convenience function that combines browser startup, connection establishment,
        and navigation into a single operation. Equivalent to calling start_chrome
        with auto_connect=True and a URL parameter.

        This function is ideal for quick browser automation tasks where you need
        to get Chrome running and navigate to a specific page without manual
        connection management.

        Args:
            url: Target URL to navigate to after Chrome startup. Must be a valid
                 URL that Chrome can load.
            port: TCP port for Chrome remote debugging server (default: 9222).
                  Must be available or already in use by Chrome.
            headless: Whether to run Chrome in headless mode without GUI.
                     Particularly useful for automated testing scenarios.
            chrome_path: Custom path to Chrome executable. If not provided,
                        uses automatic platform-specific detection.

        Returns:
            Combined status dictionary containing startup, connection, and navigation
            results. Includes all fields from start_chrome plus navigation status.

        Note:
            This is a convenience wrapper around start_chrome with auto_connect=True.
            For more granular control over the startup process, use start_chrome directly.
        """
        result = await start_chrome(
            port=port, url=url, headless=headless, chrome_path=chrome_path, auto_connect=True
        )
        return result  # type: ignore

    @mcp.tool()
    async def connect_to_browser(
        port: int = 9222,
        *,
        auto_start: bool = True,
        headless: bool = False,
        chrome_path: str | None = None,
        url: str | None = None,
    ) -> dict[str, Any]:
        """Connect to an existing Chrome instance with remote debugging enabled.

        Establishes a connection to a Chrome browser that's already running with
        remote debugging enabled on the specified port. Enables necessary DevTools
        Protocol domains and retrieves browser information.

        This function is useful when Chrome is already running (perhaps started
        manually or by another process) and you want to control it programmatically.
        It verifies the browser is accessible before attempting connection.

        Args:
            port: TCP port where Chrome remote debugging is listening (default: 9222).
            auto_start: If True, start Chrome with remote debugging when not found
                        and then connect automatically.
            headless: When auto-starting, whether to run Chrome in headless mode.
            chrome_path: Optional explicit Chrome executable path when auto-starting.
            url: Optional URL to open after connecting (used on auto-start too).

        Returns:
            Connection status dictionary containing:
            - success: Boolean indicating connection success
            - message: Human-readable status description
            - data: Connection details including:
                - connected: Boolean connection status
                - port: Port Chrome is running on
                - targetInfo: Browser version and capability information

        Note:
            If Chrome is not running on the specified port and auto_start is True,
            the server will launch Chrome with `--remote-debugging-port=PORT` and
            connect to it automatically. Set auto_start=False to disable this.
        """
        from .. import main

        cdp_client = main.cdp_client

        if not cdp_client:
            return create_error_response("CDP client not initialised")

        try:
            if not await check_chrome_running(port):
                if not auto_start:
                    return create_error_response(
                        f"Chrome not running on port {port}",
                        f"Start Chrome with: google-chrome --remote-debugging-port={port}",
                    )

                # Attempt to start Chrome and auto-connect
                start_result = await start_chrome(
                    port=port,
                    url=url,
                    headless=headless,
                    chrome_path=chrome_path,
                    auto_connect=True,
                )
                if not start_result.get("success"):
                    return start_result  # Propagate detailed error

            # Ensure the client uses the requested port
            cdp_client.port = port  # type: ignore[attr-defined]
            connected = cdp_client.connected or await cdp_client.connect()
            if not connected:
                return create_error_response("Failed to connect to Chrome")

            await cdp_client.enable_domains()
            target_info = await cdp_client.get_target_info()

            return create_success_response(
                message=f"Connected to Chrome on port {port}",
                data={"connected": True, "port": port, "targetInfo": target_info},
            )

        except Exception as e:
            return create_error_response(f"Connection error: {e}")

    @mcp.tool()
    @require_cdp_client
    async def navigate_to_url(url: str, **kwargs: Any) -> dict[str, Any]:
        """Navigate the connected browser to a specific URL.

        Instructs the currently connected Chrome instance to navigate to the specified
        URL. The function waits briefly for the navigation to begin before returning.
        Requires an active connection to Chrome established via connect_to_browser
        or start_chrome with auto_connect.

        Args:
            url: Target URL to navigate to. Must be a valid URL that Chrome can load,
                 including HTTP/HTTPS websites, local file paths, or data URIs.

        Returns:
            Navigation status dictionary containing:
            - success: Boolean indicating navigation success
            - message: Human-readable status description
            - data: Navigation details including:
                - url: The URL navigated to
                - navigated: Boolean navigation status

        Note:
            The function returns immediately after initiating navigation and doesn't
            wait for the page to fully load. Use additional tools to monitor page
            load completion if needed.
        """
        try:
            cdp_client = kwargs["cdp_client"]
            await cdp_client.send_command("Page.navigate", {"url": url})
            await asyncio.sleep(1)

            return create_success_response(
                message=f"Navigated to {url}", data={"url": url, "navigated": True}
            )

        except Exception as e:
            return create_error_response(f"Navigation error: {e}")

    @mcp.tool()
    @require_cdp_client
    async def disconnect_from_browser(**kwargs: Any) -> dict[str, Any]:
        """Disconnect from the current browser session.

        Cleanly terminates the connection to the Chrome browser instance while
        leaving the browser running. This is useful for releasing resources or
        preparing to connect to a different browser instance.

        The browser will continue running after disconnection, but will no longer
        be controllable through this client until a new connection is established.

        Returns:
            Disconnection status dictionary containing:
            - success: Boolean indicating disconnection success
            - message: Human-readable status description
            - data: Disconnection details including:
                - connected: Boolean status (should be False after disconnect)

        Note:
            This function only disconnects the client from Chrome; it doesn't
            close or terminate the browser process itself.
        """
        try:
            cdp_client = kwargs["cdp_client"]
            await cdp_client.disconnect()
            return create_success_response(
                message="Disconnected from browser", data={"connected": False}
            )

        except Exception as e:
            return create_error_response(f"Disconnection error: {e}")

    @mcp.tool()
    @require_cdp_client
    async def get_connection_status(**kwargs: Any) -> dict[str, Any]:
        """Get the current connection status to the browser.

        Retrieves comprehensive information about the current connection state,
        including browser details if connected. This is useful for diagnostics
        and determining whether other operations can be performed.

        The function provides different information depending on connection state:
        - If connected: Browser version, target info, and connection details
        - If not connected: Basic status information
        - If not initialised: Client setup status

        Returns:
            Status dictionary containing:
            - success: Boolean indicating status check success
            - message: Human-readable status description
            - data: Status details including:
                - connected: Boolean connection status
                - status: Text status (connected/disconnected/not_initialised)
                - targetInfo: Browser information (if connected)
                - host: Chrome host address (if connected)
                - port: Chrome port number (if connected)

        Note:
            This function is safe to call at any time and will not modify the
            connection state, only report it.
        """
        try:
            cdp_client = kwargs["cdp_client"]
            if cdp_client.connected:
                target_info = await cdp_client.get_target_info()
                return create_success_response(
                    message="Connected to browser",
                    data={
                        "connected": True,
                        "status": "connected",
                        "targetInfo": target_info,
                        "host": cdp_client.host,
                        "port": cdp_client.port,
                    },
                )
            else:
                return create_success_response(
                    message="Not connected to browser",
                    data={"connected": False, "status": "disconnected"},
                )

        except Exception as e:
            return create_error_response(f"Status check error: {e}")
