#!/usr/bin/env bash

PORT=8000
GAME=1

TURN=1
swap() {
    if [ ${TURN} = '1' ]; then
        TURN=2
    else
        TURN=1
    fi
}

play() {
    curl "localhost:$PORT/play?game=$GAME&player=${TURN}&x=$1&y=$2"
    echo
    curl "localhost:$PORT/status?id=$GAME"
    swap
}

start() {
    curl "localhost:$PORT/start"
}

start
play 0 0
play 1 1
play 2 2
play 0 2
play 2 0
play 1 0
play 0 1
play 2 1
play 1 2