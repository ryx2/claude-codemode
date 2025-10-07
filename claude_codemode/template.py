"""Template generator for agentRunner.py files."""

from typing import Any, List, Optional
from .types import ToolDefinition
from .converter import ToolConverter


class TemplateGenerator:
    """Generates agentRunner.py templates with tool definitions."""

    @staticmethod
    def generate_runner(
        prompt: str,
        tools: List[ToolDefinition],
        deps: Any = None,
        result_type: Optional[type] = None
    ) -> str:
        """Generate the complete agentRunner.py file.

        Args:
            prompt: The user's prompt/query
            tools: List of tool definitions
            deps: Dependencies to pass to the agent
            result_type: Expected result type

        Returns:
            Complete Python source code for agentRunner.py
        """
        converter = ToolConverter()

        # Header
        code = '"""Generated agent runner for Claude Codemode execution."""\n\n'
        code += "import json\n"
        code += "import sys\n"
        code += "from typing import Any\n\n"

        # Add tool functions
        code += "# ============================================================================\n"
        code += "# TOOL DEFINITIONS\n"
        code += "# ============================================================================\n\n"

        for tool in tools:
            tool_code = converter.generate_function_code(tool)
            code += tool_code + "\n\n"

        # Add dependencies
        code += "# ============================================================================\n"
        code += "# DEPENDENCIES\n"
        code += "# ============================================================================\n\n"
        code += converter.serialize_dependencies(deps) + "\n\n"

        # Add prompt
        code += "# ============================================================================\n"
        code += "# TASK\n"
        code += "# ============================================================================\n\n"
        code += f'PROMPT = """{prompt}"""\n\n'

        # Add main execution
        code += "# ============================================================================\n"
        code += "# MAIN EXECUTION\n"
        code += "# ============================================================================\n\n"
        code += 'def main():\n'
        code += '    """\n'
        code += '    Execute the agent task using the available tools.\n'
        code += '    \n'
        code += '    Your goal is to:\n'
        code += '    1. Use the tools defined above to accomplish the task in PROMPT\n'
        code += '    2. Write code that calls these tools in the right sequence\n'
        code += '    3. Return the final result as a JSON object with a "result" key\n'
        code += '    \n'
        code += '    The tools are already defined and ready to use.\n'
        code += '    You have full access to Python\'s standard library.\n'
        code += '    \n'
        code += '    Example:\n'
        code += '        result = some_tool(param1, param2)\n'
        code += '        processed = another_tool(result)\n'
        code += '        return {"result": processed}\n'
        code += '    """\n'
        code += '    \n'
        code += '    # TODO: Implement the task logic here\n'
        code += '    # Use the tools defined above to accomplish the task in PROMPT\n'
        code += '    \n'
        code += '    pass\n\n\n'

        code += 'if __name__ == "__main__":\n'
        code += '    try:\n'
        code += '        result = main()\n'
        code += '        if result is not None:\n'
        code += '            print("CODEMODE_RESULT:", json.dumps({"result": result, "success": True}))\n'
        code += '        else:\n'
        code += '            print("CODEMODE_RESULT:", json.dumps({"error": "No result returned", "success": False}))\n'
        code += '    except Exception as e:\n'
        code += '        print("CODEMODE_RESULT:", json.dumps({"error": str(e), "success": False}), file=sys.stderr)\n'
        code += '        sys.exit(1)\n'

        return code

    @staticmethod
    def generate_instructions(prompt: str) -> str:
        """Generate instructions for Claude Code.

        Args:
            prompt: The user's prompt

        Returns:
            Instruction string for Claude Code
        """
        instructions = f"""You are executing in Code Mode - a special mode where you write code to accomplish tasks.

TASK: {prompt}

INSTRUCTIONS:
1. Read the agentRunner.py file to understand the available tools
2. Implement the main() function to accomplish the task
3. Use the provided tools to complete the task
4. The result should be returned from main() and will be automatically serialized
5. Test your implementation by running: python agentRunner.py
6. Once you get the desired output, your task is complete

The tools are already defined and implemented. Your job is to:
- Write the logic that calls these tools in the right order
- Handle the data flow between tool calls
- Return the final result

Remember: This is Code Mode - you're writing Python code that calls tools, not directly calling tools yourself.
"""
        return instructions
