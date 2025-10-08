"""
Demonstration of Claude Codemode library.

This shows the FULL end-to-end workflow:
1. Create an agent with tools
2. Run codemode() to spawn Claude Code
3. Claude Code implements the task using the tools
4. Execute and return the result
"""

import sys
sys.path.insert(0, '.')

try:
    from pydantic_ai import Agent
    from claude_codemode import codemode, CodeModeConfig
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False
    print("Error: pydantic-ai not installed.")
    print("Install with: pip install 'claude-codemode[pydantic-ai]'")
    sys.exit(1)


print("=" * 80)
print("Claude Codemode - Live Demo")
print("=" * 80)
print()
print("This library implements Cloudflare's Code Mode for Python.")
print("Instead of directly calling tools, Claude writes Python code that calls them.")
print()

# Create an agent with tools
print("Step 1: Create agent with tools")
print("-" * 80)
agent = Agent('claude-sonnet-4-5-20250929')

@agent.tool_plain
def get_weather(city: str) -> str:
    """Get the weather for a given city.

    Args:
        city: Name of the city

    Returns:
        Weather information
    """
    weather_data = {
        "San Francisco": "Sunny, 72°F",
        "New York": "Cloudy, 65°F",
        "London": "Rainy, 55°F",
        "Tokyo": "Clear, 68°F",
    }
    return weather_data.get(city, f"Weather data not available for {city}")


@agent.tool_plain
def calculate_temperature_difference(temp1: str, temp2: str) -> str:
    """Calculate the difference between two temperatures.

    Args:
        temp1: First temperature (e.g., "72°F")
        temp2: Second temperature (e.g., "65°F")

    Returns:
        Temperature difference
    """
    import re
    match1 = re.search(r'(\d+)', temp1)
    match2 = re.search(r'(\d+)', temp2)
    if match1 and match2:
        diff = abs(int(match1.group(1)) - int(match2.group(1)))
        return f"{diff}°F"
    return "Unable to calculate difference"


print(f"  ✓ Created agent with 2 tools:")
print(f"    - get_weather(city)")
print(f"    - calculate_temperature_difference(temp1, temp2)")
print()

# Define the task
print("Step 2: Define the task")
print("-" * 80)
prompt = "Compare the weather between San Francisco and New York, and tell me the temperature difference."
print(f'  Task: "{prompt}"')
print()

# Configure codemode
print("Step 3: Running codemode...")
print("-" * 80)
print("This will:")
print("  1. Extract tools from the agent")
print("  2. Generate agentRunner.py with tool definitions")
print("  3. Spawn Claude Code to implement main() function")
print("  4. Execute the implementation and return result")
print()

config = CodeModeConfig(
    verbose=True,
    preserve_workspace=True,
    timeout=120,
)

# Actually run codemode!
print("Executing codemode (this will spawn Claude Code)...")
print("-" * 80)
result = codemode(agent, prompt, config=config)

# Show results
print()
print("=" * 80)
print("Step 4: Results")
print("=" * 80)

if result.success:
    print("✅ SUCCESS!")
    print()
    print(f"Output: {result.output}")
else:
    print("❌ FAILED")
    print()
    print(f"Error: {result.error}")

print()
print("-" * 80)
print("Execution Log:")
print("-" * 80)
print(result.execution_log)

print()
print("=" * 80)
print("Demo Complete!")
print("=" * 80)
print()
print("Key Takeaways:")
print("  ✓ Claude wrote Python code to call the tools (not direct tool calling)")
print("  ✓ Code naturally handled the multi-step workflow")
print("  ✓ This leverages Claude's extensive Python training data")
print("  ✓ More reliable than traditional tool calling for complex tasks")
print()
