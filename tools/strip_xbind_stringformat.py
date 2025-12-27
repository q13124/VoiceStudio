"""
Strip unsupported `StringFormat=...` clauses from `{x:Bind ...}` markup.

Some WindowsAppSDK XAML compiler versions crash when encountering `StringFormat`
inside `x:Bind`. This script performs a mechanical, safe rewrite:
  Text="{x:Bind Foo, Mode=OneWay, StringFormat='X {0}'}"
becomes:
  Text="{x:Bind Foo, Mode=OneWay}"

It does NOT touch classic `{Binding ... StringFormat=...}`.
"""

from __future__ import annotations

import re
from pathlib import Path


def main() -> int:
    root = Path(r"e:\VoiceStudio\src\VoiceStudio.App")
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")

    # Match StringFormat within a single {x:Bind ...} expression on one line.
    # Handles either single-quoted or double-quoted StringFormat values.
    pattern = re.compile(r"(\{x:Bind[^}]*?),\s*StringFormat=(\"[^\"]*\"|'[^']*')")

    total_replacements = 0
    changed_files: list[Path] = []

    for path in root.rglob("*.xaml"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig")

        new_text, n = pattern.subn(r"\1", text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            total_replacements += n
            changed_files.append(path)

    print(
        f"Removed StringFormat from x:Bind: {total_replacements} replacements "
        f"across {len(changed_files)} files"
    )
    for p in changed_files[:25]:
        print(f"- {p}")
    if len(changed_files) > 25:
        print(f"... and {len(changed_files) - 25} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
