#!/usr/bin/env python3
"""
Test runner script for VulnScanner backend.

This script provides convenient commands for running tests with different configurations:
- Unit tests only
- Integration tests only
- All tests with coverage
- Specific test modules or functions
- Performance and load tests

Usage:
    python scripts/test.py --help
    python scripts/test.py unit
    python scripts/test.py integration
    python scripts/test.py coverage
    python scripts/test.py --module test_crawler
    python scripts/test.py --function test_engine_initialization
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(cmd: List[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error running command: {e}")
        return 1


def run_unit_tests() -> int:
    """Run unit tests only."""
    cmd = [
        "python", "-m", "pytest",
        "-m", "unit",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running unit tests")


def run_integration_tests() -> int:
    """Run integration tests only."""
    cmd = [
        "python", "-m", "pytest",
        "-m", "integration",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running integration tests")


def run_all_tests() -> int:
    """Run all tests without coverage."""
    cmd = [
        "python", "-m", "pytest",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running all tests")


def run_coverage_tests() -> int:
    """Run all tests with coverage reporting."""
    cmd = [
        "python", "-m", "pytest",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-fail-under=80",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running tests with coverage")


def run_specific_module(module: str) -> int:
    """Run tests for a specific module."""
    cmd = [
        "python", "-m", "pytest",
        f"tests/{module}",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, f"Running tests for module: {module}")


def run_specific_function(function: str) -> int:
    """Run a specific test function."""
    cmd = [
        "python", "-m", "pytest",
        "-k", function,
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, f"Running test function: {function}")


def run_slow_tests() -> int:
    """Run slow/performance tests."""
    cmd = [
        "python", "-m", "pytest",
        "-m", "slow",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running slow/performance tests")


def run_parallel_tests() -> int:
    """Run tests in parallel using pytest-xdist."""
    cmd = [
        "python", "-m", "pytest",
        "-n", "auto",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running tests in parallel")


def generate_coverage_report() -> int:
    """Generate and open coverage report."""
    # Generate coverage report
    cmd = ["python", "-m", "coverage", "html"]
    result = run_command(cmd, "Generating HTML coverage report")
    
    if result == 0:
        print("\n📊 Coverage report generated at: htmlcov/index.html")
        
        # Try to open the report in browser
        import webbrowser
        try:
            report_path = Path("htmlcov/index.html").absolute()
            webbrowser.open(f"file://{report_path}")
            print("🌐 Opening coverage report in browser...")
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
    
    return result


def lint_code() -> int:
    """Run code linting and formatting checks."""
    commands = [
        (["python", "-m", "ruff", "check", "."], "Running ruff linter"),
        (["python", "-m", "black", "--check", "."], "Checking code formatting with black"),
        (["python", "-m", "isort", "--check-only", "."], "Checking import sorting with isort"),
        (["python", "-m", "mypy", "."], "Running type checking with mypy"),
    ]
    
    total_errors = 0
    for cmd, description in commands:
        result = run_command(cmd, description)
        if result != 0:
            total_errors += 1
    
    return total_errors


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="VulnScanner Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test.py unit                    # Run unit tests only
  python scripts/test.py integration             # Run integration tests only
  python scripts/test.py coverage                # Run all tests with coverage
  python scripts/test.py --module test_crawler   # Run specific module tests
  python scripts/test.py --function test_login   # Run specific test function
  python scripts/test.py slow                    # Run performance tests
  python scripts/test.py parallel                # Run tests in parallel
  python scripts/test.py lint                    # Run code quality checks
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["unit", "integration", "all", "coverage", "slow", "parallel", "lint", "report"],
        default="all",
        help="Test command to run (default: all)"
    )
    
    parser.add_argument(
        "--module",
        help="Run tests for specific module (e.g., test_crawler)"
    )
    
    parser.add_argument(
        "--function",
        help="Run specific test function (e.g., test_login)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    import os
    os.chdir(backend_dir)
    
    print("🧪 VulnScanner Test Runner")
    print(f"📁 Working directory: {backend_dir}")
    
    # Handle specific module or function
    if args.module:
        return run_specific_module(args.module)
    
    if args.function:
        return run_specific_function(args.function)
    
    # Handle commands
    command_map = {
        "unit": run_unit_tests,
        "integration": run_integration_tests,
        "all": run_all_tests,
        "coverage": run_coverage_tests,
        "slow": run_slow_tests,
        "parallel": run_parallel_tests,
        "lint": lint_code,
        "report": generate_coverage_report,
    }
    
    if args.command in command_map:
        exit_code = command_map[args.command]()
        
        if exit_code == 0:
            print(f"\n✅ {args.command.title()} completed successfully!")
        else:
            print(f"\n❌ {args.command.title()} failed with exit code {exit_code}")
        
        return exit_code
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())