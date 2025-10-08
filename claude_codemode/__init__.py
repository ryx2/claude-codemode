"""Claude Codemode - Python implementation of Cloudflare's Code Mode.

This library allows you to run pydantic-ai agents and Claude Agent SDK clients in
"code mode", where instead of directly calling tools, Claude writes Python code that
calls the tools to accomplish complex tasks.

Example with pydantic-ai:
    ```python
    from pydantic_ai import Agent
    from claude_codemode import codemode, CodeModeConfig

    agent = Agent('claude-sonnet-4-5-20250929')

    @agent.tool
    def search_docs(query: str) -> str:
        \"\"\"Search documentation.\"\"\"
        return f"Results for: {query}"

    @agent.tool
    def analyze_code(code: str) -> dict:
        \"\"\"Analyze code for issues.\"\"\"
        return {"issues": [], "quality": "good"}

    # Use codemode instead of run
    result = codemode(
        agent,
        "Search for authentication docs and analyze the code examples",
        config=CodeModeConfig(verbose=True)
    )

    print(result.output)
    ```

Example with Claude Agent SDK:
    ```python
    from claude_agent_sdk import ClaudeSDKClient
    import claude_codemode

    async with ClaudeSDKClient() as client:
        @client.register_codemode_tool
        def search_docs(query: str) -> str:
            \"\"\"Search documentation.\"\"\"
            return f"Results for: {query}"

        result = await client.codemode("Search for authentication docs")
        print(result.output)
    ```

Alternative usage with monkey-patched method:
    ```python
    from claude_codemode import CodeModeConfig
    import claude_codemode  # This adds .codemode() to Agent

    # Now you can use agent.codemode()
    result = agent.codemode(
        "Search for authentication docs and analyze the code examples"
    )
    ```
"""

from .core import CodeMode, codemode
from .types import CodeModeConfig, CodeModeResult

__version__ = "0.1.4"

__all__ = [
    "CodeMode",
    "codemode",
    "CodeModeConfig",
    "CodeModeResult",
]
