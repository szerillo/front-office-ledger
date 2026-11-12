# serves ROOT/<site>/ with gzip (like GitHub Pages) and max-age=600
import http.server, os, gzip, sys, functools
ROOT = sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        path = self.translate_path(self.path.split('?')[0])
        if os.path.isdir(path): path = os.path.join(path, 'index.html')
        if not os.path.isfile(path): self.send_error(404); return
        data = open(path, 'rb').read(); ctype = self.guess_type(path)
        if 'gzip' in self.headers.get('Accept-Encoding', '') and any(path.endswith(e) for e in ('.html', '.js', '.json', '.css', '.svg')):
            data = gzip.compress(data, 6); enc = True
        else: enc = False
        self.send_response(200); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(data)))
        if enc: self.send_header('Content-Encoding', 'gzip')
        self.send_header('Cache-Control', 'max-age=600'); self.end_headers(); self.wfile.write(data)
http.server.ThreadingHTTPServer(('127.0.0.1', 8767), functools.partial(H, directory=ROOT)).serve_forever()
