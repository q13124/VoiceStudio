#!/usr/bin/env python3
"""
Extract all pending brainstormer ideas (non-implemented) from BRAINSTORMER_IDEAS.md
"""

import re
import sys


def extract_pending_ideas(input_file, output_file):
    """Extract all ideas that are not marked as implemented."""

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split content by idea headers
    # Pattern: ## IDEA <number>: <title> [optional status]
    idea_pattern = r"## IDEA (\d+):(.*?)(?=## IDEA \d+:|$)"

    ideas = re.finditer(idea_pattern, content, re.DOTALL)

    pending_ideas = []
    implemented_ids = set()

    # First pass: identify implemented ideas
    for match in re.finditer(idea_pattern, content, re.DOTALL):
        idea_id = int(match.group(1))
        idea_content = match.group(0)
        if "✅ IMPLEMENTED" in idea_content:
            implemented_ids.add(idea_id)

    # Second pass: extract pending ideas
    for match in re.finditer(idea_pattern, content, re.DOTALL):
        idea_id = int(match.group(1))
        idea_content = match.group(0)

        if idea_id not in implemented_ids:
            pending_ideas.append((idea_id, idea_content))

    # Sort by idea ID
    pending_ideas.sort(key=lambda x: x[0])

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Pending Brainstormer Ideas - VoiceStudio Quantum+\n")
        f.write("## All Non-Implemented Ideas\n\n")
        f.write(f"**Total Pending Ideas:** {len(pending_ideas)}\n")
        f.write(f"**Extracted:** {len(pending_ideas)} ideas\n")
        f.write(f"**Implemented Ideas Excluded:** {len(implemented_ids)}\n\n")
        f.write("---\n\n")

        for idea_id, idea_content in pending_ideas:
            f.write(idea_content)
            f.write("\n\n---\n\n")

    print(f"Extracted {len(pending_ideas)} pending ideas")
    print(f"Excluded {len(implemented_ids)} implemented ideas")
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    input_file = r"E:\VoiceStudio\docs\governance\BRAINSTORMER_IDEAS.md"
    output_file = r"E:\VoiceStudio\docs\governance\PENDING_BRAINSTORMER_IDEAS.md"

    extract_pending_ideas(input_file, output_file)
