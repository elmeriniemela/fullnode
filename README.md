
## Build bitcoind
* `git submodule update --init`
* `cd bitcoin`
* `./autogen.sh`
* `./configure`
* `make`
* Source: https://github.com/bitcoin/bitcoin/blob/master/doc/build-unix.md


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

## Service
* `sudo cp bitcoind.service /etc/systemd/system/`
* `sudo cp electrumx.service /etc/systemd/system/`
* `sudo systemctl enable bitcoind --now && journalctl -u bitcoind.service -f`
* `sudo systemctl enable electrumx --now && journalctl -u electrumx.service -f`

## Connect wallet:
* `electrum --oneserver --server 127.0.0.1:50001:t`
