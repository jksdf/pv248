#!/usr/bin/env python3

import http.server
import socket
import urllib.request
import urllib.error
import json
import sys
import ssl
from pprint import pprint


def _clear_dict(data):
    res = {}
    for key, value in data.items():
        if value is not None:
            if type(value) == type({}):
                res[key] = _clear_dict(value)
            else:
                res[key] = value
    return res


def _create_handler(url):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            new_headers = dict(self.headers)
            if 'Host' in new_headers:
                del new_headers['Host']
            new_request = urllib.request.Request(url=url,
                                                 data=None,
                                                 headers=new_headers,
                                                 method='GET')
            try:
                with urllib.request.urlopen(new_request, timeout=1) as response:
                    self.send_response(200)
                    for hkey, hvalue in response.getheaders():
                        self.send_header(hkey, hvalue)
                    self.end_headers()
                    res_content = response.read().decode(_get_charset(response.getheaders()))
                    return self._return(200, dict(response.getheaders()), res_content)
            except socket.timeout:
                return self._return('timeout')

        def do_POST(self):
            try:
                request = json.loads(self._read_request())
                if request['type'] == 'POST' and ('url' not in request.keys() or 'content' not in request.keys()):
                    raise ValueError
            except:
                return self._return('invalid_json')
            new_request = urllib.request.Request(url=request['url'],
                                                data=request.get('content'),
                                                headers=request['headers'],
                                                method=request.get('type', 'GET'))
            with urllib.request.urlopen(new_request, timeout=request['timeout']) as response:
                content = response.read().decode(_get_charset(response.getheaders()))
                return self._return(code=200, headers=dict(response.getheaders()), contents=content)

        def _read_request(self):
            if 'Content-Length' not in self.headers:
                return ''
            return self.rfile.read(int(self.headers['Content-Length'])).decode(_get_charset(self.headers))

        def _return(self, code, headers=None, contents=None):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            jsonData, contentData = None, None
            try:
                jsonData = json.loads(contents)
            except:
                contentData = contents
            self.wfile.write(bytes(json.dumps(_clear_dict({'code': code,
                                                           'headers': headers,
                                                           'json': jsonData,
                                                           'content': contentData}), indent=2),
                                   'UTF-8'))
            # TODO: respond with different encodings
    return Handler


def _get_charset(headers, default='ISO-8859-1'):
    ct = dict(headers).get('Content-Type')
    if ct is None:
        return default
    header = [i.strip() for i in ct.split(';')]
    for i in header:
        value = [j.strip() for j in i.split('=')]
        if len(value) == 2 and value[0] == 'charset':
            return value[1]
    return default


def run(port, url):
    httpd = http.server.HTTPServer(("", port), _create_handler(url))
    httpd.serve_forever()


if __name__ == '__main__':
    run(int(sys.argv[1]), sys.argv[2])
