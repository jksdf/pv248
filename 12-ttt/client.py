#!/usr/bin/env python3
import json
import socket
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from enum import Enum
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


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


class Controller:
    def __init__(self, url):
        self.url = url
        self.gid = None
        self.player = None

    def request(self, path, params):
        req_url = '{}/{}?{}'.format(self.url, path, '&'.join(['{}={}'.format(k, v) for k, v in params.items()]))
        try:
            with urllib.request.urlopen(req_url) as response_raw:
                return json.loads(response_raw.read().decode(_get_charset(response_raw.getheaders())))
        except urllib.error.HTTPError:
            logger.info('HTTPError.', exc_info=True)
            raise urllib.error.HTTPError
        except urllib.error.URLError:
            logger.info('URLError.', exc_info=True)
            raise urllib.error.HTTPError
        # except:
        #     logger.info('Unknown issue.', exc_info=True)
        #     raise urllib.error.HTTPError

    def list_games(self):
        """Lists all active games with no moves played."""
        try:
            return self.request('list', {})
        except urllib.error.HTTPError as e:
            print('There is an issue with the connection to the server.')
            raise e

    def start_game(self):
        """Start a game, return gid."""
        try:
            self.gid = self.request('start', {})['id']
            self.player = 1
            return self.gid
        except urllib.error.HTTPError as e:
            print('There is an issue with the connection to the server.')
            raise e

    def join_game(self, gid):
        """Join a game by gid."""
        self.gid = gid
        self.player = 2

    def play(self, x, y):
        """Play a move and return an error message or None."""
        try:
            res = self.request('play', {'game': self.gid, 'player': self.player, 'x': x, 'y': y})
            return res['message'] if res['status'] == 'bad' else None
        except urllib.error.HTTPError as e:
            print('There is an issue with the connection to the server.')
            raise e

    def my_turn(self):
        """Returns true if the next player is me or the game is finished."""
        try:
            res = self.request('status', {'id': self.gid})
            return res.get('next') == self.player or 'winner' in res.keys()
        except urllib.error.HTTPError as e:
            print('There is an issue with the connection to the server.')
            raise e

    def get_board(self):
        try:
            res = self.request('status', {'id': self.gid})
            return res['board']
        except urllib.error.HTTPError as e:
            print('There is an issue with the connection to the server.')
            raise e

    def is_done(self):
        try:
            res = self.request('status', {'id': self.gid})
            return 'winner' in res.keys()
        except urllib.error.HTTPError as e:
            print('There is an issue with the connection to the server.')
            raise e

    def get_winner(self):
        try:
            res = self.request('status', {'id': self.gid})
            return res.get('winner')
        except urllib.error.HTTPError as e:
            print('There is an issue with the connection to the server.')
            raise e


class Client:

    class States(Enum):
        INIT = 1,
        MY_TURN = 2,
        ENEMY_TURN = 3
        END = 4,
        EXIT = 5

    def __init__(self, url):
        self.url = url
        self.state = Client.States.INIT
        self.ctrl = Controller(url)

    def get_action(self):
        return {self.States.INIT: self.s_init,
                self.States.MY_TURN: self.s_my_turn,
                self.States.ENEMY_TURN: self.s_enemy_turn,
                self.States.END: self.s_end}[self.state]

    def s_my_turn(self):
        print('your turn ({}):'.format(self.play_num_to_char[self.ctrl.player]))
        try:
            x, y = [int(i.strip()) for i in input().split()]
            err_msg = self.ctrl.play(x, y)
            if err_msg is not None:
                print('Error from the server:', err_msg)
                return self.States.MY_TURN
            return self.States.ENEMY_TURN if self.ctrl.get_winner() is None else self.States.END
        except (TypeError, ValueError):
            print('invalid input')
            return self.States.MY_TURN

    def s_enemy_turn(self):
        print('waiting for the other player')
        while not self.ctrl.my_turn():
            time.sleep(1)

        self.print_board()
        return self.States.MY_TURN if self.ctrl.get_winner() is None else self.States.END

    def s_end(self):
        winner = self.ctrl.get_winner()
        if winner == 0:
            print('draw')
        elif winner == self.ctrl.player:
            print('you won')
        else:
            print('you lost')
        return self.States.EXIT

    def s_init(self):
        # Prompt with game selection
        print('Available games:')
        # TODO: only empty games
        for game in self.ctrl.list_games():
            print('{}: {}'.format(game['id'], game['name']))
        print('Pick one by id or enter \'new\' to start a new game:')
        cmd = input().strip()
        if cmd == 'new':
            self.ctrl.start_game()
            print('Starting a new game.')
            return Client.States.MY_TURN
        else:
            try:
                gid = int(cmd)
                self.ctrl.join_game(gid)
                return Client.States.ENEMY_TURN
            except:
                print('Invalid game.')
                return Client.States.INIT

    def loop(self):
        # Main loop waiting for the game
        while self.state != Client.States.EXIT:
            logger.info('in state %s', str(self.state))
            self.state = self.get_action()()

    play_num_to_char = {0: '_', 1: 'x', 2: 'o'}

    def print_board(self):
        board = self.ctrl.get_board()
        for line in board:
            print(''.join([self.play_num_to_char[i] for i in line]))


def start_client(host, port):
    url = 'http://{}:{}'.format(host, port)
    c = Client(url)
    c.loop()

def main(args):
    start_client(args[0], int(args[1]))

if __name__ == '__main__':
    main(sys.argv[1:])