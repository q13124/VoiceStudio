"""
Plugin Test Command.

Runs plugin tests using pytest.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import click


def find_test_directory(plugin_dir: Path) -> Optional[Path]:
    """Find the tests directory in a plugin."""
    # Standard locations
    for name in ["tests", "test"]:
        test_dir = plugin_dir / name
        if test_dir.exists() and test_dir.is_dir():
            return test_dir
    
    return None


def find_test_files(plugin_dir: Path) -> List[Path]:
    """Find all test files in a plugin."""
    test_files = []
    
    # Check tests directory
    test_dir = find_test_directory(plugin_dir)
    if test_dir:
        test_files.extend(test_dir.glob("test_*.py"))
        test_files.extend(test_dir.glob("*_test.py"))
    
    # Also check for test files in root
    test_files.extend(plugin_dir.glob("test_*.py"))
    
    return sorted(set(test_files))


def run_pytest(
    plugin_dir: Path,
    coverage: bool = False,
    verbose: bool = False,
    markers: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> int:
    """
    Run pytest on the plugin.
    
    Returns:
        Exit code from pytest
    """
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
        ])
    
    # Add markers filter
    if markers:
        cmd.extend(["-m", markers])
    
    # Add extra arguments
    if extra_args:
        cmd.extend(extra_args)
    
    # Add test directory
    test_dir = find_test_directory(plugin_dir)
    if test_dir:
        cmd.append(str(test_dir))
    else:
        # Run from plugin directory
        cmd.append(str(plugin_dir))
    
    # Run pytest
    result = subprocess.run(
        cmd,
        cwd=plugin_dir,
        env={**os.environ, "PYTHONPATH": str(plugin_dir)},
    )
    
    return result.returncode


def check_pytest_installed() -> bool:
    """Check if pytest is installed."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_coverage_installed() -> bool:
    """Check if pytest-cov is installed."""
    try:
        subprocess.run(
            [sys.executable, "-c", "import pytest_cov"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@click.command("test")
@click.argument(
    "path",
    type=click.Path(exists=True),
    default=".",
)
@click.option(
    "--coverage",
    is_flag=True,
    help="Collect test coverage.",
)
@click.option(
    "-m", "--markers",
    help="Only run tests matching the given markers.",
)
@click.option(
    "-k", "--keyword",
    help="Only run tests matching the given keyword expression.",
)
@click.option(
    "--failfast", "-x",
    is_flag=True,
    help="Stop on first failure.",
)
@click.option(
    "--last-failed",
    is_flag=True,
    help="Re-run only tests that failed last time.",
)
@click.option(
    "--install-deps",
    is_flag=True,
    help="Install test dependencies before running.",
)
@click.pass_context
def test_command(
    ctx: click.Context,
    path: str,
    coverage: bool,
    markers: Optional[str],
    keyword: Optional[str],
    failfast: bool,
    last_failed: bool,
    install_deps: bool,
) -> None:
    """
    Run plugin tests.
    
    Runs pytest on the plugin at PATH (defaults to current directory).
    Requires pytest to be installed.
    
    Examples:
    
        voicestudio-plugin test
        
        voicestudio-plugin test ./my-plugin --coverage
        
        voicestudio-plugin test -k "test_init"
        
        voicestudio-plugin test -m "not slow"
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)
    
    plugin_path = Path(path).resolve()
    
    # Check for test directory or files
    test_dir = find_test_directory(plugin_path)
    test_files = find_test_files(plugin_path)
    
    if not test_dir and not test_files:
        raise click.ClickException(
            "No test directory or test files found. "
            "Create a 'tests/' directory with test_*.py files."
        )
    
    # Install dependencies if requested
    if install_deps:
        if not quiet:
            click.echo("Installing test dependencies...")
        
        # Try to install from setup.py or pyproject.toml
        setup_py = plugin_path / "setup.py"
        pyproject = plugin_path / "pyproject.toml"
        
        if setup_py.exists() or pyproject.exists():
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
                cwd=plugin_path,
                capture_output=not verbose,
            )
            if result.returncode != 0:
                click.echo(click.style("Warning: Failed to install dev dependencies", fg="yellow"))
        else:
            # Just install pytest
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"],
                capture_output=not verbose,
            )
    
    # Check pytest is installed
    if not check_pytest_installed():
        raise click.ClickException(
            "pytest is not installed. "
            "Run 'pip install pytest pytest-asyncio' or use --install-deps."
        )
    
    # Check coverage if requested
    if coverage and not check_coverage_installed():
        raise click.ClickException(
            "pytest-cov is not installed for coverage. "
            "Run 'pip install pytest-cov' or use --install-deps."
        )
    
    # Build extra arguments
    extra_args = []
    
    if keyword:
        extra_args.extend(["-k", keyword])
    
    if failfast:
        extra_args.append("-x")
    
    if last_failed:
        extra_args.append("--lf")
    
    if not quiet:
        test_count = len(test_files)
        click.echo(f"Running tests for plugin at: {plugin_path}")
        click.echo(f"Found {test_count} test file(s)")
        click.echo()
    
    # Run pytest
    exit_code = run_pytest(
        plugin_path,
        coverage=coverage,
        verbose=verbose,
        markers=markers,
        extra_args=extra_args,
    )
    
    # Report results
    if exit_code == 0:
        if not quiet:
            click.echo()
            click.echo(click.style("[OK] All tests passed", fg="green"))
        
        if coverage and not quiet:
            htmlcov = plugin_path / "htmlcov" / "index.html"
            if htmlcov.exists():
                click.echo(f"\nCoverage report: {htmlcov}")
    else:
        if not quiet:
            click.echo()
            click.echo(click.style("[X] Tests failed", fg="red"))
        sys.exit(exit_code)
