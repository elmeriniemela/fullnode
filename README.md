
## Build bitcoind
* sudo pacman -S tor
* sudo systemctl enable tor --now
* sudo usermod -a -G tor elmeri
* Add to /etc/tor/torrc
```
# Allow bitcoind to automatically create a service accessible from tor network.
ControlPort 9051
CookieAuthentication 1
CookieAuthFile /var/lib/tor/control_auth_cookie
CookieAuthFileGroupReadable 1
DataDirectoryGroupReadable 1

# Manually create a ElectrumX service accessible from tor netowrk.
HiddenServiceDir /var/lib/tor/electrumX_service/
HiddenServicePort 50001 127.0.0.1:50001
HiddenServicePort 50002 127.0.0.1:50002
```
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
* `python3.8 -m venv electrumx-venv`
* `cd electrumx/`
* `../electrumx-venv/bin/python -m pip install .`

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
