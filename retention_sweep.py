"""Retention sweeper stub: apply the retention.json rule and record the deletion."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

NOW = 1_724_000_000  # frozen fixture clock, not a production run
RULES = json.loads(Path('retention.json').read_text())
DELETION_LOG = Path('deletion_records.jsonl')


def sweep(src: Path, dest: Path, dataset: str = 'triage_messages', now: int = NOW) -> dict:
    # The deletion record is never an input or an output of a sweep
    if dataset == 'deletion_records' or DELETION_LOG.resolve() in (Path(src).resolve(), Path(dest).resolve()):
        raise ValueError('deletion records are never swept')
    days = RULES.get(dataset, {}).get('days')
    if not days:
        raise ValueError(f'no retention rule for {dataset}')
    cut = now - days * 86400
    kept, dropped = [], []
    for line in Path(src).read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        (kept if row['ts'] >= cut else dropped).append(row)
    Path(dest).write_text(''.join(json.dumps(r) + '\n' for r in kept))
    report = {
        'job_id': str(uuid.uuid4()),
        'run_date': datetime.fromtimestamp(now, timezone.utc).date().isoformat(),
        'clock': 'fixture: frozen NOW, not a production run' if now == NOW else 'live',
        'dataset': dataset,
        'range': {'cut_ts': cut, 'now_ts': now},
        'count_dropped': len(dropped),
        'count_kept': len(kept),
        'rule': f'{days}-day retention for {dataset} (retention.json)',
    }
    with DELETION_LOG.open('a') as f:  # append-only
        f.write(json.dumps(report) + '\n')
    Path('sweep_report.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    src = Path('fixtures/old_logs.jsonl')
    src.parent.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        src.write_text(json.dumps({'ts': NOW - 90 * 86400 - 10, 'id': 'old'}) + '\n'
                       + json.dumps({'ts': NOW - 100, 'id': 'fresh'}) + '\n')
    print(sweep(src, Path('kept.jsonl'), dataset='triage_messages'))

    before = DELETION_LOG.read_text()
    for args in ((DELETION_LOG, Path('x.jsonl')), (src, DELETION_LOG)):
        try:
            sweep(*args)
        except ValueError:
            pass
        else:
            raise AssertionError('sweeper touched the deletion record')
    assert DELETION_LOG.read_text() == before
    print('retention_sweep OK: deletion record untouched')