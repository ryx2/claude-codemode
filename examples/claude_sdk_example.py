"""Example using the Claude Agent SDK with codemode."""

import asyncio
from claude_codemode import CodeModeConfig

# This example demonstrates how to use codemode with the Claude Agent SDK


async def main():
    """Run a Claude Agent SDK codemode example."""
    print("=" * 80)
    print("Claude Agent SDK Codemode Example")
    print("=" * 80)

    try:
        from claude_agent_sdk import ClaudeSDKClient
    except ImportError:
        print("Error: claude-agent-sdk not installed")
        print("Install it with: pip install claude-agent-sdk")
        return

    # Create a Claude SDK client
    async with ClaudeSDKClient() as client:

        # Define tools using the register_codemode_tool method
        @client.register_codemode_tool
        def search_documentation(query: str) -> str:
            """Search the documentation for relevant information.

            Args:
                query: The search query

            Returns:
                Search results
            """
            # Simulated search results
            docs = {
                "api": """
                API Documentation:
                - Base URL: https://api.example.com
                - Authentication: Bearer token
                - Rate limit: 1000 requests/hour
                """,
                "authentication": """
                Authentication:
                - Get your API key from the dashboard
                - Include in Authorization header
                - Format: Authorization: Bearer YOUR_KEY
                """,
                "webhooks": """
                Webhooks:
                - Configure endpoint URL in settings
                - Verify signature using HMAC-SHA256
                - Retry policy: 3 attempts with exponential backoff
                """,
            }

            for key, content in docs.items():
                if key in query.lower():
                    return content

            return "No documentation found for query"

        @client.register_codemode_tool
        def analyze_code_snippet(code: str, language: str = "python") -> dict:
            """Analyze a code snippet for best practices.

            Args:
                code: The code to analyze
                language: Programming language (default: python)

            Returns:
                Analysis results with suggestions
            """
            # Simulated code analysis
            analysis = {
                "language": language,
                "lines": len(code.split("\n")),
                "suggestions": [
                    "Consider adding error handling",
                    "Add type hints for better code clarity",
                    "Include docstrings for functions",
                ],
                "quality_score": 7.5,
            }

            # Check for specific patterns
            if "try" not in code.lower():
                analysis["warnings"] = ["Missing error handling"]

            if "def " in code and '"""' not in code:
                analysis["warnings"] = analysis.get("warnings", [])
                analysis["warnings"].append("Missing docstrings")

            return analysis

        @client.register_codemode_tool
        def generate_summary(title: str, content: dict) -> str:
            """Generate a formatted summary report.

            Args:
                title: Report title
                content: Content to summarize (dict with sections)

            Returns:
                Formatted summary string
            """
            summary = f"# {title}\n\n"

            for key, value in content.items():
                summary += f"## {key.replace('_', ' ').title()}\n\n"
                if isinstance(value, list):
                    for item in value:
                        summary += f"- {item}\n"
                elif isinstance(value, dict):
                    for k, v in value.items():
                        summary += f"**{k}**: {v}\n"
                else:
                    summary += f"{value}\n"
                summary += "\n"

            return summary

        # Configure codemode
        config = CodeModeConfig(
            verbose=True,
            preserve_workspace=True,
            timeout=120,
        )

        # Run a complex task in code mode
        prompt = """
        Create a comprehensive API integration guide:

        1. Search for 'api' and 'authentication' documentation
        2. Extract example code snippets from the docs
        3. Analyze the code snippets for quality
        4. Generate a summary report with:
           - API overview
           - Authentication steps
           - Code examples with analysis
           - Best practices

        Return the final formatted report.
        """

        print(f"\nPrompt: {prompt}\n")
        print("Running in codemode...\n")

        # Call codemode on the client
        result = await client.codemode(prompt, config=config)

        print("\n" + "=" * 80)
        print("Result")
        print("=" * 80)

        if result.success:
            print(f"✓ Success!\n")
            print(result.output)
        else:
            print(f"✗ Failed\n")
            print(f"Error: {result.error}")

        if config.verbose:
            print(f"\n{'-' * 80}")
            print("Execution log:")
            print(f"{'-' * 80}")
            print(result.execution_log)


if __name__ == "__main__":
    asyncio.run(main())
