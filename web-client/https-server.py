# taken from http://www.piware.de/2011/01/creating-an-https-server-in-python/
# generate server.xml with the following command:
#    openssl req -new -x509 -keyout secrets/server.pem -out secrets/server.pem -days 365 -nodes
# run as follows:
#    python simple-https-server.py
# then in your browser, visit:
#    https://localhost:4443

import ssl
from http.server import HTTPServer, SimpleHTTPRequestHandler

httpd = HTTPServer(('localhost', 4443), SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(
    httpd.socket, certfile='./secrets/server.pem', server_side=True)
httpd.serve_forever()
