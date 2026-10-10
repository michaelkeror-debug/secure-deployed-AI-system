"""Fail closed if .env is tracked or a Compose file inlines a secret."""
import re
import subprocess
import sys
from pathlib import Path

COMPOSE_CANDIDATES = ['docker-compose.yml', 'docker-compose.yaml', 'compose.yaml']
COMMENT = re.compile(r'#.*$')


def strip_comments(text: str) -> str:
    """Remove # comments so teaching notes do not trip the scanner."""
    return '\n'.join(COMMENT.sub('', line) for line in text.splitlines())


def env_ignored() -> bool:
    r = subprocess.run(['git', 'check-ignore', '-v', '.env'],
                       capture_output=True, text=True)
    return r.returncode == 0 and bool(r.stdout.strip())


def looks_inlined(text: str) -> bool:
    text = strip_comments(text)
    for key in ('JWT_SECRET', 'OPENAI_API_KEY'):
        for line in text.splitlines():
            if key in line and '${' not in line and 'secrets.' not in line:
                if '"' in line or "'" in line:
                    return True
    return False


def compose_clean() -> bool:
    for name in COMPOSE_CANDIDATES:
        p = Path(name)
        if p.exists() and looks_inlined(p.read_text()):
            return False
    return True


def main() -> int:
    if not env_ignored():
        print('FAIL: .env is not gitignored. Add it, then re-run.')
        return 1
    if not compose_clean():
        print('FAIL: a Compose file looks like it inlines a secret. Use ${JWT_SECRET}.')
        return 1
    print('OK: .env ignored and Compose looks clean')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())