# Claude Codemode 🚀

A Python implementation of [Cloudflare's Code Mode](https://blog.cloudflare.com/code-mode/), enabling AI agents to write code that calls tools instead of directly invoking them. Built on [pydantic-ai](https://ai.pydantic.dev) and Claude AI.

## What is Code Mode

**Traditional Tool Calling Agents:**

Input → LLM → loop(Tool Call → Execute Tool → Result → LLM) → output

**Code Mode Agent:**

Input → loop(Claude Codes w/ access to your tools) → Execute Code → output

## Why it's better

Each time tool output is passed to the LLM, and output is introduced, it leaves some possibility of mistake. As the number of iterations your agent does *n* increases, the better Code Mode gets compared to traditional iterative tool calling agents.

LLMs are better at generating code files & verifying & running that code they generate than calling tools to create output.

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                         Your Application                        │
│                                                                 │
│  agent = Agent('claude-sonnet-4-5-20250929')                    │
│                                                                 │
│  @agent.tool                                                    │
│  def search_docs(query: str) -> list[database_rows]: ...        │
│                                                                 │
│  @agent.tool                                                    │
│  def analyze_blueprints(file_location: str) -> dict: ...        │
│                                                                 │
│  @agent.tool                                                    │
│  def report_blueprint(pdf_location: str) -> None: ...           │
│                                                                 │
│  result = agent.codemode("verify structural integrity")         │
│             │                                                   │
└─────────────┼───────────────────────────────────────────────────┘
              │
              │ 1. Extract tools from agent
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Claude Codemode                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  2. Generate agentRunner.py with tool definitions        │   │
│  │                                                          │   │
│  │  def search_docs(query: str) -> list[database_rows]:     │   │
│  │      """Search documentation, returns database rows."""  │   │
│  │      "... implementation ..."                            │   │
│  │                                                          │   │
│  │  def analyze_blueprints(file_location: str) -> dict:     │   │
│  │      """Analyze blueprints for issues."""                │   │
│  │      "... implementation ..."                            │   │
│  │                                                          │   │
│  │  def report_blueprint(pdf_location: str) -> None:        │   │
│  │      """Report a blueprint for failing standards."""     │   │
│  │      "... implementation ..."                            │   │
│  │                                                          │   │
│  │  def main(params: str = "verify structural integrity")   │   │
│  │      "TODO: Implement task using above tools"            │   │
│  │      pass                                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │ 3. Spawn Claude Code
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Code                              │
│                                                                 │
│  Instructions:                                                  │
│  "Implement the main() function to accomplish the task.         │
│   Use the provided tools by writing Python code."               │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Claude reads agentRunner.py                            │     │
│  │ Claude writes implementation:                          │     │
│  │                                                        │     │
│  │ def find_database_files_on_disk(database_row):         │     │
│  │     "Claude wrote this helper function!"               │     │
│  │     return database_row['file'].download().path        │     │
│  │                                                        │     │
│  │ def main():                                            │     │
│  │     "Search docs - returns database rows"              │     │
│  │     database_rows = search_docs("structural integrity")│     │
│  │                                                        │     │
│  │     "Analyze each blueprint and report failures"       │     │
│  │     analyses = []                                      │     │
│  │     for row in database_rows:                          │     │
│  │         file_path = find_database_files_on_disk(row)   │     │
│  │         result = analyze_blueprints(file_path)         │     │
│  │         analyses.append(result)                        │     │
│  │         if not result.passes:                          │     │
│  │             report_blueprint(file_path)                │     │
│  │                                                        │     │
│  │     return {"analyses": analyses}                      │     │
│  └────────────────────────────────────────────────────────┘     │
│                          │                                      │
│                          │ 4. Execute agentRunner.py            │
│                          ▼                                      │
│              ┌────────────────────────┐                         │
│              │  python agentRunner.py │                         │
│              └────────────────────────┘                         │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │ 5. Return result
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CodeModeResult                             │
│                                                                 │
│  {                                                              │
│    "output": {...},                                             │
│    "success": true,                                             │
│    "execution_log": "..."                                       │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

### More Specifically Why It's Better

This problem has a lot of elements of what an agent excels at: some ambiguity, needing to integrate pieces together, formatting a nice output.

As the amount of functions needed to be called by the agents becomes very large, then the amount of advantage that the Code Mode Agent has keeps increasing. The best LLM agents today can call tools in parallel, but it's difficult for them to call > 10 tools in parallel. They can call tools in serially, but after 20 iterations, they lose track of where they are even with a todo list. 

With Code Mode Agent, you can call an essentially unlimited amount of functions provided to you by the original agent definition, without waiting for a ridiculous number of agent iterations because of for serial or parallel limitations of agents.  

## Installation

Install with support for your preferred agent framework:

```bash
# For pydantic-ai support
pip install claude-codemode[pydantic-ai]

# For Claude Agent SDK support
pip install claude-codemode[anthropic-sdk]

# For both
pip install claude-codemode[all]
```

Or install from source:

```bash
git clone https://github.com/yourusername/claude-codemode.git
cd claude-codemode

# Using pip
pip install -e ".[all]"

# Or using poetry (recommended for development)
poetry install --extras pydantic-ai
# Then run examples with: poetry run python examples/basic_example.py
```

### Prerequisites

- Python 3.10+
- [Claude Code](https://claude.com/claude-code) CLI installed
- Anthropic API key set up for Claude Code
- Either `pydantic-ai` or `claude-agent-sdk` (installed via extras above)

## Quick Start

### Basic Usage

```python
from pydantic_ai import Agent
from claude_codemode import codemode

# Create an agent with tools
agent = Agent('claude-sonnet-4-5-20250929')

@agent.tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Weather in {city}: Sunny, 72°F"

@agent.tool
def calculate_temp_diff(temp1: str, temp2: str) -> str:
    """Calculate temperature difference."""
    import re
    t1 = int(re.search(r'(\d+)', temp1).group(1))
    t2 = int(re.search(r'(\d+)', temp2).group(1))
    return f"{abs(t1 - t2)}°F"

# Use codemode instead of run
result = codemode(
    agent,
    "Compare weather between San Francisco and New York"
)

print(result.output)
```

### Using the Monkey-Patched Method

```python
from pydantic_ai import Agent
import claude_codemode  # This adds .codemode() to Agent

agent = Agent('claude-sonnet-4-5-20250929')

@agent.tool
def search_docs(query: str) -> str:
    """Search documentation."""
    return f"Results for: {query}"

# Call codemode directly on the agent
result = agent.codemode("Search for authentication docs")
print(result.output)
```

### Using Claude Agent SDK

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient
import claude_codemode  # This adds .codemode() to ClaudeSDKClient

async def main():
    async with ClaudeSDKClient() as client:
        # Register tools using the codemode extension
        @client.register_codemode_tool
        def search_docs(query: str) -> str:
            """Search documentation."""
            return f"Results for: {query}"

        @client.register_codemode_tool
        def analyze_code(code: str) -> dict:
            """Analyze code for issues."""
            return {"issues": [], "quality": "good"}

        # Use codemode
        result = await client.codemode(
            "Search for authentication docs and analyze the examples"
        )
        print(result.output)

asyncio.run(main())
```

### With Configuration

```python
from claude_codemode import codemode, CodeModeConfig

config = CodeModeConfig(
    verbose=True,              # Print detailed logs
    preserve_workspace=True,   # Keep workspace for inspection
    timeout=300,               # 5 minute timeout
    workspace_dir="/tmp/my-workspace"  # Custom workspace location
)

result = codemode(agent, "Your complex task here", config=config)
```

## Architecture

### Components

```
claude_codemode/
├── core.py          # Main CodeMode class and codemode() function
├── converter.py     # Extracts and converts pydantic-ai tools
├── template.py      # Generates agentRunner.py templates
├── runner.py        # Manages Claude Code subprocess
└── types.py         # Type definitions
```

### Flow Diagram

```
User Code → Extract Tools → Generate Template → Spawn Claude Code → Execute → Return Result
    ↓           ↓                ↓                    ↓              ↓           ↓
  Agent    ToolConverter   TemplateGenerator   ClaudeCodeRunner  agentRunner.py CodeModeResult
```

## Advanced Examples

### With Dependencies

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class DatabaseContext:
    connection_string: str

agent = Agent('claude-sonnet-4-5-20250929', deps_type=DatabaseContext)

@agent.tool
def query_db(ctx: RunContext[DatabaseContext], sql: str) -> list:
    """Execute database query."""
    # Use ctx.deps.connection_string
    return [{"id": 1, "name": "Alice"}]

deps = DatabaseContext("postgresql://localhost/mydb")
result = codemode(agent, "Get all users from database", deps=deps)
```

### Complex Multi-Step Tasks

```python
agent = Agent('claude-sonnet-4-5-20250929')

@agent.tool
def fetch_data(source: str) -> dict:
    """Fetch data from source."""
    pass

@agent.tool
def transform_data(data: dict, rules: list) -> dict:
    """Transform data according to rules."""
    pass

@agent.tool
def validate_data(data: dict) -> bool:
    """Validate transformed data."""
    pass

@agent.tool
def store_data(data: dict, destination: str) -> bool:
    """Store data to destination."""
    pass

# Code Mode handles the complex orchestration
result = codemode(
    agent,
    """
    Create an ETL pipeline:
    1. Fetch data from 'api_source'
    2. Transform using rules: ['normalize', 'deduplicate']
    3. Validate the transformed data
    4. If valid, store to 'warehouse'
    5. Return success status and record count
    """
)
```

## API Reference

### `codemode(agent, prompt, deps=None, config=None)`

Execute an agent in code mode.

**Parameters:**
- `agent` (Agent): The pydantic-ai agent with tools
- `prompt` (str): Task description for Claude
- `deps` (Any, optional): Dependencies for the agent
- `config` (CodeModeConfig, optional): Configuration options

**Returns:**
- `CodeModeResult`: Result object with output, success status, and logs

### `CodeModeConfig`

Configuration for codemode execution.

```python
@dataclass
class CodeModeConfig:
    workspace_dir: Optional[str] = None       # Custom workspace directory
    claude_code_path: str = "claude"          # Path to Claude Code CLI
    timeout: int = 300                        # Execution timeout in seconds
    verbose: bool = False                     # Enable detailed logging
    preserve_workspace: bool = False          # Keep workspace after execution
```

### `CodeModeResult`

Result from codemode execution.

```python
@dataclass
class CodeModeResult:
    output: Any                # The result from the agent
    execution_log: str         # Complete execution logs
    success: bool              # Whether execution succeeded
    error: Optional[str] = None  # Error message if failed
```

## Comparison: Traditional vs Code Mode

### Traditional Tool Calling

```python
# Agent directly calls tools
result = agent.run("Compare weather in SF and NY")

# Behind the scenes:
# 1. LLM decides to call get_weather("San Francisco")
# 2. LLM decides to call get_weather("New York")
# 3. LLM decides to call calculate_difference(...)
# Limited by tool calling training data
```

### Code Mode

```python
# Agent writes code that calls tools
result = agent.codemode("Compare weather in SF and NY")

# Behind the scenes:
# 1. Claude sees available tools as Python functions
# 2. Claude writes: sf_weather = get_weather("San Francisco")
# 3. Claude writes: ny_weather = get_weather("New York")
# 4. Claude writes: diff = calculate_difference(sf_weather, ny_weather)
# Leverages extensive Python training data
```

## Benefits

### 🎯 Better Tool Usage
Claude is trained on millions of Python examples and knows how to compose functions naturally.

### 🔄 Complex Workflows
Multi-step tasks with conditionals, loops, and error handling become trivial.

### 🐛 Easier Debugging
Generated Python code can be inspected, modified, and tested independently.

### 🚀 More Reliable
Reduces errors from unfamiliar tool-calling formats.

### 💡 Flexible
Claude can use Python's full capabilities (data structures, libraries, etc.)

## Examples

See the `examples/` directory for complete examples:

- [`basic_example.py`](examples/basic_example.py) - Simple weather comparison with pydantic-ai
- [`advanced_example.py`](examples/advanced_example.py) - Complex ETL with dependencies
- [`monkey_patch_example.py`](examples/monkey_patch_example.py) - Using `agent.codemode()` method
- [`claude_sdk_example.py`](examples/claude_sdk_example.py) - Using Claude Agent SDK with codemode

Run an example:

```bash
cd examples
python basic_example.py
# or for Claude SDK
python claude_sdk_example.py
```

## Limitations

- Requires Claude Code CLI to be installed
- Spawns a subprocess for each codemode execution
- Tools must be serializable to Python source code
- Currently only supports Python tools (not TypeScript like Cloudflare's version)

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.


## Inspirations

- [Cloudflare's blog post](https://blog.cloudflare.com/code-mode/) introducing the code mode concept
- [Theo's t3 chat video](https://youtu.be/bAYZjVAodoo?si=ouW-gfrrBsaz5LSj) for making me aware of this approach
- [Early MCP implementation](https://github.com/jx-codes/codemode-mcp) by jx-codes

## Acknowledgments

- Inspired by [Cloudflare's Code Mode](https://blog.cloudflare.com/code-mode/)
- Built on [pydantic-ai](https://ai.pydantic.dev)
- Powered by [Claude AI](https://claude.ai)

## Related Projects

- [pydantic-ai](https://github.com/pydantic/pydantic-ai) - Data validation using Python type hints
- [Claude Code](https://claude.com/claude-code) - Official Claude CLI
- [Anthropic Agent SDK](https://docs.claude.com/en/api/agent-sdk/python) - Agent development framework

---

Made with ❤️ by the Claude Codemode Contributors
