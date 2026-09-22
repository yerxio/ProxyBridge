from dataclasses import dataclass
from urllib.parse import unquote, urlsplit

@dataclass(frozen=True)
class Upstream:
    scheme: str
    host: str
    port: int
    username: str | None = None
    password: str | None = None

    @classmethod
    def parse(cls, value: str) -> "Upstream":
        p = urlsplit(value)
        if p.scheme.lower() != "http":
            raise ValueError("当前仅支持 http 上游代理")
        if not p.hostname or not p.port:
            raise ValueError("上游代理必须是 http://[user:password@]host:port")
        if p.path or p.query or p.fragment:
            raise ValueError("上游代理 URL 不应包含 path/query/fragment")
        return cls(p.scheme.lower(), p.hostname, p.port,
                   unquote(p.username) if p.username else None,
                   unquote(p.password) if p.password else None)
