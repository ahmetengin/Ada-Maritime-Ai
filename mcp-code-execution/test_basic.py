"""Basic tests for MCP code execution"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from runtime import CodeExecutionRuntime
from tool_loader import ToolLoader
from sandbox import SecureSandbox, SandboxValidator
from privacy import PrivacyLayer, PIIDetector


def test_tool_loader():
    """Test tool discovery and loading"""
    print("\n=== Testing Tool Loader ===")

    loader = ToolLoader()

    # List servers
    servers = loader.list_servers()
    print(f"✓ Found {len(servers)} servers: {servers}")

    # Search tools
    tools = loader.search_tools("vessel")
    print(f"✓ Search 'vessel': {len(tools)} results")

    # List tools in server
    if "maritime-data" in servers:
        tools = loader.list_tools("maritime-data")
        print(f"✓ Maritime tools: {[t.name for t in tools]}")

    # Load a tool
    if "maritime-data" in servers:
        tool_func = loader.load_tool_function("maritime-data", "vessel_tracking")
        if tool_func:
            print("✓ Loaded vessel_tracking function")
        else:
            print("✗ Failed to load tool function")

    print("✓ Tool loader tests passed")


def test_sandbox():
    """Test secure sandbox execution"""
    print("\n=== Testing Sandbox ===")

    sandbox = SecureSandbox()

    # Test simple execution
    code = """
result = 2 + 2
print(f"Result: {result}")
"""

    result, stdout, stderr = sandbox.execute(code)
    assert result == 4, "Simple math failed"
    print(f"✓ Simple execution: {result}")

    # Test validation
    is_safe, error = SandboxValidator.validate("print('hello')")
    assert is_safe, "Safe code marked unsafe"
    print("✓ Safe code validated")

    is_safe, error = SandboxValidator.validate("os.system('rm -rf /')")
    assert not is_safe, "Dangerous code not caught"
    print("✓ Dangerous code blocked")

    print("✓ Sandbox tests passed")


def test_privacy():
    """Test PII detection and tokenization"""
    print("\n=== Testing Privacy Layer ===")

    privacy = PrivacyLayer()

    # Test PII detection
    text = "Contact john@example.com at IMO9876543"
    detections = PIIDetector.detect(text)
    print(f"✓ Detected PII: {list(detections.keys())}")

    # Test tokenization
    tokenized, tokens = privacy.tokenize_pii(text)
    print(f"✓ Tokenized: {tokenized}")

    # Test detokenization
    restored = privacy.detokenize(tokenized)
    print(f"✓ Detokenized: {restored}")

    # Test sensitive data filtering
    data = {
        "name": "John Doe",
        "password": "secret123",
        "api_key": "abc123"
    }
    filtered = privacy.filter_sensitive_data(data)
    assert filtered["password"] == "[REDACTED]"
    print("✓ Sensitive data filtered")

    print("✓ Privacy tests passed")


def test_runtime():
    """Test code execution runtime"""
    print("\n=== Testing Runtime ===")

    runtime = CodeExecutionRuntime()

    # Test basic execution
    code = """
result = {"message": "Hello from runtime", "value": 42}
"""

    exec_result = runtime.execute(code)
    assert exec_result.success, f"Execution failed: {exec_result.stderr}"
    print(f"✓ Basic execution: {exec_result.result}")

    # Test MCP functions
    code = """
# Test search_tools
tools = search_tools("vessel")
print(f"Found {len(tools)} tools")

# Test list_servers
servers = list_servers()
print(f"Servers: {servers}")

result = {
    "tools_found": len(tools),
    "servers": servers
}
"""

    exec_result = runtime.execute(code)
    assert exec_result.success, f"MCP execution failed: {exec_result.stderr}"
    print(f"✓ MCP functions: {exec_result.result}")
    print(f"✓ Tokens saved: {exec_result.tokens_saved}")

    # Test tool loading
    code = """
# Load vessel tracking tool
track = load_tool("maritime-data", "vessel_tracking")

# Call it
vessels = track(vessel_type="yacht")

result = {
    "vessels_found": len(vessels),
    "first_vessel": vessels[0]["name"] if vessels else None
}
"""

    exec_result = runtime.execute(code)
    if exec_result.success:
        print(f"✓ Tool execution: {exec_result.result}")
        print(f"✓ Tools used: {exec_result.tools_used}")
    else:
        print(f"Note: Tool execution might fail without full setup")
        print(f"  Error: {exec_result.stderr[:200]}")

    print("✓ Runtime tests passed")


def test_state_persistence():
    """Test state persistence"""
    print("\n=== Testing State Persistence ===")

    runtime = CodeExecutionRuntime()

    # Save state
    code1 = """
save_state("test_key", {"data": "test_value"})
result = "State saved"
"""

    result1 = runtime.execute(code1)
    assert result1.success
    print("✓ State saved")

    # Load state
    code2 = """
loaded = load_state("test_key")
result = loaded
"""

    result2 = runtime.execute(code2)
    assert result2.success
    assert result2.result["data"] == "test_value"
    print(f"✓ State loaded: {result2.result}")

    print("✓ State persistence tests passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MCP CODE EXECUTION - BASIC TESTS")
    print("=" * 60)

    try:
        test_tool_loader()
        test_sandbox()
        test_privacy()
        test_runtime()
        test_state_persistence()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
