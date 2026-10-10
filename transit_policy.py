"""Transit policy: partner URLs must be HTTPS; localhost HTTP is a lab exception."""
from urllib.parse import urlparse, urljoin
import urllib.error
import urllib.request
import ssl
import urllib.request
import socket

LAB_HOSTS = {'127.0.0.1', 'localhost'}


def transit_ok(url: str, allow_localhost: bool = True) -> bool:
    """Policy check: non-localhost partner URLs must use https."""
    u = urlparse(url)
    if not u.scheme or not u.hostname:
        return False
    if allow_localhost and u.hostname in LAB_HOSTS:
        return True  # HTTP allowed only here, and only for labs
    return u.scheme == 'https'


def tls_handshake_ok(host, port=443, timeout=5.0):
    ctx = ssl.create_default_context()  # verifies chain and hostname
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            with ctx.wrap_socket(s, server_hostname=host):
                return True
    except Exception:
        return False


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Stop urllib following redirects on its own, so each hop is policy-checked."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def https_get_ok(url: str, timeout: float = 5.0, max_redirects: int = 3,
                 allow_localhost: bool = False) -> bool:
    """Real HTTPS GET. Every redirect hop must pass transit_ok, or the check fails closed.

    Only a 2xx final response counts as OK. Localhost HTTP is a lab exception
    and makes no network request.
    """
    opener = urllib.request.build_opener(_NoRedirect)
    for _ in range(max_redirects + 1):
        if not transit_ok(url, allow_localhost=allow_localhost):
            return False
        if allow_localhost and urlparse(url).hostname in LAB_HOSTS:
            return True
        try:
            with opener.open(url, timeout=timeout) as resp:
                return 200 <= resp.status < 300
        except urllib.error.HTTPError as e:
            if 300 <= e.code < 400 and e.headers.get('Location'):
                url = urljoin(url, e.headers['Location'])  # re-checked at top of loop
                continue
            return False
        except Exception:
            return False
    return False  # too many redirects
    

if __name__ == '__main__':
    assert transit_ok('ftp://api.afyaplus.ke') is False
    assert transit_ok('https://') is False
    assert transit_ok('http://localhost.evil.com/x') is False   # lookalike host
    assert transit_ok('http://127.0.0.1:8000', allow_localhost=False) is False
    assert transit_ok('https://api.afyaplus.ke/triage') is True
    assert transit_ok('http://127.0.0.1:8000/triage') is True
    assert transit_ok('http://api.afyaplus.ke/triage') is False
    print('transit_policy OK')