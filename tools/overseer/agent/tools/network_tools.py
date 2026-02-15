"""
Network Tools

Governed HTTP requests.
"""


from .base_tool import BaseTool, ToolResult


class HttpRequestTool(BaseTool):
    """Make HTTP requests."""

    name = "HttpRequest"
    description = "Make an HTTP request"
    required_params = ("url",)
    optional_params = {
        "method": "GET",
        "headers": {},
        "body": None,
        "timeout": 30,
        "verify_ssl": True,
    }

    def execute(self, **params) -> ToolResult:
        """
        Make an HTTP request.

        Args:
            url: Request URL
            method: HTTP method (GET, POST, etc.)
            headers: Request headers
            body: Request body (for POST, PUT, etc.)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates

        Returns:
            ToolResult with response data
        """
        try:
            import json as json_module
            import urllib.error
            import urllib.request

            url = params["url"]
            method = self.get_param(params, "method", "GET").upper()
            headers = self.get_param(params, "headers", {})
            body = self.get_param(params, "body", None)
            timeout = self.get_param(params, "timeout", 30)

            # Prepare request
            if body is not None:
                if isinstance(body, dict):
                    body = json_module.dumps(body).encode("utf-8")
                    if "Content-Type" not in headers:
                        headers["Content-Type"] = "application/json"
                elif isinstance(body, str):
                    body = body.encode("utf-8")

            request = urllib.request.Request(
                url,
                data=body,
                headers=headers,
                method=method,
            )

            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    content = response.read()

                    # Try to decode as text
                    try:
                        content_text = content.decode("utf-8")
                        # Try to parse as JSON
                        try:
                            content_json = json_module.loads(content_text)
                            output = content_json
                        except json_module.JSONDecodeError:
                            output = content_text
                    except UnicodeDecodeError:
                        output = content

                    return ToolResult.ok(
                        output=output,
                        status_code=response.status,
                        headers=dict(response.headers),
                        url=response.url,
                    )

            except urllib.error.HTTPError as e:
                return ToolResult.fail(
                    error=f"HTTP {e.code}: {e.reason}",
                    status_code=e.code,
                    url=url,
                )
            except urllib.error.URLError as e:
                return ToolResult.fail(
                    error=f"URL Error: {e.reason}",
                    url=url,
                )

        except TimeoutError:
            return ToolResult.fail(
                error=f"Request timed out after {timeout}s",
                url=params.get("url"),
            )
        except Exception as e:
            return ToolResult.fail(
                error=f"Request failed: {e}",
                url=params.get("url"),
            )
