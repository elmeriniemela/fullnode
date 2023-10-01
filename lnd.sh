#!/bin/bash
if [ ! -f "bitcoin-blockchain-datadir/lnd-pw.txt" ]; then
    ./go/bin/lnd --bitcoin.active --bitcoin.mainnet --bitcoind.dir=bitcoin-blockchain-datadir --bitcoin.node=bitcoind $@
else
    ./go/bin/lnd --bitcoin.active --bitcoin.mainnet --bitcoind.dir=bitcoin-blockchain-datadir --bitcoin.node=bitcoind --wallet-unlock-password-file=bitcoin-blockchain-datadir/lnd-pw.txt $@
fi

