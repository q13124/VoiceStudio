#!/usr/bin/env python3
"""Merge Python and .NET SBOMs into a single file."""

import json
from pathlib import Path
from datetime import datetime, timezone
import uuid

def main():
    buildlogs = Path('.buildlogs/sbom')
    
    # Load Python SBOM
    python_sbom = {}
    python_path = buildlogs / 'python-sbom.json'
    if python_path.exists():
        with open(python_path, encoding='utf-8') as f:
            python_sbom = json.load(f)
    
    # Load .NET SBOM
    dotnet_sbom = {}
    dotnet_path = buildlogs / 'dotnet-sbom.json'
    if dotnet_path.exists():
        with open(dotnet_path, encoding='utf-8') as f:
            dotnet_sbom = json.load(f)
    
    # Merge components
    components = []
    for comp in python_sbom.get('components', []):
        comp['properties'] = comp.get('properties', [])
        comp['properties'].append({'name': 'ecosystem', 'value': 'python'})
        components.append(comp)
        
    for comp in dotnet_sbom.get('components', []):
        comp['properties'] = comp.get('properties', [])
        comp['properties'].append({'name': 'ecosystem', 'value': 'dotnet'})
        components.append(comp)
    
    # Create merged SBOM
    merged = {
        '$schema': 'http://cyclonedx.org/schema/bom-1.5.schema.json',
        'bomFormat': 'CycloneDX',
        'specVersion': '1.5',
        'serialNumber': f'urn:uuid:{uuid.uuid4()}',
        'version': 1,
        'metadata': {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'tools': {
                'components': [
                    {'type': 'application', 'name': 'VoiceStudio SBOM Generator', 'version': '1'},
                    {'type': 'application', 'name': 'cyclonedx-py', 'version': '7.2.1'},
                    {'type': 'application', 'name': 'CycloneDX.NET', 'version': 'dotnet tool'},
                ],
            },
            'component': {
                'type': 'application',
                'name': 'VoiceStudio',
                'version': '1.0.1',
                'description': 'Professional voice synthesis and cloning application',
            },
        },
        'components': components,
    }
    
    # Write merged SBOM
    output_path = buildlogs / 'voicestudio-sbom.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2)
    
    py_count = len(python_sbom.get('components', []))
    net_count = len(dotnet_sbom.get('components', []))
    
    print(f'Merged SBOM created with {len(components)} components')
    print(f'  Python: {py_count}')
    print(f'  .NET: {net_count}')
    print(f'  Output: {output_path}')

if __name__ == '__main__':
    main()
