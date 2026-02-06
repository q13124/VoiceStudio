from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.onboarding.core.assembler import OnboardingAssembler


def _ensure_utf8_stdout() -> None:
    """Ensure stdout can handle UTF-8 for emoji/unicode in prompts."""
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    # ALLOWED: bare except - Best effort UTF-8 stdout config
    except Exception:
        pass


def main(argv=None) -> int:
    _ensure_utf8_stdout()
    
    parser = argparse.ArgumentParser(prog="onboard", description="Generate onboarding packet")
    parser.add_argument("--role", required=True, help="Role id or alias (e.g., 4, core-platform)")
    parser.add_argument("--output", "-o", help="Write onboarding packet to file")
    parser.add_argument("--full-guide", action="store_true", help="Include full role guide")
    args = parser.parse_args(argv)

    assembler = OnboardingAssembler()
    packet = assembler.assemble(args.role, include_full_guide=bool(args.full_guide))
    content = assembler.render(packet)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
    else:
        # Use sys.stdout.buffer for direct UTF-8 output if reconfigure failed
        try:
            print(content)
        except UnicodeEncodeError:
            sys.stdout.buffer.write(content.encode('utf-8'))
            sys.stdout.buffer.write(b'\n')
    return 0


if __name__ == "__main__":
    sys.exit(main())
