

## Verify:
* `sha256sum --ignore-missing --check SHA256SUMS`
* `gpg --keyserver hkps://keys.openpgp.org --recv-keys E777299FC265DD04793070EB944D35F9AC3DB76A`
* `gpg --verify SHA256SUMS.asc`



## Run bitcoind before starting electrumx:
* `./bitcoind.sh`


## Install electrumx dependencies:
* `cd electrumx/`
* `pip3 install .`


## Config:
* `bitcoin-blockchain-datadir/bitcoin.conf`
* `bitcoin-blockchain-datadir/electrumx.env`


## Usage:
* `./electrumx_start.sh`
* `./electrumx_stop.sh`

## Connect wallet:
* `electrum --oneserver --server 127.0.0.1:50001:t`
