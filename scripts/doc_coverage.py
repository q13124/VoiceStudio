#!/usr/bin/env python3
"""
Documentation Coverage Analyzer

Measures documentation completeness across the codebase.

Metrics:
- Public API coverage: Docstrings in public functions/classes
- Module README coverage: README.md in each src/ subdirectory
- User doc completeness: Cross-reference features vs docs
- Code comment ratio: Comments per lines of code

Usage:
    python scripts/doc_coverage.py
    python scripts/doc_coverage.py --language python
    python scripts/doc_coverage.py --language csharp
    python scripts/doc_coverage.py --report
    python scripts/doc_coverage.py --threshold 80

Exit Codes:
    0: Coverage meets threshold
    1: Coverage below threshold
    2: Error occurred
"""

from _env_setup import PROJECT_ROOT, BUILDLOGS_DIR

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Output directory
DOC_COVERAGE_DIR = BUILDLOGS_DIR / "doc_coverage"
DOC_COVERAGE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class DocItem:
    """An item that should be documented."""
    name: str
    kind: str  # function, class, method, module
    file_path: str
    line_number: int
    has_docstring: bool
    docstring_length: int = 0


@dataclass
class CoverageReport:
    """Complete documentation coverage report."""
    language: str
    total_public_items: int
    documented_items: int
    coverage_percent: float
    missing_docs: List[DocItem]
    module_readme_coverage: float
    comment_ratio: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "total_public_items": self.total_public_items,
            "documented_items": self.documented_items,
            "coverage_percent": round(self.coverage_percent, 2),
            "missing_docs": [
                {
                    "name": item.name,
                    "kind": item.kind,
                    "file": item.file_path,
                    "line": item.line_number,
                }
                for item in self.missing_docs[:50]  # Limit to 50
            ],
            "module_readme_coverage": round(self.module_readme_coverage, 2),
            "comment_ratio": round(self.comment_ratio, 2),
        }


class PythonDocAnalyzer:
    """Analyze Python documentation coverage."""
    
    def __init__(self, source_dirs: List[Path]):
        self.source_dirs = source_dirs
        self.items: List[DocItem] = []
        self.total_lines = 0
        self.comment_lines = 0
    
    def analyze(self) -> CoverageReport:
        """Analyze all Python files in source directories."""
        for source_dir in self.source_dirs:
            if source_dir.exists():
                for py_file in source_dir.rglob("*.py"):
                    self._analyze_file(py_file)
        
        documented = sum(1 for item in self.items if item.has_docstring)
        total = len(self.items)
        
        coverage = (documented / total * 100) if total > 0 else 100.0
        comment_ratio = (self.comment_lines / self.total_lines * 100) if self.total_lines > 0 else 0
        
        # Calculate module README coverage
        readme_coverage = self._calculate_readme_coverage()
        
        return CoverageReport(
            language="python",
            total_public_items=total,
            documented_items=documented,
            coverage_percent=coverage,
            missing_docs=[item for item in self.items if not item.has_docstring],
            module_readme_coverage=readme_coverage,
            comment_ratio=comment_ratio,
        )
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            # Count lines and comments
            lines = content.split("\n")
            self.total_lines += len(lines)
            self.comment_lines += sum(1 for line in lines if line.strip().startswith("#"))
            
            # Parse AST
            tree = ast.parse(content)
            rel_path = str(file_path.relative_to(PROJECT_ROOT))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_") or node.name.startswith("__"):
                        if node.name.startswith("__") and node.name.endswith("__"):
                            continue  # Skip dunder methods
                        if node.name.startswith("_") and not node.name.startswith("__"):
                            continue  # Skip private methods
                        
                        docstring = ast.get_docstring(node)
                        self.items.append(DocItem(
                            name=node.name,
                            kind="function",
                            file_path=rel_path,
                            line_number=node.lineno,
                            has_docstring=docstring is not None,
                            docstring_length=len(docstring) if docstring else 0,
                        ))
                
                elif isinstance(node, ast.ClassDef):
                    if not node.name.startswith("_"):
                        docstring = ast.get_docstring(node)
                        self.items.append(DocItem(
                            name=node.name,
                            kind="class",
                            file_path=rel_path,
                            line_number=node.lineno,
                            has_docstring=docstring is not None,
                            docstring_length=len(docstring) if docstring else 0,
                        ))
                        
        # ALLOWED: bare except - File parsing, skip files with errors
        except SyntaxError:
            pass
        # ALLOWED: bare except - File parsing, individual file failure is acceptable
        except Exception:
            pass
    
    def _calculate_readme_coverage(self) -> float:
        """Calculate README coverage for modules."""
        module_dirs = set()
        readme_count = 0
        
        for source_dir in self.source_dirs:
            if source_dir.exists():
                for py_file in source_dir.rglob("*.py"):
                    parent = py_file.parent
                    if parent != source_dir:
                        module_dirs.add(parent)
        
        for module_dir in module_dirs:
            if (module_dir / "README.md").exists() or (module_dir / "readme.md").exists():
                readme_count += 1
        
        return (readme_count / len(module_dirs) * 100) if module_dirs else 100.0


class CSharpDocAnalyzer:
    """Analyze C# documentation coverage."""
    
    # Regex patterns for C# parsing
    CLASS_PATTERN = re.compile(r"^\s*(?:public|internal)\s+(?:partial\s+)?(?:sealed\s+)?(?:abstract\s+)?class\s+(\w+)", re.MULTILINE)
    METHOD_PATTERN = re.compile(r"^\s*(?:public|protected)\s+(?:virtual\s+|override\s+|static\s+|async\s+)*[\w<>\[\],\s]+\s+(\w+)\s*\(", re.MULTILINE)
    XML_DOC_PATTERN = re.compile(r"^\s*///", re.MULTILINE)
    
    def __init__(self, source_dirs: List[Path]):
        self.source_dirs = source_dirs
        self.items: List[DocItem] = []
        self.total_lines = 0
        self.comment_lines = 0
    
    def analyze(self) -> CoverageReport:
        """Analyze all C# files in source directories."""
        for source_dir in self.source_dirs:
            if source_dir.exists():
                for cs_file in source_dir.rglob("*.cs"):
                    self._analyze_file(cs_file)
        
        documented = sum(1 for item in self.items if item.has_docstring)
        total = len(self.items)
        
        coverage = (documented / total * 100) if total > 0 else 100.0
        comment_ratio = (self.comment_lines / self.total_lines * 100) if self.total_lines > 0 else 0
        
        # Calculate README coverage
        readme_coverage = self._calculate_readme_coverage()
        
        return CoverageReport(
            language="csharp",
            total_public_items=total,
            documented_items=documented,
            coverage_percent=coverage,
            missing_docs=[item for item in self.items if not item.has_docstring],
            module_readme_coverage=readme_coverage,
            comment_ratio=comment_ratio,
        )
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single C# file."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            self.total_lines += len(lines)
            
            rel_path = str(file_path.relative_to(PROJECT_ROOT))
            
            # Count comment lines
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                    self.comment_lines += 1
            
            # Find classes
            for match in self.CLASS_PATTERN.finditer(content):
                class_name = match.group(1)
                line_num = content[:match.start()].count("\n") + 1
                
                # Check for XML doc comment above
                has_doc = self._has_xml_doc(lines, line_num - 1)
                
                self.items.append(DocItem(
                    name=class_name,
                    kind="class",
                    file_path=rel_path,
                    line_number=line_num,
                    has_docstring=has_doc,
                ))
            
            # Find public methods
            for match in self.METHOD_PATTERN.finditer(content):
                method_name = match.group(1)
                if method_name in ("if", "while", "for", "switch", "catch"):
                    continue  # Skip control flow keywords
                
                line_num = content[:match.start()].count("\n") + 1
                has_doc = self._has_xml_doc(lines, line_num - 1)
                
                self.items.append(DocItem(
                    name=method_name,
                    kind="method",
                    file_path=rel_path,
                    line_number=line_num,
                    has_docstring=has_doc,
                ))
        # ALLOWED: bare except - File parsing, individual file failure is acceptable
        except Exception:
            pass
    
    def _has_xml_doc(self, lines: List[str], line_index: int) -> bool:
        """Check if there's an XML doc comment above the given line."""
        # Look up to 10 lines above for /// comments
        for i in range(line_index - 1, max(-1, line_index - 10), -1):
            if i < 0:
                break
            stripped = lines[i].strip()
            if stripped.startswith("///"):
                return True
            if stripped and not stripped.startswith("//") and not stripped.startswith("["):
                break  # Hit code or attribute, stop looking
        return False
    
    def _calculate_readme_coverage(self) -> float:
        """Calculate README coverage for project directories."""
        project_dirs = set()
        readme_count = 0
        
        for source_dir in self.source_dirs:
            if source_dir.exists():
                for csproj in source_dir.rglob("*.csproj"):
                    project_dirs.add(csproj.parent)
        
        for project_dir in project_dirs:
            if (project_dir / "README.md").exists() or (project_dir / "readme.md").exists():
                readme_count += 1
        
        return (readme_count / len(project_dirs) * 100) if project_dirs else 100.0


def analyze_combined() -> Dict[str, CoverageReport]:
    """Analyze both Python and C# documentation."""
    results = {}
    
    # Python sources
    python_dirs = [
        PROJECT_ROOT / "app",
        PROJECT_ROOT / "backend",
        PROJECT_ROOT / "tools",
        PROJECT_ROOT / "scripts",
    ]
    python_analyzer = PythonDocAnalyzer(python_dirs)
    results["python"] = python_analyzer.analyze()
    
    # C# sources
    csharp_dirs = [
        PROJECT_ROOT / "src",
    ]
    csharp_analyzer = CSharpDocAnalyzer(csharp_dirs)
    results["csharp"] = csharp_analyzer.analyze()
    
    return results


def format_markdown(reports: Dict[str, CoverageReport]) -> str:
    """Format reports as Markdown."""
    lines = [
        "# Documentation Coverage Report",
        "",
        f"**Generated**: {datetime.now().isoformat()}",
        "",
    ]
    
    for lang, report in reports.items():
        lines.extend([
            f"## {lang.title()} Documentation",
            "",
            f"- **Public Items**: {report.total_public_items}",
            f"- **Documented**: {report.documented_items}",
            f"- **Coverage**: {report.coverage_percent:.1f}%",
            f"- **Module README Coverage**: {report.module_readme_coverage:.1f}%",
            f"- **Comment Ratio**: {report.comment_ratio:.1f}%",
            "",
        ])
        
        if report.missing_docs:
            lines.extend([
                "### Missing Documentation",
                "",
                "| File | Kind | Name | Line |",
                "|------|------|------|------|",
            ])
            for item in report.missing_docs[:30]:  # Top 30
                lines.append(f"| `{item.file_path}` | {item.kind} | `{item.name}` | {item.line_number} |")
            
            if len(report.missing_docs) > 30:
                lines.append(f"| ... | ... | ... | ({len(report.missing_docs) - 30} more) |")
            lines.append("")
    
    # Combined summary
    total_items = sum(r.total_public_items for r in reports.values())
    total_documented = sum(r.documented_items for r in reports.values())
    overall_coverage = (total_documented / total_items * 100) if total_items > 0 else 100.0
    
    lines.extend([
        "## Overall Summary",
        "",
        f"- **Total Public Items**: {total_items}",
        f"- **Total Documented**: {total_documented}",
        f"- **Overall Coverage**: {overall_coverage:.1f}%",
        "",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze documentation coverage")
    parser.add_argument(
        "--language",
        choices=["python", "csharp", "all"],
        default="all",
        help="Language to analyze (default: all)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate full report"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=50.0,
        help="Coverage threshold (default: 50)"
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "markdown", "both"],
        default="both",
        help="Output format (default: both)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Documentation Coverage Analyzer")
    print("=" * 60)
    print()
    
    reports = analyze_combined()
    
    if args.language != "all":
        reports = {args.language: reports[args.language]}
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save outputs
    if args.output_format in ["json", "both"]:
        json_path = DOC_COVERAGE_DIR / f"doc_coverage_{timestamp}.json"
        json_data = {lang: report.to_dict() for lang, report in reports.items()}
        json_path.write_text(json.dumps(json_data, indent=2))
        print(f"JSON saved: {json_path}")
    
    if args.output_format in ["markdown", "both"]:
        md_path = DOC_COVERAGE_DIR / f"doc_coverage_{timestamp}.md"
        md_path.write_text(format_markdown(reports))
        print(f"Markdown saved: {md_path}")
    
    # Print summary
    print()
    print("-" * 60)
    
    overall_coverage = 0.0
    total_weight = 0
    
    for lang, report in reports.items():
        status = "OK" if report.coverage_percent >= args.threshold else "LOW"
        print(f"  {lang.title():10} {report.coverage_percent:5.1f}% ({report.documented_items}/{report.total_public_items}) [{status}]")
        overall_coverage += report.coverage_percent
        total_weight += 1
    
    if total_weight > 0:
        overall_coverage /= total_weight
    
    print("-" * 60)
    print(f"Overall: {overall_coverage:.1f}%")
    print(f"Status: {'PASS' if overall_coverage >= args.threshold else 'FAIL'} (threshold: {args.threshold}%)")
    print()
    
    if overall_coverage < args.threshold:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
