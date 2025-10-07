"""Basic example of using Claude Codemode."""

from pydantic_ai import Agent
from claude_codemode import codemode, CodeModeConfig


# Create an agent
agent = Agent('claude-sonnet-4-5-20250929')


# Define some tools
@agent.tool
def get_weather(city: str) -> str:
    """Get the weather for a given city.

    Args:
        city: Name of the city

    Returns:
        Weather information
    """
    # Simulated weather data
    weather_data = {
        "San Francisco": "Sunny, 72°F",
        "New York": "Cloudy, 65°F",
        "London": "Rainy, 55°F",
        "Tokyo": "Clear, 68°F",
    }
    return weather_data.get(city, f"Weather data not available for {city}")


@agent.tool
def calculate_temperature_difference(temp1: str, temp2: str) -> str:
    """Calculate the difference between two temperatures.

    Args:
        temp1: First temperature (e.g., "72°F")
        temp2: Second temperature (e.g., "65°F")

    Returns:
        Temperature difference
    """
    import re

    # Extract numbers from temperature strings
    match1 = re.search(r'(\d+)', temp1)
    match2 = re.search(r'(\d+)', temp2)

    if match1 and match2:
        diff = abs(int(match1.group(1)) - int(match2.group(1)))
        return f"{diff}°F"

    return "Unable to calculate difference"


def main():
    """Run a basic codemode example."""
    print("=" * 80)
    print("Basic Claude Codemode Example")
    print("=" * 80)

    # Configure codemode
    config = CodeModeConfig(
        verbose=True,
        preserve_workspace=True,  # Keep the workspace for inspection
        timeout=60,
    )

    # Run in code mode
    prompt = """
    Compare the weather between San Francisco and New York.
    Get the weather for both cities and calculate the temperature difference.
    Return a summary of the comparison.
    """

    print(f"\nPrompt: {prompt}\n")

    result = codemode(agent, prompt, config=config)

    print("\n" + "=" * 80)
    print("Result")
    print("=" * 80)

    if result.success:
        print(f"✓ Success!\n")
        print(f"Output: {result.output}")
    else:
        print(f"✗ Failed\n")
        print(f"Error: {result.error}")

    print(f"\nExecution log:\n{result.execution_log}")


if __name__ == "__main__":
    main()
