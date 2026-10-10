"""Access-request sketch: count events for a peppered subject hash, never content."""
import hashlib
import hmac
import json
import os
from pathlib import Path


def pepper() -> bytes:
    val = os.getenv('SUBJECT_PEPPER') or ''
    if not val.strip():
        raise SystemExit('missing SUBJECT_PEPPER')
    return val.encode()


def key(clinic_id: str) -> str:
    cid = clinic_id.strip().upper()  # same normalisation as logistics_mcp.py
    return hmac.new(pepper(), cid.encode(), hashlib.sha256).hexdigest()[:16]

def lookup(clinic_id: str, path: str = 'fixtures/subjects.json') -> dict:
    want = key(clinic_id)
    rows = json.loads(Path(path).read_text())
    n = sum(1 for r in rows if r.get('subject_hash') == want)
    return {'found': n > 0, 'n_events': n}


if __name__ == '__main__':
    # The fixture is shipped statically. Do not regenerate it here.
    path = Path('fixtures/subjects.json')
    assert path.exists(), 'missing fixtures/subjects.json (shipped static fixture)'
    found = lookup('C01')
    absent = lookup('C05')
    assert found == {'found': True, 'n_events': 3}, found
    assert absent == {'found': False, 'n_events': 0}, absent
    print(found)
    print(absent)