"""
Demonstration of Claude Codemode library.

This shows the core functionality:
1. Extract tools from an agent
2. Generate agentRunner.py template
3. Show what would be sent to Claude Code
"""

import sys
sys.path.insert(0, '.')

from claude_codemode.template import TemplateGenerator
from claude_codemode.types import ToolDefinition
from claude_codemode.converter import ToolConverter
import inspect


print("=" * 80)
print("Claude Codemode - Demo")
print("=" * 80)
print()
print("This library implements Cloudflare's Code Mode for Python.")
print("Instead of directly calling tools, Claude writes Python code that calls them.")
print()

# Create simple mock tools
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


# Create tool definitions
print("Step 1: Define tools")
print("-" * 80)
tools = [
    ToolDefinition(
        name="get_weather",
        function=get_weather,
        description=inspect.getdoc(get_weather),
        parameters=dict(inspect.signature(get_weather).parameters),
        return_annotation=inspect.signature(get_weather).return_annotation
    ),
    ToolDefinition(
        name="calculate_temperature_difference",
        function=calculate_temperature_difference,
        description=inspect.getdoc(calculate_temperature_difference),
        parameters=dict(inspect.signature(calculate_temperature_difference).parameters),
        return_annotation=inspect.signature(calculate_temperature_difference).return_annotation
    )
]

for tool in tools:
    print(f"  ✓ {tool.name}")
print()

# Generate the agentRunner.py template
print("Step 2: Generate agentRunner.py template")
print("-" * 80)
template_gen = TemplateGenerator()
prompt = "Compare the weather between San Francisco and New York, and tell me the temperature difference."
runner_code = template_gen.generate_runner(prompt, tools, deps=None)
print(f"  ✓ Generated {len(runner_code)} characters of Python code")
print()

print("Step 3: What gets sent to Claude Code")
print("-" * 80)
print("The agentRunner.py file contains:")
print("  • Tool definitions (as Python functions)")
print("  • The task prompt")
print("  • A main() function stub for Claude to implement")
print()
print("Claude Code is instructed:")
print('  "Implement the main() function using the tools provided"')
print()

print("Step 4: Preview of generated agentRunner.py")
print("-" * 80)
# Show first part of the generated code
lines = runner_code.split('\n')
preview_lines = 40
print('\n'.join(lines[:preview_lines]))
print(f"\n... ({len(lines)} total lines) ...")
print()

print("=" * 80)
print("✅ Demo Complete!")
print("=" * 80)
print()
print("Key Points:")
print("  1. Tools are converted to Python function definitions")
print("  2. Claude Code sees them as regular Python code (not tool calling)")
print("  3. Claude writes Python that calls these functions naturally")
print("  4. Result is executed and returned")
print()
print("This leverages Claude's extensive Python training data instead of")
print("limited tool-calling training, resulting in better complex workflows!")
print()
print("To use with real agents:")
print("  • pydantic-ai: result = agent.codemode('your task here')")
print("  • Claude SDK: result = await client.codemode('your task here')")
print()
