# Data subject rights checklist

- [ ] Access path owner named: Data protection lead, [name to be assigned]
- [ ] Erasure and restriction path owner named: Platform owner, [name to be assigned]
- [ ] Hashed lookup stub exists (`rights_lookup.py`): counts events by peppered subject hash, never content
- [ ] What we will not invent: no fabricated regulator ticket numbers

Notes:
- Erasure is a documented process, not automated. Each erasure appends a counts-only record to `deletion_records.jsonl`, which is never swept.
- Lawful-basis values in `data_inventory.json` are teaching labels, not legal advice.
- No registration or approval number is claimed.