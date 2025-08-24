from collections import Counter
import json
from pathlib import Path


content = json.loads(Path("leads.json").read_text())
leads = content.get("_embedded", {}).get("leads", [])
counts = Counter(lead["status_id"] for lead in leads)
print(counts[143])

