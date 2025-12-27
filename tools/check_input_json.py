import json
import sys

with open(sys.argv[1], "r", encoding="utf-8-sig") as f:
    d = json.load(f)

pages = d.get("Pages", [])
print(f"Total Pages in input.json: {len(pages)}")
if pages:
    print("\nFirst 10 pages:")
    for p in pages[:10]:
        print(f"  {p.get('File', '?')}")
