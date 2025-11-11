"""Secure Sandbox for Code Execution

Provides secure, resource-limited Python execution environment.
Implements safety controls for untrusted code execution.
"""

import sys
import io
import traceback
import resource
import signal
from contextlib import contextmanager
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    max_execution_time: int = 30  # seconds
    max_memory: int = 512 * 1024 * 1024  # 512MB
    max_output_size: int = 1024 * 1024  # 1MB
    allow_network: bool = True
    allow_file_write: bool = False
    allowed_modules: set = None

    def __post_init__(self):
        if self.allowed_modules is None:
            # Default allowed modules for maritime AI
            self.allowed_modules = {
                'json', 'datetime', 'math', 're', 'typing',
                'dataclasses', 'collections', 'itertools',
                'functools', 'operator', 'statistics',
                # Maritime-specific
                'requests',  # For API calls
                'pandas',    # Data processing
                'numpy',     # Numerical operations
            }


class SandboxExecutionError(Exception):
    """Raised when sandbox execution fails"""
    pass


class SandboxTimeoutError(SandboxExecutionError):
    """Raised when execution exceeds time limit"""
    pass


class SandboxMemoryError(SandboxExecutionError):
    """Raised when execution exceeds memory limit"""
    pass


class SecureSandbox:
    """
    Secure sandbox for executing Python code.

    Features:
    - Resource limits (CPU, memory, time)
    - Module restrictions
    - Output capture
    - Error handling
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self._original_modules = None

    def execute(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Tuple[Any, str, str]:
        """
        Execute code in sandbox.

        Args:
            code: Python code to execute
            context: Variables to inject into execution context
            timeout: Override default timeout

        Returns:
            Tuple of (result, stdout, stderr)

        Raises:
            SandboxExecutionError: On execution failure
            SandboxTimeoutError: On timeout
            SandboxMemoryError: On memory limit exceeded
        """
        timeout = timeout or self.config.max_execution_time

        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        result = None
        error = None

        try:
            with self._resource_limits():
                with self._timeout(timeout):
                    with self._captured_output(stdout_capture, stderr_capture):
                        # Prepare execution context
                        exec_context = self._prepare_context(context or {})

                        # Execute code
                        exec(code, exec_context)

                        # Extract result if available
                        if 'result' in exec_context:
                            result = exec_context['result']

        except TimeoutError as e:
            error = SandboxTimeoutError(f"Execution exceeded {timeout}s timeout")
            stderr_capture.write(str(error))

        except MemoryError as e:
            error = SandboxMemoryError("Execution exceeded memory limit")
            stderr_capture.write(str(error))

        except Exception as e:
            error = SandboxExecutionError(f"Execution failed: {str(e)}")
            stderr_capture.write(traceback.format_exc())

        stdout = stdout_capture.getvalue()
        stderr = stderr_capture.getvalue()

        # Truncate output if too large
        if len(stdout) > self.config.max_output_size:
            stdout = stdout[:self.config.max_output_size] + "\n... (truncated)"

        if len(stderr) > self.config.max_output_size:
            stderr = stderr[:self.config.max_output_size] + "\n... (truncated)"

        if error:
            raise error

        return result, stdout, stderr

    def _prepare_context(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare execution context with restricted builtins"""
        # Start with safe builtins
        safe_builtins = {
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'sorted': sorted,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'any': any,
            'all': all,
        }

        # Restricted imports
        def safe_import(name, *args, **kwargs):
            if name not in self.config.allowed_modules:
                raise ImportError(f"Module '{name}' not allowed in sandbox")
            return __import__(name, *args, **kwargs)

        safe_builtins['__import__'] = safe_import

        # Combine with user context
        exec_context = {
            '__builtins__': safe_builtins,
            **user_context
        }

        return exec_context

    @contextmanager
    def _resource_limits(self):
        """Set resource limits for execution"""
        try:
            # Set memory limit (soft, hard)
            resource.setrlimit(
                resource.RLIMIT_AS,
                (self.config.max_memory, self.config.max_memory)
            )
        except (ValueError, OSError):
            # Resource limits may not be available on all systems
            pass

        yield

        # Reset limits
        try:
            resource.setrlimit(
                resource.RLIMIT_AS,
                (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
            )
        except (ValueError, OSError):
            pass

    @contextmanager
    def _timeout(self, seconds: int):
        """Timeout context manager"""

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Execution exceeded {seconds}s")

        # Set alarm
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)

        try:
            yield
        finally:
            # Cancel alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    @contextmanager
    def _captured_output(self, stdout_capture: io.StringIO, stderr_capture: io.StringIO):
        """Capture stdout and stderr"""
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


class SandboxValidator:
    """Validates code before execution"""

    DANGEROUS_PATTERNS = [
        'os.system',
        'subprocess',
        'eval(',
        'exec(',
        '__import__',
        'open(',
        'file(',
        'input(',
    ]

    @staticmethod
    def validate(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate code for security issues.

        Returns:
            Tuple of (is_safe, error_message)
        """
        # Check for dangerous patterns
        for pattern in SandboxValidator.DANGEROUS_PATTERNS:
            if pattern in code:
                return False, f"Dangerous pattern detected: {pattern}"

        # Check code length
        if len(code) > 100_000:
            return False, "Code too long (max 100KB)"

        return True, None
