import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
from urllib.error import HTTPError, URLError
from socket import timeout
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
    
    def try_urlopen(self, request, delay = 1):
        try:
            with urllib.request.urlopen(request, timeout = delay) as response:
                resp_headers = dict(response.getheaders())  
                resp_content = response.read().decode('utf-8')
                
                return self.load_json(response.status, resp_headers, resp_content)
                
        except timeout:
            return {"code" : "timeout"}
        
        except HTTPError as e:
            return {"code" : e.code}
        
        except URLError as e:
            return {"code" : str(e.reason)}
        
    def send_contents(self, out, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(out, indent=4, ensure_ascii = False), 'utf-8'))
        
    def check_url(self, url):
        if url.startswith("http://") or url.startswith("https://"):
            return url
        else:
            return "http://" + url
        
    def do_GET(self):
        headers = dict(self.headers)
        
        url = self.check_url(upstream)
        
        request = urllib.request.Request(url = url, headers = headers, method = "GET")
        
        out_json = self.try_urlopen(request)
        
        self.send_contents(out_json)
        
    def do_POST(self):
        if not "Content-Length" in self.headers:
            out_json = {"code" : "invalid json"}
            self.send_contents(out_json)
            return
        
        content_length = int(self.headers["Content-Length"])
        content = self.rfile.read(content_length)
        out_json = None
        request = None
        
        try:
            request = json.loads(content)
        except:
            pass
        
        if request == None or ("type" in request and request["type"] == "POST" \
                               and ("content" not in request)) \
                               or "url" not in request:
            out_json = {"code" : "invalid json"}
        else:
            url = self.check_url(request["url"])
            if "headers" in request and "content-type" not in request["headers"]:
                    request["headers"]["content-type"] = "application/json"
                    
            new_req = urllib.request.Request(url=url, data=bytes(request["content"], "utf-8") if "content" in request else None, 
                                             headers=request["headers"] if "headers" in request else {}, 
                                             method=request["type"] if "type" in request else "GET")
        
            out_json = self.try_urlopen(new_req, int(request["timeout"] if "timeout" in request else "1"))
        
        self.send_contents(out_json)
        
httpd = HTTPServer(("", int(sys.argv[1])), myHandler)

#httpd.socket = ssl.wrap_socket (httpd.socket, keyfile="key.pem", certfile='cert.pem', server_side=True)

httpd.serve_forever()