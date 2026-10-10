"""Resolve secrets by name from secret_refs.yaml, and refuse to boot without them."""
import os
import sys
from pathlib import Path
import yaml


def main() -> int:
    refs = yaml.safe_load(Path('secret_refs.yaml').read_text())
    jwt = refs['secrets']['jwt_secret']
    env_key = jwt.get('env', 'JWT_SECRET')
    val = os.getenv(env_key) or ''
    if not val.strip():
        print('missing secret:', jwt['name'], file=sys.stderr)
        return 1
    print(f"loaded: {jwt['name']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())