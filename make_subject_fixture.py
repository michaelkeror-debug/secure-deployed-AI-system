import json
from pathlib import Path
from rights_lookup import key

rows = [{'subject_hash': key('C01'), 'event': i} for i in range(3)]
Path('fixtures').mkdir(exist_ok=True)
Path('fixtures/subjects.json').write_text(json.dumps(rows, indent=2))