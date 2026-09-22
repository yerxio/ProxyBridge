import select, socket
from urllib.parse import urlsplit
from .upstream import UpstreamSelector, proxy_authorization

MAX_HEADER = 64 * 1024
BUFFER = 256 * 1024

def read_headers(sock):
    data = bytearray()
    while b"\r\n\r\n" not in data:
        if len(data) >= MAX_HEADER: raise ValueError("HTTP headers too large")
        chunk = sock.recv(4096)
        if not chunk: raise ConnectionError("client closed before headers")
        data.extend(chunk)
    head, rest = bytes(data).split(b"\r\n\r\n", 1)
    lines = head.decode("latin-1").split("\r\n")
    if len(lines[0].split(" ", 2)) != 3: raise ValueError("invalid request line")
    return lines[0], lines[1:], rest

def headers_for(line, headers, auth, connection):
    out=[]
    for h in headers:
        name=h.split(":",1)[0].strip().lower() if ":" in h else ""
        if name in {"proxy-authorization","proxy-connection","connection"}: continue
        out.append(h)
    if auth: out.append("Proxy-Authorization: " + auth)
    out.append("Connection: " + connection)
    return ("\r\n".join([line,*out,"",""])).encode("latin-1")

def relay(a, b, idle_timeout):
    a.setblocking(False); b.setblocking(False); peer={a:b,b:a}; pending={a:bytearray(),b:bytearray()}; reading={a,b}
    while reading or any(pending.values()):
        readable,writable,_=select.select(list(reading),[x for x in (a,b) if pending[x]],[],idle_timeout)
        if not readable and not writable: return
        for dst in writable:
            try: sent=dst.send(pending[dst]); del pending[dst][:sent]
            except (BlockingIOError,InterruptedError): pass
        for src in readable:
            try: data=src.recv(min(65536, BUFFER-len(pending[peer[src]])))
            except (BlockingIOError,InterruptedError): continue
            if data: pending[peer[src]].extend(data)
            else: reading.remove(src)

def handle(client, selector, connect_timeout, idle_timeout):
    client.settimeout(connect_timeout); upstream_sock=None
    try:
        line, headers, rest = read_headers(client); method,target,_=line.split(" ",2); connect=method.upper()=="CONNECT"
        u=selector.active; upstream_sock=socket.create_connection((u.host,u.port),connect_timeout); auth=proxy_authorization(u)
        if connect:
            upstream_sock.sendall(headers_for(line,headers,auth,"Keep-Alive"))
            response=read_headers(upstream_sock)[0]
            code=int(response.split(" ",2)[1]); client.sendall((response+"\r\n\r\n").encode("latin-1"))
            if code != 200: return
        else:
            upstream_sock.sendall(headers_for(line,headers,auth,"close")+rest)
        relay(client,upstream_sock,idle_timeout)
    finally:
        for s in (client,upstream_sock):
            if s:
                try: s.close()
                except OSError: pass
