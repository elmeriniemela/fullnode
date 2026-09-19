#!/bin/bash
set -euo pipefail

exec /srv/bitcoin/fullnode/bitcoin/build/bin/bitcoind \
    -datadir=/srv/bitcoin/data \
    -conf=/srv/bitcoin/config/bitcoin.conf \
    -pid=/run/bitcoind/bitcoind.pid \
    -startupnotify='systemd-notify --ready' \
    -shutdownnotify='systemd-notify --stopping' \
    "$@"
