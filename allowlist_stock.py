"""A stub check_stock that only answers for identifiers on the allowlist."""
import json
from pathlib import Path

ALLOWLIST_PATH = Path('clinics_allowlist.json')


def load_known() -> set[str]:
    if not ALLOWLIST_PATH.exists():
        return set()
    data = json.loads(ALLOWLIST_PATH.read_text())
    return {str(x).strip().upper() for x in data.get('clinics', [])}


STOCK = {('KSM-01', 'ORS'): 40, ('VIH-01', 'ORS'): 12, ('HBA-01', 'ORS'): 7}


def check_stock(clinic_id: str, item: str = 'ORS') -> dict:
    known = load_known()
    if not known:
        return {'error': 'empty allowlist', 'code': 500}
    cid = (clinic_id or '').strip().upper()
    if cid not in known:
        return {'error': 'unknown clinic_id', 'code': 400}
    return {'clinic_id': cid, 'item': item, 'qty': STOCK.get((cid, item), 0)}


if __name__ == '__main__':
    ALLOWLIST_PATH.write_text(json.dumps({'clinics': ['KSM-01', 'VIH-01', 'HBA-01']}))
    assert check_stock('KSM-01')['qty'] == 40
    assert check_stock('*')['code'] == 400
    ALLOWLIST_PATH.write_text(json.dumps({'clinics': []}))
    assert check_stock('KSM-01')['code'] == 500
    ALLOWLIST_PATH.write_text(json.dumps({'clinics': ['KSM-01', 'VIH-01', 'HBA-01']}))
    print('allowlist_stock OK')