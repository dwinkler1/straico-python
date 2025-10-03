#!/usr/bin/env python3
"""
Test script to verify the Straico API package installation.
"""

import sys
import subprocess
import os


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print()

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

        if result.stdout:
            print("Output:")
            print(result.stdout)

        if result.stderr and result.returncode != 0:
            print("Errors:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ SUCCESS")
            return True
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all installation tests."""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     Straico API Package Installation & Functionality Tests     ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    tests = []

    # Test 1: Package installation
    tests.append(run_command("pip show straico-api", "Package installation check"))

    # Test 2: Python imports
    tests.append(
        run_command(
            'python -c "from straico_api import StraicoClient, LoadingAnimation, __version__; '
            "print(f'Package version: {__version__}'); "
            "print(f'StraicoClient available: {StraicoClient is not None}'); "
            "print(f'LoadingAnimation available: {LoadingAnimation is not None}')\"",
            "Python imports",
        )
    )

    # Test 3: CLI command availability
    tests.append(run_command("which straico-api", "CLI command location"))

    # Test 4: CLI help
    tests.append(run_command("straico-api --help", "CLI help command"))

    # Test 5: Client initialization
    tests.append(
        run_command(
            'python -c "from straico_api import StraicoClient; '
            "client = StraicoClient(api_key='test-key'); "
            "print(f'Client initialized: {client is not None}'); "
            "print(f'API version: {client.api_version}'); "
            "print(f'Base URL: {client.base_url}')\"",
            "Client initialization",
        )
    )

    # Test 6: Quantity validation
    tests.append(
        run_command(
            'python -c "from straico_api import StraicoClient; '
            "client = StraicoClient(api_key='test'); "
            "result = client.chat('test', quantity=5, show_animation=False); "
            "assert not result.get('success'), 'Should fail validation'; "
            "assert 'Quantity must be between 1 and 4' in result.get('error', ''), 'Wrong error message'; "
            "print('Validation working: ', result.get('error'))\"",
            "Quantity validation (invalid value)",
        )
    )

    # Test 7: Valid quantity
    tests.append(
        run_command(
            'python -c "from straico_api import StraicoClient; '
            "client = StraicoClient(api_key='test'); "
            "result = client.chat('test', quantity=2, show_animation=False); "
            "error = result.get('error', ''); "
            "assert 'Quantity must be between 1 and 4' not in error, f'Should accept valid quantity: {error}'; "
            "print('Valid quantity accepted (2)')\"",
            "Quantity validation (valid value)",
        )
    )

    # Test 8: List models method
    tests.append(
        run_command(
            'python -c "from straico_api import StraicoClient; '
            "client = StraicoClient(api_key='test'); "
            "assert hasattr(client, 'get_models'), 'get_models method missing'; "
            "assert hasattr(client, 'find_similar_models'), 'find_similar_models method missing'; "
            "print('All client methods available')\"",
            "Client methods availability",
        )
    )

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(tests)
    total = len(tests)

    print(f"Tests passed: {passed}/{total}")
    print()

    if passed == total:
        print("🎉 All tests passed! Package is working correctly.")
        print()
        print("✅ Package installed successfully")
        print("✅ Python imports working")
        print("✅ CLI command available")
        print("✅ Client initialization working")
        print("✅ Quantity validation working")
        print("✅ All methods available")
        print()
        print("📦 The package is ready to use!")
        print()
        print("Try it out:")
        print("  export STRAICO_API_KEY='your-api-key'")
        print("  straico-api 'Hello, world!'")
        print()
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed.")
        print()
        print("Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
