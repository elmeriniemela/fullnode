## Cofigure bitcoind and electrumx
* `./config.py`
* `cat bitcoin-blockchain-datadir/bitcoin.conf`
* `cat bitcoin-blockchain-datadir/electrumx.env`

## Run bitcoind before starting electrumx:
* `./bitcoind.sh`

## Install electrumx dependencies:
* `cd electrumx/`
* `pip3 install .`

## Usage:
* `./electrumx_start.sh`
* `./electrumx_stop.sh`

## Connect wallet:
* `electrum --oneserver --server 127.0.0.1:50001:t`
