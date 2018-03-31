#!/usr/bin/env python
import SimpleHTTPServer
import SocketServer
import os
import sys
from sys import argv
from StringIO import StringIO
import glob
try:
    from jinja2 import Template
except:
    os.system('pip install jinja2')
    from jinja2 import Template

PROJ_DIR = os.path.abspath(os.path.dirname(__file__))

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def load_doc(self):
        nav_files = glob.glob(os.path.join(PROJ_DIR, 'docs/user-guide/*'))
        raw_template = open(os.path.join(PROJ_DIR, 'src/index.html')).read()
        doc_body = open(os.path.join(PROJ_DIR, self.path.strip('/'))).read()
        return Template(raw_template).render(doc_body=doc_body, nav=nav_files)

    def serve_doc(self):
        f = StringIO()
        f.write(self.load_doc())
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        self.wfile.write(f.read())
        


    def do_GET(self):
        if self.path == '/':
            self.path = '/docs/user-guide/index.html'
        if self.path.startswith('/docs/'):
            return self.serve_doc()
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)



if __name__ == "__main__":
    port = int(argv[1]) if len(argv) == 2 else 8011
    os.system('open http://127.0.0.1:%s/docs/user-guide/index.html'%port)
    
    server = SocketServer.TCPServer(('0.0.0.0', port), MyRequestHandler)
    server.serve_forever()
