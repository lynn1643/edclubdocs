#!/usr/bin/env python
import SimpleHTTPServer
import SocketServer
import os
import sys
from sys import argv
from StringIO import StringIO
from ruamel.yaml import YAML
import glob
try:
    from jinja2 import Template
except:
    os.system('pip install jinja2')
    from jinja2 import Template

PROJ_DIR = os.path.abspath(os.path.dirname(__file__))
yaml = YAML(typ='safe')

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def load_doc(self):
        raw_template = open(os.path.join(PROJ_DIR, 'src/index.html')).read()
        doc_body = open(os.path.join(PROJ_DIR, self.path.strip('/'))).read()
        doc_body = Template(doc_body).render(EDC_SRC="/src/", EDC_DOCS="/docs/")

        try:
            menu = yaml.load(file(os.path.join(PROJ_DIR, 'src/user-guide.yaml')).read())
        except Exception as e:
            doc_body = "<h4>YAML Exception:</h4><p class='doc-warn'>%s</p>" % e
            menu = []
            
        navbar = {}
        def traverse_menu(menu):
            has_active = False
            for item in menu:
                item['path'] = "/docs/%s" % item['path']
                item['active'] = ''
                if self.path == item['path']:
                    item['active'] = 'active'
                    navbar['current'] = self.path
                    has_active = True
                else:
                    if navbar.get('current'):
                        if not navbar.get('next'):
                            navbar['next'] = item['path']
                    else:
                        navbar['prev'] = item['path']
                if 'subtopics' in item:
                    if traverse_menu(item['subtopics']):
                        item['active'] = 'active has-active'
                        has_active = True
            return has_active

        traverse_menu(menu)
        return Template(raw_template).render(doc_body=doc_body, navbar=navbar, menu=menu, EDC_SRC="/src/", EDC_DOCS="/docs/")

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
