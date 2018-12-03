#!/usr/bin/env python3

import http.server
import json
import re
import socket
import sys
import urllib.error
from pprint import pprint
import logging

import OpenSSL.SSL
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _clear_dict(data):
    res = {}
    for key, value in data.items():
        if value is not None:
            if type(value) == type({}):
                res[key] = _clear_dict(value)
            else:
                res[key] = value
    return res

def host_to_url(host, protocol='https'):
    parsed_url = urllib.parse.urlparse(host)
    if not parsed_url.scheme:
        url = protocol + '://' + host
        parsed_url = urllib.parse.urlparse(url)
    return parsed_url

def _create_handler(url, default_scheme='http'):
    logger.info('url: %s', url)
    parsed_url = host_to_url(url, default_scheme)

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            new_request = urllib.request.Request(url=self._create_request_url(),
                                                 data=None,
                                                 headers=self.create_get_headers(),
                                                 method='GET')
            self.open_follow(new_request, 1)

        def do_POST(self):
            try:
                request = json.loads(self._read_request())
                if 'type' not in request.keys():
                    request['type'] = 'GET'
                if 'url' not in request.keys() or \
                        (request['type'] == 'POST' and 'content' not in request.keys()):
                    return self._return_error('invalid json')
            except:
                return self._return_error('invalid json')
            new_request = urllib.request.Request(url=request['url'],
                                                 data=bytes(request.get('content'), 'UTF-8') if 'content' in request else None,
                                                 headers=request.get('headers', {}),
                                                 method=request['type'])
            self.open_follow(new_request, timeout=request.get('timeout', 1))

        def create_get_headers(self):
            new_headers = dict(self.headers)
            if 'Host' in new_headers:
                del new_headers['Host']
            return new_headers

        def open_follow(self, request, timeout):
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    res_content = response.read().decode(_get_charset(response.getheaders()))
                    return self._return(response.status, dict(response.getheaders()), res_content)
            except urllib.error.HTTPError as e:
                return self._return_error(e.getcode())
            except urllib.error.URLError as e:
                logger.info('Timeout1 maybe.', exc_info=True)
                if type(e.reason) == socket.timeout:
                    return self._return_error('timeout')
                else:
                    # No idea what happened here
                    return self._return_error('timeout')
            except:
                # No idea what happened here
                logger.info('Timeout2 maybe.', exc_info=True)
                return self._return_error('timeout')

        def _create_request_url(self):
            new_parts = urllib.parse.urlparse(self.path)
            return urllib.parse.urlunparse(parsed_url[:2] + new_parts[2:])

        def _read_request(self):
            if 'Content-Length' not in self.headers:
                return ''
            return self.rfile.read(int(self.headers['Content-Length'])).decode(_get_charset(self.headers))

        def _return_error(self, code):
            return self._return(code, None, None)

        def _return(self, code, headers, contents):
            logger.info('_return code: %s headers: \'%s\' contents: \'%s\'.',
                        str(code),
                        str(headers),
                        str(contents))
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
