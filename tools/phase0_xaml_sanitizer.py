"""
Phase 0 XAML sanitizer for WinUI 3 build reliability.

Removes XAML constructs that commonly crash WindowsAppSDK XamlCompiler.exe in this repo:
- WPF-style triggers blocks (e.g. <Grid.Triggers>...</Grid.Triggers>, <Style.Triggers>...</Style.Triggers>)
- Popup Placement="..." attribute (not supported by WinUI 3 Popup)
- Window/ContentDialog size attributes in XAML (Width/Height/Background) that have been observed to crash the compiler
- Invalid Thickness composition in Margin/Padding/BorderThickness (comma-separated StaticResource fragments)
- Binding StringFormat (WinUI binding/parser fragility)

This is intentionally conservative and line-based to keep XAML well-formed.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"e:\VoiceStudio\src\VoiceStudio.App")

# Match start/end tags for triggers blocks
TRIGGERS_START_RE = re.compile(r"^\s*<([A-Za-z_][\w\.]*Triggers)\b[^>]*>\s*$")
TRIGGERS_END_RE = re.compile(r"^\s*</([A-Za-z_][\w\.]*Triggers)>\s*$")

# Popup placement attribute (Placement="Bottom" etc)
POPUP_PLACEMENT_ATTR_RE = re.compile(r'\s+Placement\s*=\s*"[^"]*"')

# Window/ContentDialog attribute stripping (compiler fragile with these in this repo)
WINDOW_CD_SIZE_ATTR_RE = re.compile(r'\s+(Width|Height|Background)\s*=\s*"[^"]*"')

# AncestorType=UserControl bindings (WinUI compiler fragile) -> x:Bind
ANCESTOR_USERCONTROL_BINDING_RE = re.compile(
    r"\{Binding\s+([A-Za-z_]\w*)\s*,\s*RelativeSource=\{RelativeSource\s+AncestorType=UserControl\}\s*\}"
)

# Remove Binding StringFormat: {Binding Foo, StringFormat='...'} -> {Binding Foo}
BINDING_STRINGFORMAT_RE = re.compile(
    r"\{Binding\s+([^,}]+)\s*,\s*StringFormat\s*=\s*[^}]+\}"
)

# Fix stray single-quote left behind in bindings: Text="{Binding Foo}'}" -> Text="{Binding Foo}"
# (common artifact after removing StringFormat in this repo)
STRAY_BINDING_QUOTE_BRACE_RE = re.compile(r"(\{[^}]+\})'\}")
STRAY_BINDING_QUOTE_RE = re.compile(r"(\{[^}]+\})'(?=\")")

# Fix broken StringFormat remnants (artifact after stripping StringFormat):
#   Text="{Binding Foo}{0:P0}'}" -> Text="{Binding Foo}"
BROKEN_STRINGFORMAT_FRAGMENT_RE = re.compile(r"(\{Binding\s+[^}]+\})\{0:[^}]+\}'\}")

# Replace invalid Thickness composition that contains StaticResource fragments.
THICKNESS_ATTR_RE = re.compile(r'\b(Margin|Padding|BorderThickness)\s*=\s*"([^"]*)"')


def sanitize_text(text: str) -> tuple[str, int, int]:
    """
    Returns: (new_text, triggers_blocks_removed, popup_placement_removed)
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []

    in_triggers = False
    triggers_depth = 0
    removed_triggers_blocks = 0
    removed_popup_placement = 0
    rewritten_ancestor_bindings = 0
    rewritten_thickness = 0
    rewritten_stringformats = 0
    rewritten_broken_stringformats = 0

    in_window_tag = False
    in_contentdialog_tag = False

    for line in lines:
        # Track when we're inside a <Window ...> or <ContentDialog ...> start tag (may span lines)
        if not in_window_tag and "<Window" in line:
            in_window_tag = True
        if not in_contentdialog_tag and "<ContentDialog" in line:
            in_contentdialog_tag = True

        if in_window_tag or in_contentdialog_tag:
            # Strip Width/Height/Background attributes (even on their own lines)
            if "Width" in line or "Height" in line or "Background" in line:
                new_line, n = WINDOW_CD_SIZE_ATTR_RE.subn("", line)
                if n:
                    line = new_line
            # If line became empty/whitespace, drop it
            if line.strip() == "":
                # keepends already present; dropping line is safe inside tag
                pass

        # End of start tag
        if in_window_tag and ">" in line:
            in_window_tag = False
        if in_contentdialog_tag and ">" in line:
            in_contentdialog_tag = False

        # Trigger block removal (start/end tags)
        if not in_triggers and (".Triggers" in line or "<Style.Triggers" in line):
            if TRIGGERS_START_RE.match(line.strip()):
                in_triggers = True
                triggers_depth = 1
                removed_triggers_blocks += 1
                continue
            # Handle <Style.Triggers>
            if line.strip().startswith("<Style.Triggers"):
                in_triggers = True
                triggers_depth = 1
                removed_triggers_blocks += 1
                continue

        if in_triggers:
            # Increase depth if nested triggers start (rare)
            if TRIGGERS_START_RE.match(line.strip()) or line.strip().startswith(
                "<Style.Triggers"
            ):
                triggers_depth += 1
                continue
            # End triggers
            if TRIGGERS_END_RE.match(line.strip()) or line.strip().startswith(
                "</Style.Triggers"
            ):
                triggers_depth -= 1
                if triggers_depth <= 0:
                    in_triggers = False
                continue
            continue

        # Remove Popup Placement attr wherever it appears on a line
        if "Placement" in line and "<Popup" in line:
            new_line, n = POPUP_PLACEMENT_ATTR_RE.subn("", line)
            if n:
                removed_popup_placement += n
                line = new_line

        # Rewrite {Binding Foo, RelativeSource={RelativeSource AncestorType=UserControl}} -> {x:Bind Foo, Mode=OneWay}
        if (
            "RelativeSource" in line
            and "AncestorType=UserControl" in line
            and "{Binding" in line
        ):
            new_line, n = ANCESTOR_USERCONTROL_BINDING_RE.subn(
                r"{x:Bind \1, Mode=OneWay}", line
            )
            if n:
                rewritten_ancestor_bindings += n
                line = new_line

        # Remove Binding StringFormat (WinUI parser fragile)
        if "StringFormat" in line and "{Binding" in line:
            new_line, n = BINDING_STRINGFORMAT_RE.subn(r"{Binding \1}", line)
            if n:
                rewritten_stringformats += n
                line = new_line

        # Remove stray quote artifact after bindings (can break XAML parsing)
        if "}'" in line and "{" in line and "}" in line:
            new_line, n1 = STRAY_BINDING_QUOTE_BRACE_RE.subn(r"\1", line)
            if n1:
                rewritten_broken_stringformats += n1
                line = new_line

            new_line, n2 = STRAY_BINDING_QUOTE_RE.subn(r"\1", line)
            if n2:
                rewritten_broken_stringformats += n2
                line = new_line

        if "{0:" in line and "{Binding" in line and "}'" in line:
            new_line, n = BROKEN_STRINGFORMAT_FRAGMENT_RE.subn(r"\1", line)
            if n:
                rewritten_broken_stringformats += n
                line = new_line

        # Fix invalid Thickness composition for Margin/Padding/BorderThickness:
        # - Any value that mixes StaticResource fragments with commas: Margin="...,{StaticResource ...},..."
        # - Any "Value" token used where Thickness is expected: Padding="{StaticResource VSQ.Spacing.Value.Large}"
        if "{StaticResource" in line and (
            "Margin=" in line or "Padding=" in line or "BorderThickness=" in line
        ):

            def _fix_thickness(m: re.Match) -> str:
                nonlocal rewritten_thickness
                attr = m.group(1)
                val = m.group(2)
                if ("," in val and "{StaticResource" in val) or (
                    ".Value." in val and "{StaticResource" in val
                ):
                    rewritten_thickness += 1
                    if attr == "Margin":
                        return f'{attr}="0"'
                    if attr == "BorderThickness":
                        return f'{attr}="1"'
                    # Padding
                    return f'{attr}="12"'
                return m.group(0)

            line = THICKNESS_ATTR_RE.sub(_fix_thickness, line)

        if line.strip() != "":
            out.append(line)

    new_text = "".join(out)
    return (
        new_text,
        removed_triggers_blocks,
        removed_popup_placement
        + rewritten_ancestor_bindings
        + rewritten_thickness
        + rewritten_stringformats
        + rewritten_broken_stringformats,
    )


def main() -> int:
    if not ROOT.exists():
        raise SystemExit(f"Root not found: {ROOT}")

    total_files = 0
    changed_files = 0
    total_triggers_blocks = 0
    total_popup_placement = 0

    for path in ROOT.rglob("*.xaml"):
        total_files += 1
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig")

        new_text, trig_blocks, popup_attrs = sanitize_text(text)
        if trig_blocks or popup_attrs:
            total_triggers_blocks += trig_blocks
            total_popup_placement += popup_attrs
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed_files += 1

    print(f"Scanned {total_files} XAML files")
    print(f"Modified {changed_files} files")
    print(f"Removed triggers blocks: {total_triggers_blocks}")
    print(
        f"Removed Popup Placement attrs / rewritten ancestor bindings: {total_popup_placement}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
