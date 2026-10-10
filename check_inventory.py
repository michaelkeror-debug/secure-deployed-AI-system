"""Gate: the inventory must cover four datasets and flag the sensitive one."""
import json
import sys
from pathlib import Path

REQUIRED = {'triage_messages', 'jwt_subjects', 'mcp_stock_queries', 'audit_logs'}
FIELDS = ('purpose', 'lawful_basis', 'retention_days', 'special_category')


def main() -> int:
    rows = json.loads(Path('data_inventory.json').read_text())
    names = {r['name'] for r in rows}
    missing = REQUIRED - names
    if missing:
        print('FAIL missing datasets:', sorted(missing))
        return 1
    by = {r['name']: r for r in rows}
    if by['triage_messages'].get('special_category') is not True:
        print('FAIL triage_messages must be special_category true')
        return 1
    for r in rows:
        for k in FIELDS:
            if k not in r:
                print('FAIL', r.get('name'), 'missing', k)
                return 1
    print('inventory OK', len(rows), 'datasets')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
