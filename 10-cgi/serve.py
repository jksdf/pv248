#!/usr/bin/env python3
import http.server
import os
import pprint
import socketserver
import sys
import urllib.error
import urllib.parse
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_handler(base_dir, read_len=1000):
    full_base_dir = os.path.abspath(base_dir)

    class Handler(http.server.CGIHTTPRequestHandler):
        def do_HEAD(self):
            logger.info(pprint.pformat(self.__dict__))
            self.send_error(418)

        def do_POST(self):
            logger.info(pprint.pformat(self.__dict__))
            self.handle_call()

        def do_GET(self):
            logger.info(pprint.pformat(self.__dict__))
            self.handle_call()

        def handle_call(self):
            request_url = urllib.parse.urlparse(self.path)
            full_path = os.path.abspath(os.path.join(full_base_dir, request_url.path[1:]))
            logging.info("Opening path: \"{}\" (rel: \"{}\")".format(full_path, os.path.relpath(full_path, os.getcwd())))
            os.path.relpath(full_path, os.getcwd())
            if os.path.isfile(full_path):
                if full_path.endswith('.cgi'):
                    self.cgi_info = '', '{}?{}'.format(os.path.relpath(full_path, os.getcwd()), request_url.query)
                    self.run_cgi()
                else:
                    self.print_file(full_path)
            else:
                self.send_error(404, explain='The file does not exist')

        def print_file(self, full_path):
            file_size = os.path.getsize(full_path)
            self.send_response(200)
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            fp = open(full_path, 'rb')
            cont = True
            read = 0
            while cont:
                data = fp.read(read_len)
                if data is None or data == b'' or file_size == read:
                    cont = False
                else:
                    read += len(data)
                    self.wfile.write(data)

    return Handler


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass


def serve(port, path):
    httpd = ThreadedHTTPServer(("", port), create_handler(path))
    httpd.serve_forever()


def main(args):
    serve(int(args[0]), args[1])


if __name__ == '__main__':
    main(sys.argv[1:])
