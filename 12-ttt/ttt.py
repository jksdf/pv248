#!/usr/bin/env python3
import http.server
import json
import logging
import socketserver
import sys
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_handler(game):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            path = urllib.parse.urlparse(self.path)
            query = dict([i.split('=') for i in urllib.parse.unquote_plus(path.query).split('&') if i])
            logger.info('requested path %s with query %s', str(path), str(query))
            if path.path == '/start':
                gid = game.create_game(query.get('name', ''))
                return self.return_json({'id': gid})
            elif path.path == '/status':
                try:
                    gid = int(query.get('game'))
                    status = game.status(gid)
                except TypeError:
                    return self.return_error(404)
                return self.return_json(status)
            elif path.path == '/play':
                try:
                    gid = int(query['game'])
                except:
                    return self.return_error(404)
                try:
                    player, x, y = [int(query[i]) for i in ('player', 'x', 'y')]
                except TypeError:
                    return self.return_json({'status': 'bad', 'message': 'Error parsing int parameter'})
                try:
                    err = game.play(gid, player, x, y)
                except:
                    return self.return_error(404)
                return self.return_json({'status': 'ok' if err is None else 'bad', 'message': err})
            elif path.path == '/list':
                self.return_json([{'name': g['name'], 'id': gid} for gid, g in game.games.items() if g.get('board') == [[0]*3]*3])
            else:
                return self.return_error(418)

        def return_error(self, code):
            self.send_response(code)
            self.end_headers()
            self.wfile.write(b'{}')

        def return_json(self, js):
            if type(js) == dict:
                js = {key: val for key, val in js.items() if val is not None}
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(js, indent=2), 'UTF-8'))

    return Handler


class Game:

    def __init__(self):
        self.games = {}
        self.id_counter = -1

    def create_game(self, name):
        name = name if name else ''
        self.id_counter += 1
        self.games[self.id_counter] = {'name': name, 'next': 1, 'board': [[0 for _ in range(3)] for _ in range(3)]}
        return self.id_counter

    def play(self, gid, player, x, y):
        g = self.games.get(gid)
        if not g:
            raise TypeError
        if g['next'] != player:
            return 'Incorrect player'
        if x not in range(3):
            return 'X coordinate out of range'
        if y not in range(3):
            return 'Y coordinate out of range'
        if g['board'][x][y] != 0:
            return 'The space on the board is already in use'
        g['board'][x][y] = player
        g['next'] = 1 if player == 2 else 2

        res = self.finished(g)
        if res is not None:
            self.games[gid] = {'winner': res, 'name': g['name']}
        return None

    def status(self, gid):
        if gid is None or gid not in self.games:
            raise TypeError
        return self.games[gid]

    def finished(self, g):
        for i in range(3):
            all = [g['board'][i][j] for j in range(3)]
            if all == [1]*3:
                return 1
            if all == [2]*3:
                return 2
        for i in range(3):
            all = [g['board'][j][i] for j in range(3)]
            if all == [1] * 3:
                return 1
            if all == [2] * 3:
                return 2
        all = [g['board'][0][0], g['board'][1][1], g['board'][2][2]]
        if all == [1] * 3:
            return 1
        if all == [2] * 3:
            return 2
        all = [g['board'][0][2], g['board'][1][1], g['board'][2][0]]
        if all == [1] * 3:
            return 1
        if all == [2] * 3:
            return 2
        if len([k for k in [g['board'][i][j] for i in range(3) for j in range(3)] if k == 0]) == 0:
            return 0
        return None


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass


def serve(port):
    game = Game()
    httpd = ThreadedHTTPServer(("", port), create_handler(game))
    httpd.serve_forever()


def main(args):
    serve(int(args[0]))


if __name__ == '__main__':
    main(sys.argv[1:])

