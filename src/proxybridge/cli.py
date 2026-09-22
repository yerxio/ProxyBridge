import argparse, logging, os
from . import __version__
from .config import Upstream
from .server import Server
from .upstream import UpstreamSelector

def parser():
 p=argparse.ArgumentParser(description="将带认证 HTTP 代理桥接为本地普通 HTTP 代理")
 p.add_argument('--listen',default='127.0.0.1:18888',metavar='HOST:PORT')
 p.add_argument('--upstream',default=None,help='http://[USER:PASSWORD@]HOST:PORT')
 p.add_argument('--upstream-file',help='读取第一行上游 URL')
 p.add_argument('--connect-timeout',type=float,default=30)
 p.add_argument('--idle-timeout',type=float,default=120)
 p.add_argument('--log-level',choices=['DEBUG','INFO','WARNING'],default='INFO')
 p.add_argument('--version',action='version',version=__version__); return p

def main(argv=None):
 a=parser().parse_args(argv); raw=a.upstream or os.getenv('PROXYBRIDGE_UPSTREAM')
 if not raw and a.upstream_file: raw=open(a.upstream_file,encoding='utf-8').readline().strip()
 if not raw: parser().error('必须提供 --upstream、--upstream-file 或 PROXYBRIDGE_UPSTREAM')
 try: host,port=a.listen.rsplit(':',1); address=(host,int(port)); upstream=Upstream.parse(raw)
 except (ValueError,OSError) as e: parser().error(str(e))
 logging.basicConfig(level=getattr(logging,a.log_level),format='%(asctime)s %(levelname)s %(message)s')
 logging.info('listening on %s:%s -> %s:%s',host,port,upstream.host,upstream.port)
 try: Server(address,UpstreamSelector(upstream),a.connect_timeout,a.idle_timeout).serve_forever()
 except KeyboardInterrupt: return 0
 return 0
