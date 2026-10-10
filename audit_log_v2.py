"""Audit trail: redact first, then hash, then append one JSON line."""
import hashlib
import json
import re
import time
import uuid
from pathlib import Path

LOG = Path('logs/audit.jsonl')

BEARER = re.compile(r'Bearer\s+\S+', re.I)
# 8-digit national ID, not a 7-to-10 catch-all: that eats timestamps
KENYA_ID = re.compile(r'\b\d{8}\b')
PHONE = re.compile(r'(?:\+254|0)7\d{8}\b')
# M-Pesa code: a letter then nine alphanumerics, so a 10-digit epoch never matches
MPESA = re.compile(r'\b[A-Z][A-Z0-9]{9}\b')


def redact(text: str) -> str:
    text = BEARER.sub('Bearer [REDACTED]', text)
    text = PHONE.sub('[REDACTED_PHONE]', text)
    text = MPESA.sub('[REDACTED_MPESA]', text)
    text = KENYA_ID.sub('[REDACTED_ID]', text)
    return text


def audit(actor: str, action: str, resource: str, outcome: str,
          payload: str | None = None, trace_id: str | None = None) -> dict:
    """outcome is 'ok', 'denied' or 'error'. actor is a role or user id, never a token."""
    clean = redact(payload or '')                      # 1) redact
    row = {
        'ts': int(time.time()),
        'trace_id': trace_id or uuid.uuid4().hex[:16],
        'actor': actor,
        'action': action,
        'resource': resource,
        'outcome': outcome,
        'payload_sha': hashlib.sha256(clean.encode()).hexdigest()[:16],  # 2) hash
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a') as f:                           # 3) append
        f.write(json.dumps(row) + '\n')
    return row


if __name__ == '__main__':
    LOG = Path('evidence/deliverable 3/audit_sample.jsonl')          # sample goes to evidence/
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text('')

    raw = ('id 12345678 phone 0712345678 code SH45K7L9M2 '
           'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.aaa')
    row = audit('partner_clinic', 'check_stock', 'C01', 'ok', raw)
    blob = LOG.read_text()

    # Nothing sensitive reaches disk
    for secret in ('12345678', '0712345678', 'SH45K7L9M2', 'eyJhbGci'):
        assert secret not in blob, secret
    # Required fields are present
    for key in ('ts', 'trace_id', 'actor', 'action', 'resource', 'outcome', 'payload_sha'):
        assert key in row, key
    # Identical payloads correlate
    assert audit('partner_clinic', 'check_stock', 'C01', 'ok', raw)['payload_sha'] == row['payload_sha']
    # A ten-digit epoch timestamp survives redaction
    assert redact('ts 1724000000 event') == 'ts 1724000000 event'
    print('audit_log OK')
    print(blob.splitlines()[0])