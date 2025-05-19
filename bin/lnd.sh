#!/bin/bash
if [ ! -f "config/lnd-pw.txt" ]; then
    ./fullnode/go/bin/lnd --bitcoin.active --bitcoin.mainnet --bitcoind.dir=data --bitcoind.config=config/bitcoin.conf --bitcoin.node=bitcoind $@
else
    ./fullnode/go/bin/lnd --bitcoin.active --bitcoin.mainnet --bitcoind.dir=data --bitcoind.config=config/bitcoin.conf --bitcoin.node=bitcoind --wallet-unlock-password-file=config/lnd-pw.txt $@
fi

