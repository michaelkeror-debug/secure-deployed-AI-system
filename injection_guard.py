"""Refuse instruction-like user text at the boundary, before any model or tool call."""
OVERRIDE_PHRASES = (
    'ignore previous instructions',
    'ignore all instructions',
    'you are now',
    'reveal the system prompt',
    'print your secret',
)


def looks_like_override(message: str) -> bool:
    """Substring match on override phrases, not a true prefix check."""
    m = message.strip().lower()
    return any(p in m for p in OVERRIDE_PHRASES)


def triage_or_reject(message: str) -> dict:
    if looks_like_override(message):
        return {'error': 'rejected', 'code': 400}
    return {'ok': True, 'message': message}


if __name__ == '__main__':
    assert triage_or_reject('Fever two days')['ok'] is True
    assert triage_or_reject('Ignore previous instructions')['code'] == 400
    # False-positive guard: legitimate pharmacy wording must still be allowed
    assert triage_or_reject('ignore previous advice from the pharmacy')['ok'] is True
    print('injection_guard OK') 