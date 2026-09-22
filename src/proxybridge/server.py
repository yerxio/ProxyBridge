import logging, socketserver
from .connection import handle
from .upstream import UpstreamSelector
class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try: handle(self.request,self.server.selector,self.server.connect_timeout,self.server.idle_timeout)
        except Exception as e: logging.warning("request failed: %s",type(e).__name__)
class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address=True; daemon_threads=True
    def __init__(self, address, selector, connect_timeout, idle_timeout):
        super().__init__(address,Handler); self.selector=selector; self.connect_timeout=connect_timeout; self.idle_timeout=idle_timeout
