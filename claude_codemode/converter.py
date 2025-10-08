"""Tool converter for transforming pydantic-ai tools to Python code."""

import inspect
from typing import Any, List
from .types import ToolDefinition


class ToolConverter:
    """Converts pydantic-ai tools to Python function definitions."""

    @staticmethod
    def extract_tools(agent: Any) -> List[ToolDefinition]:
        """Extract tools from an agent (pydantic-ai or Claude SDK).

        Args:
            agent: The agent instance (pydantic-ai Agent or ClaudeSDKClient)

        Returns:
            List of ToolDefinition objects
        """
        tools = []

        # Check if this is a pydantic-ai agent (v1.0+)
        if hasattr(agent, '_function_toolset') and hasattr(agent._function_toolset, 'tools'):
            for tool in agent._function_toolset.tools.values():
                func = tool.function
                sig = inspect.signature(func)

                tool_def = ToolDefinition(
                    name=tool.name or func.__name__,
                    function=func,
                    description=tool.description or inspect.getdoc(func),
                    parameters=dict(sig.parameters),
                    return_annotation=sig.return_annotation
                )
                tools.append(tool_def)

        # Check if this is an older pydantic-ai agent
        elif hasattr(agent, '_function_tools'):
            for tool in agent._function_tools.values():
                func = tool.function
                sig = inspect.signature(func)

                tool_def = ToolDefinition(
                    name=tool.name or func.__name__,
                    function=func,
                    description=tool.description or inspect.getdoc(func),
                    parameters=dict(sig.parameters),
                    return_annotation=sig.return_annotation
                )
                tools.append(tool_def)

        # Check if this is a Claude SDK client with registered codemode tools
        elif hasattr(agent, '_codemode_tools'):
            for func in agent._codemode_tools:
                sig = inspect.signature(func)

                tool_def = ToolDefinition(
                    name=func.__name__,
                    function=func,
                    description=inspect.getdoc(func),
                    parameters=dict(sig.parameters),
                    return_annotation=sig.return_annotation
                )
                tools.append(tool_def)

        return tools

    @staticmethod
    def generate_function_code(tool: ToolDefinition) -> str:
        """Generate Python function code from a tool definition.

        Args:
            tool: The ToolDefinition to convert

        Returns:
            Python source code string
        """
        # Generate function signature
        params = []
        for param_name, param in tool.parameters.items():
            # Skip special parameters like RunContext
            if param_name in ('ctx', 'context', 'run_context'):
                continue

            param_str = param_name
            if param.annotation != inspect.Parameter.empty:
                # Get the annotation as a string
                annotation = param.annotation
                if hasattr(annotation, '__name__'):
                    param_str += f": {annotation.__name__}"
                else:
                    param_str += f": {annotation}"

            if param.default != inspect.Parameter.empty:
                if isinstance(param.default, str):
                    param_str += f' = "{param.default}"'
                else:
                    param_str += f" = {param.default}"

            params.append(param_str)

        params_str = ", ".join(params)

        # Generate return type
        return_type = ""
        if tool.return_annotation != inspect.Signature.empty:
            if hasattr(tool.return_annotation, '__name__'):
                return_type = f" -> {tool.return_annotation.__name__}"
            else:
                return_type = f" -> {tool.return_annotation}"

        # Generate docstring
        docstring = ""
        if tool.description:
            docstring = f'    """{tool.description}"""\n'

        # Get the actual function source if possible
        try:
            source = inspect.getsource(tool.function)
            # Remove decorators
            source_lines = source.split('\n')
            func_lines = []
            in_func = False
            for line in source_lines:
                if line.strip().startswith('def '):
                    in_func = True
                if in_func:
                    func_lines.append(line)

            if func_lines:
                return '\n'.join(func_lines)
        except (OSError, TypeError):
            pass

        # Generate a stub implementation
        code = f"def {tool.name}({params_str}){return_type}:\n"
        code += docstring
        code += "    # Tool implementation\n"
        code += f"    # This function should be implemented or will be called via the agent\n"
        code += "    pass\n"

        return code

    @staticmethod
    def serialize_dependencies(deps: Any) -> str:
        """Serialize dependencies to Python code.

        Args:
            deps: Dependencies to serialize

        Returns:
            Python code string representing the dependencies
        """
        if deps is None:
            return "dependencies = None"

        # Try to serialize as dict
        if hasattr(deps, '__dict__'):
            deps_dict = deps.__dict__
            return f"dependencies = {repr(deps_dict)}"

        return f"dependencies = {repr(deps)}"
