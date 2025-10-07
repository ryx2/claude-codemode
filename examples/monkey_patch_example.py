"""Example using the monkey-patched agent.codemode() method."""

from pydantic_ai import Agent
import claude_codemode  # This adds .codemode() to Agent
from claude_codemode import CodeModeConfig


# Create agent
agent = Agent('claude-sonnet-4-5-20250929')


@agent.tool
def search_documentation(query: str) -> str:
    """Search documentation for relevant information.

    Args:
        query: Search query

    Returns:
        Search results
    """
    # Simulated search results
    docs = {
        "authentication": """
        Authentication Guide:
        - Use API keys for authentication
        - Include key in Authorization header
        - Keys can be generated in dashboard
        """,
        "rate limiting": """
        Rate Limiting:
        - Default limit: 100 requests/minute
        - Headers: X-RateLimit-Remaining
        - Upgrade for higher limits
        """,
        "webhooks": """
        Webhook Configuration:
        - POST endpoint required
        - Verify signature using secret
        - Retry logic: 3 attempts
        """,
    }

    for key, content in docs.items():
        if key in query.lower():
            return content

    return "No results found"


@agent.tool
def extract_code_examples(text: str) -> list:
    """Extract code examples from text.

    Args:
        text: Text containing code examples

    Returns:
        List of code examples
    """
    import re

    # Simple extraction (in reality would be more sophisticated)
    code_blocks = re.findall(r'`([^`]+)`', text)
    return code_blocks if code_blocks else ["No code examples found"]


@agent.tool
def create_summary(title: str, points: list) -> str:
    """Create a formatted summary.

    Args:
        title: Summary title
        points: List of bullet points

    Returns:
        Formatted summary
    """
    summary = f"**{title}**\n\n"
    for i, point in enumerate(points, 1):
        summary += f"{i}. {point}\n"
    return summary


def main():
    """Demonstrate the monkey-patched .codemode() method."""
    print("=" * 80)
    print("Monkey-Patched agent.codemode() Example")
    print("=" * 80)

    # Using the monkey-patched method directly on the agent
    config = CodeModeConfig(verbose=True, preserve_workspace=True)

    prompt = """
    Research authentication in the documentation and create a summary.

    Steps:
    1. Search for authentication documentation
    2. Extract any code examples from the docs
    3. Create a summary with key points about authentication

    Return the final summary.
    """

    print(f"\nPrompt: {prompt}\n")
    print("Calling agent.codemode() - note the method is added via monkey-patching!\n")

    # This is the key difference - calling .codemode() directly on the agent
    result = agent.codemode(prompt, config=config)

    print("\n" + "=" * 80)
    print("Result")
    print("=" * 80)

    if result.success:
        print(f"✓ Success!\n")
        print(result.output)
    else:
        print(f"✗ Failed\n")
        print(f"Error: {result.error}")


if __name__ == "__main__":
    main()
