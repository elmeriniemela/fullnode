#!/bin/bash
if [ ! -f "config/lnd-pw.txt" ]; then
    ./go/bin/lnd --bitcoin.active --bitcoin.mainnet --bitcoind.dir=data --bitcoin.node=bitcoind $@
else
    ./go/bin/lnd --bitcoin.active --bitcoin.mainnet --bitcoind.dir=data --bitcoin.node=bitcoind --wallet-unlock-password-file=config/lnd-pw.txt $@
fi

