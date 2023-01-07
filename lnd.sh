#!/bin/bash
./go/bin/lnd --bitcoin.active --bitcoin.mainnet --bitcoind.dir=bitcoin-blockchain-datadir --bitcoin.node=bitcoind $@
