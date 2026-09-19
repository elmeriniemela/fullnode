#!/bin/bash
set -euo pipefail

if [ ! -f "/srv/bitcoin/config/lnd-pw.txt" ]; then
    exec /srv/bitcoin/fullnode/go/bin/lnd \
        --bitcoin.active \
        --bitcoin.mainnet \
        --bitcoind.dir=/srv/bitcoin/data \
        --bitcoind.config=/srv/bitcoin/config/bitcoin.conf \
        --bitcoin.node=bitcoind \
        "$@"
else
    exec /srv/bitcoin/fullnode/go/bin/lnd \
        --bitcoin.active \
        --bitcoin.mainnet \
        --bitcoind.dir=/srv/bitcoin/data \
        --bitcoind.config=/srv/bitcoin/config/bitcoin.conf \
        --bitcoin.node=bitcoind \
        --wallet-unlock-password-file=/srv/bitcoin/config/lnd-pw.txt \
        "$@"
fi
