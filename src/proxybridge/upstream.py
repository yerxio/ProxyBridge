import base64
from .config import Upstream

class UpstreamSelector:
    """Current single-upstream selector; future pool/health switching plugs in here."""
    def __init__(self, upstream: Upstream): self._active = upstream
    @property
    def active(self) -> Upstream: return self._active
    def switch(self, upstream: Upstream) -> None: self._active = upstream

def proxy_authorization(upstream: Upstream) -> str | None:
    if upstream.username is None: return None
    raw = f"{upstream.username}:{upstream.password or ''}".encode()
    return "Basic " + base64.b64encode(raw).decode("ascii")
