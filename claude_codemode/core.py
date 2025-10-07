"""Core codemode functionality."""

from typing import Any, Optional

from .converter import ToolConverter
from .runner import ClaudeCodeRunner
from .template import TemplateGenerator
from .types import CodeModeConfig, CodeModeResult


class CodeMode:
    """Main codemode interface."""

    def __init__(self, config: Optional[CodeModeConfig] = None):
        """Initialize codemode.

        Args:
            config: Configuration for codemode execution
        """
        self.config = config or CodeModeConfig()
        self.converter = ToolConverter()
        self.template_gen = TemplateGenerator()
        self.runner = ClaudeCodeRunner(self.config)

    def run(
        self,
        agent: Any,
        prompt: str,
        deps: Any = None,
    ) -> CodeModeResult:
        """Run an agent in code mode.

        Args:
            agent: The pydantic-ai agent
            prompt: The task prompt
            deps: Optional dependencies

        Returns:
            CodeModeResult with the execution result
        """
        # Extract tools from agent
        tools = self.converter.extract_tools(agent)

        if self.config.verbose:
            print(f"Extracted {len(tools)} tools from agent")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")

        # Generate agentRunner.py
        runner_code = self.template_gen.generate_runner(prompt, tools, deps)

        # Generate instructions for Claude Code
        instructions = self.template_gen.generate_instructions(prompt)

        # Create workspace
        workspace = self.runner.create_workspace(runner_code)

        try:
            # Execute with Claude Code
            success, stdout, stderr = self.runner.execute_with_claude_code(
                workspace, instructions
            )

            # Extract result
            result = self.runner.extract_result(workspace, stdout, stderr)

            return result

        finally:
            # Cleanup
            if not self.config.preserve_workspace:
                self.runner.cleanup_workspace(workspace)


def codemode(
    agent: Any,
    prompt: str,
    deps: Any = None,
    config: Optional[CodeModeConfig] = None,
) -> CodeModeResult:
    """Convenience function to run an agent in code mode.

    Args:
        agent: The pydantic-ai agent
        prompt: The task prompt
        deps: Optional dependencies
        config: Optional configuration

    Returns:
        CodeModeResult with the execution result

    Example:
        ```python
        from pydantic_ai import Agent
        from claude_codemode import codemode

        agent = Agent('claude-3-5-sonnet-20241022')

        @agent.tool
        def get_weather(city: str) -> str:
            return f"Weather in {city}: Sunny, 72°F"

        result = codemode(agent, "What's the weather in San Francisco?")
        print(result.output)
        ```
    """
    cm = CodeMode(config)
    return cm.run(agent, prompt, deps)


# Monkey-patch extension for Agent classes
def add_codemode_to_agents():
    """Add codemode method to pydantic-ai Agent and Claude SDK classes."""
    # Try to add to pydantic-ai Agent
    try:
        from pydantic_ai import Agent

        def agent_codemode(
            self,
            prompt: str,
            deps: Any = None,
            config: Optional[CodeModeConfig] = None,
        ) -> CodeModeResult:
            """Run this agent in code mode.

            Args:
                prompt: The task prompt
                deps: Optional dependencies
                config: Optional configuration

            Returns:
                CodeModeResult with the execution result
            """
            return codemode(self, prompt, deps, config)

        # Add method to Agent class
        Agent.codemode = agent_codemode

        if hasattr(Agent, '__annotations__'):
            Agent.__annotations__['codemode'] = type(agent_codemode)

    except ImportError:
        # pydantic-ai not installed, skip monkey-patching
        pass

    # Try to add to Claude Agent SDK
    try:
        from claude_agent_sdk import ClaudeSDKClient

        # Store original methods
        _original_init = ClaudeSDKClient.__init__

        def _patched_init(self, *args, **kwargs):
            """Patched init to add codemode attribute."""
            _original_init(self, *args, **kwargs)
            self._codemode_tools = []

        def register_codemode_tool(self, func):
            """Register a tool for codemode usage.

            Args:
                func: The tool function to register

            Returns:
                The function (unchanged)
            """
            if not hasattr(self, '_codemode_tools'):
                self._codemode_tools = []
            self._codemode_tools.append(func)
            return func

        async def sdk_codemode(
            self,
            prompt: str,
            config: Optional[CodeModeConfig] = None,
        ) -> CodeModeResult:
            """Run this agent in code mode.

            Args:
                prompt: The task prompt
                config: Optional configuration

            Returns:
                CodeModeResult with the execution result
            """
            return codemode(self, prompt, config=config)

        # Add methods to ClaudeSDKClient class
        ClaudeSDKClient.__init__ = _patched_init
        ClaudeSDKClient.register_codemode_tool = register_codemode_tool
        ClaudeSDKClient.codemode = sdk_codemode

    except ImportError:
        # claude-agent-sdk not installed, skip monkey-patching
        pass


# Automatically add codemode method when module is imported
add_codemode_to_agents()
