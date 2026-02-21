"""Add from __future__ import annotations to test files for Python 3.9 compatibility."""

from pathlib import Path

# Files that need __future__ annotations
files_to_fix = [
    'tests/ui/conftest.py',
    'tests/ui/tracing/websocket_monitor.py',
    'tests/ui/tracing/correlated_tracer.py',
    'tests/ui/tracing/workflow_tracer.py',
    'tests/ui/tracing/audio_integrity.py',
    'tests/ui/tracing/api_monitor.py',
    'tests/ui/fixtures/test_data.py',
    'tests/ui/fixtures/__init__.py',
    'tests/ui/helpers/backend.py',
    'tests/ui/helpers.py',
    'tests/ui/page_objects/base_page.py',
    'tests/unit/backend/api/routes/test_voice.py',
    'tests/performance/test_ui_performance.py',
    'tests/performance/generate_report.py',
    'tests/mocks/llm_mocks.py',
    'tests/e2e/pages/voice_quick_clone.py',
    'tests/e2e/pages/synthesis.py',
    'tests/e2e/pages/project.py',
    'tests/e2e/conftest.py',
    'tests/test_utils.py',
    'tests/test_reporting.py',
    'tests/quality/test_api_endpoints_static.py',
    'tests/regression/audio_comparison.py',
    'tests/integration/test_websocket.py',
    'tests/integration/test_load.py',
    'tests/unit/app/test_json_serialization.py',
    'tests/unit/core/validation/test_optimizer.py',
    'tests/fixtures/mock_backend.py',
    'tests/fixtures/canonical.py',
]

future_import = 'from __future__ import annotations'
fixed = []
already_has = []

for f in files_to_fix:
    path = Path(f)
    if not path.exists():
        continue
    content = path.read_text(encoding='utf-8')
    if future_import in content:
        already_has.append(f)
        continue
    
    lines = content.split('\n')
    insert_idx = 0
    in_docstring = False
    docstring_char = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0 and (stripped.startswith('"""') or stripped.startswith("'''")):
            in_docstring = True
            docstring_char = stripped[:3]
            if stripped.count(docstring_char) >= 2:
                in_docstring = False
                insert_idx = i + 1
            continue
        if in_docstring:
            if docstring_char in stripped:
                in_docstring = False
                insert_idx = i + 1
            continue
        if stripped.startswith('import ') or stripped.startswith('from ') or (stripped and not stripped.startswith('#')):
            insert_idx = i
            break
        insert_idx = i
    
    lines.insert(insert_idx, future_import)
    lines.insert(insert_idx + 1, '')
    path.write_text('\n'.join(lines), encoding='utf-8')
    fixed.append(f)

print(f'Fixed {len(fixed)} files')
print(f'Already had annotation import: {len(already_has)} files')
for f in fixed:
    print(f'  - {f}')
