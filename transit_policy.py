"""Transit policy: partner URLs must be HTTPS; localhost HTTP is a lab exception."""
from urllib.parse import urlparse
import ssl
import urllib.request

LAB_HOSTS = {'127.0.0.1', 'localhost'}


def transit_ok(url: str, allow_localhost: bool = True) -> bool:
    """Policy check: non-localhost partner URLs must use https."""
    u = urlparse(url)
    if not u.scheme or not u.hostname:
        return False
    if allow_localhost and u.hostname in LAB_HOSTS:
        return True  # HTTP allowed only here, and only for labs
    return u.scheme == 'https'


def tls_handshake_ok(host: str, port: int = 443, timeout: float = 5.0) -> bool:
    """Real TLS check: fetch the server certificate, failing closed on any error."""
    try:
        ssl.get_server_certificate((host, port), timeout=timeout)
        return True
    except Exception:
        return False


def https_get_ok(url: str, timeout: float = 5.0) -> bool:
    """Real HTTPS request; localhost HTTP remains a documented lab exception."""
    if not transit_ok(url):
        return False
    u = urlparse(url)
    if u.hostname in LAB_HOSTS:
        return True
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return 200 <= resp.status < 500
    except Exception:
        return False


if __name__ == '__main__':
    assert transit_ok('https://api.afyaplus.ke/triage') is True
    assert transit_ok('http://127.0.0.1:8000/triage') is True
    assert transit_ok('http://api.afyaplus.ke/triage') is False
    print('transit_policy OK')