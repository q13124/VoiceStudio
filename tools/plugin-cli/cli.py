"""
VoiceStudio Plugin CLI - Main entry point.

Usage:
    voicestudio-plugin init <name> [--template=<template>]
    voicestudio-plugin validate [<path>]
    voicestudio-plugin test [<path>] [--coverage]
    voicestudio-plugin pack [<path>] [--output=<output>]
    voicestudio-plugin sign <package> [--key=<key>]
    voicestudio-plugin certify <package> [--level=<level>]
    voicestudio-plugin cert-info <result_file>
    voicestudio-plugin publish <package> [--catalog=<url>]
    voicestudio-plugin lock [--output=<output>]
    voicestudio-plugin lock-add <plugin_id> <version>
    voicestudio-plugin lock-remove <plugin_id>
    voicestudio-plugin lock-export <output>
    voicestudio-plugin lock-import <input>
    voicestudio-plugin lock-plan
    voicestudio-plugin benchmark <plugin_id> [-n <iterations>] [-o <output>]
    voicestudio-plugin benchmark-compare <baseline> <current>
    voicestudio-plugin benchmark-report <results_file> [-f <format>]
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

# Handle both package and script execution
try:
    from . import __version__
    from .commands import benchmark, certify, init, lock, pack, publish, sign, test, validate
except ImportError:
    # Running as script
    __version__ = "1.0.0"
    from commands import benchmark, certify, init, lock, pack, publish, sign, test, validate


@click.group()
@click.version_option(version=__version__, prog_name="voicestudio-plugin")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output.")
@click.option("-q", "--quiet", is_flag=True, help="Suppress non-error output.")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """VoiceStudio Plugin CLI - Tools for plugin development."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


# Register subcommands
cli.add_command(init.init_command, name="init")
cli.add_command(validate.validate_command, name="validate")
cli.add_command(test.test_command, name="test")
cli.add_command(pack.pack_command, name="pack")
cli.add_command(sign.sign_command, name="sign")
cli.add_command(certify.certify_command, name="certify")
cli.add_command(certify.cert_info_command, name="cert-info")
# Lockfile commands (Phase 5C M4)
cli.add_command(lock.lock_command, name="lock")
cli.add_command(lock.validate_command, name="lock-validate")
cli.add_command(lock.lock_add_command, name="lock-add")
cli.add_command(lock.lock_remove_command, name="lock-remove")
cli.add_command(lock.lock_export_command, name="lock-export")
cli.add_command(lock.lock_import_command, name="lock-import")
cli.add_command(lock.lock_plan_command, name="lock-plan")
cli.add_command(publish.publish_command, name="publish")
# Benchmark commands (Phase 5D M1)
cli.add_command(benchmark.benchmark_command, name="benchmark")
cli.add_command(benchmark.benchmark_compare_command, name="benchmark-compare")
cli.add_command(benchmark.benchmark_report_command, name="benchmark-report")


def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
