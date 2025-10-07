"""Simple test to demonstrate the core functionality without running Claude Code."""

import sys
sys.path.insert(0, '.')

from claude_codemode.template import TemplateGenerator
from claude_codemode.types import ToolDefinition
import inspect


# Create a simple mock tool
def get_weather(city: str) -> str:
    """Get the weather for a given city.

    Args:
        city: Name of the city

    Returns:
        Weather information
    """
    return f"Weather in {city}: Sunny, 72°F"


def calculate_temp_diff(temp1: str, temp2: str) -> str:
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
tools = [
    ToolDefinition(
        name="get_weather",
        function=get_weather,
        description=inspect.getdoc(get_weather),
        parameters=dict(inspect.signature(get_weather).parameters),
        return_annotation=inspect.signature(get_weather).return_annotation
    ),
    ToolDefinition(
        name="calculate_temp_diff",
        function=calculate_temp_diff,
        description=inspect.getdoc(calculate_temp_diff),
        parameters=dict(inspect.signature(calculate_temp_diff).parameters),
        return_annotation=inspect.signature(calculate_temp_diff).return_annotation
    )
]

# Generate the agentRunner.py template
template_gen = TemplateGenerator()
prompt = "Compare the weather between San Francisco and New York"
runner_code = template_gen.generate_runner(prompt, tools, deps=None)

print("=" * 80)
print("Generated agentRunner.py Template")
print("=" * 80)
print(runner_code)
print("\n" + "=" * 80)
print("✓ Template generation works!")
print("=" * 80)
print("\nThis template would be given to Claude Code to implement the main() function.")
print("Claude Code would write Python code that calls these tools to accomplish the task.")
