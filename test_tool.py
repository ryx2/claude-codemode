from pydantic_ai import Agent

# Try with tool_plain for tools that don't need context
agent = Agent('claude-sonnet-4-5-20250929')

@agent.tool_plain
def get_weather(city: str) -> str:
    """Get weather.

    Args:
        city: Name of the city

    Returns:
        Weather information
    """
    return f"Weather in {city}"

print("Tool registered successfully!")
print(f"Has _function_toolset: {hasattr(agent, '_function_toolset')}")
if hasattr(agent, '_function_toolset'):
    tools = agent._function_toolset.tools
    print(f"Tools: {tools}")
    print(f"Tools type: {type(tools)}")
    if tools:
        tool = list(tools.values())[0] if isinstance(tools, dict) else tools[0]
        print(f"First tool: {tool}")
        print(f"First tool type: {type(tool)}")
        print(f"First tool attrs: {[attr for attr in dir(tool) if not attr.startswith('_')]}")
