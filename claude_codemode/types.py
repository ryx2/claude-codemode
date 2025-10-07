"""Type definitions for Claude Codemode."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from inspect import Parameter


@dataclass
class ToolDefinition:
    """Represents a tool that can be called by the agent."""

    name: str
    function: Callable[..., Any]
    description: Optional[str]
    parameters: Dict[str, Parameter]
    return_annotation: Any


@dataclass
class CodeModeResult:
    """Result from a codemode execution."""

    output: Any
    execution_log: str
    success: bool
    error: Optional[str] = None


@dataclass
class CodeModeConfig:
    """Configuration for codemode execution."""

    workspace_dir: Optional[str] = None
    claude_code_path: str = "claude"
    timeout: int = 300  # 5 minutes default
    verbose: bool = False
    preserve_workspace: bool = False
