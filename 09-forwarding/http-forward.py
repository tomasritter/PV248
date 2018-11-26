import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import socket
import json

port = sys.argv[1]
upstream = sys.argv[2]

class myHandler(BaseHTTPRequestHandler):
    def load_json(self, resp_code, resp_headers, resp_content):
        d = {"code" : resp_code, "headers" : resp_headers}
        try:
            d["json"] = json.loads(resp_content)
        except:
            d["content"] = resp_content
        return d
    
    def try_urlopen(self, request):
        try:
            with urllib.request.urlopen(request, timeout = 1) as response:
                resp_headers = dict(response.getheaders())
                resp_content = response.read()
                
                return self.load_json(response.status, resp_headers, resp_content)
                
        except socket.timeout:
            return {"code" : "timeout"}
        
    def send_contents(self, out, code=200):
        self.send_response(code)
        self.send_header('Connection', 'close' )
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(out, indent=4, ensure_ascii = False), 'UTF-8'))
        
    def do_GET(self):
        headers = dict(self.headers)
        #if 'Host' in headers:
         #   del headers['Host']
        
        request = urllib.request.Request(url = upstream, headers = headers, method = "GET")
        
        out_json = self.try_urlopen(request)
        
        self.send_contents(out_json)
        
    def do_POST(self):
        out_json = None
        content = self.rfile.read()
        request = None
        
        try:
            request = json.loads(content)
        except:
            pass
        
        if request == None or (request["type"] == "POST" and ("url" not in request or "content" not in request)):
            out_json = {"code" : "invalid json"}
            
        else:
            new_req = urllib.request.Request(url=request["url"], data=request["content"], headers=request["headers"],
                                                    method=request["type"] if "type" in request else "GET")
        
            out_json = self.try_urlopen(new_req)
        
        self.send_contents(out_json)
        
httpd = HTTPServer(("", int(sys.argv[1])), myHandler)

#httpd.socket = ssl.wrap_socket (httpd.socket, keyfile="key.pem", certfile='cert.pem', server_side=True)

httpd.serve_forever()