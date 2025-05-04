
## Build bitcoind
* Tor is for securely accessing the node from outside networks. ZeroMQ is for lnd notifications.
* `sudo pacman -S --needed tor zeromq`
* `sudo pacman -S --needed autoconf automake boost gcc libevent libtool make pkgconf python sqlite`
* `sudo systemctl enable tor --now`
* `sudo usermod -a -G tor elmeri`
* Add to `/etc/tor/torrc`
```
# Allow bitcoind to automatically create a service accessible from tor network.
ControlPort 9051
CookieAuthentication 1
CookieAuthFile /var/lib/tor/control_auth_cookie
CookieAuthFileGroupReadable 1
DataDirectoryGroupReadable 1

# Manually create a ElectrumX service accessible from tor netowrk.
HiddenServiceDir /var/lib/tor/electrumx/
HiddenServicePort 50001 127.0.0.1:50001
HiddenServicePort 50002 127.0.0.1:50002
```
* `git submodule update --init`
* `cd bitcoin`
* `./autogen.sh`
* `./configure`
* `make`
* Source: https://github.com/bitcoin/bitcoin/blob/master/doc/build-unix.md

## Install electrumx dependencies:
* `python3.12 -m venv electrumx-venv`
* `cd electrumx/`
* `../electrumx-venv/bin/python -m pip install .`


## DATUM Gateway
* `cd datum_gateway`
* `sudo pacman -Syu base-devel cmake pkgconf curl jansson libsodium libmicrohttpd psmisc`
* `cmake . && make`


## Lightning Network Daemon (lnd)
* `mkdir go`
* `sudo pacman -S go`
* `cd lnd`
* `GOPATH=~/bitcoin-extdrive/fullnode/go make install tags="signrpc walletrpc chainrpc invoicesrpc"`
* Update `git pull && make clean && make` and run command above

## Lightning Loop
* `cd loop/cmd`
* `GOPATH=~/bitcoin-extdrive/fullnode/go go install ./...`

## Cofigure services
* `cd .. && mkdir config`
* `./fullnode/bin/config.py`
* `cat config/bitcoin.conf`
* `cat config/electrumx.env`
* `cat config/nbxplorer.config`
* `cat data/btcpayserver/Main/settings.config`

## Run bitcoind before starting electrumx:
* `./bitcoind.sh`

## Usage:
* `./electrumx_start.sh`
* `./electrumx_stop.sh`

## Service
* `sudo cp service/* /etc/systemd/system/`
* `sudo systemctl daemon-reload`
* `sudo systemctl enable bitcoind --now && journalctl -u bitcoind.service -f`
* `sudo systemctl enable electrumx --now && journalctl -u electrumx.service -f`

## Connect wallet:
* `electrum --oneserver --server 127.0.0.1:50001:t`

## Connect wallet via tor:
* Get tor hostname: `sudo ./electrumx-onion-host.py`
* Install tor
    * Linux: `sudo pacman -S tor`
    * Android download Orbot and add electrum to its services
* Electrum -> Network -> Proxy: localhost:9050
* `electrum --oneserver --server <tor-host-name>:50002:s`

## btcpayserver
* `yay -S btcpayserver nbxplorer`
* `sudo cp nbxplorer.service /etc/systemd/system/`
* `sudo cp btcpayserver.service /etc/systemd/system/`
* `sudo systemctl enable nbxplorer --now && journalctl -u nbxplorer.service -f`
* `sudo systemctl enable btcpayserver --now && journalctl -u btcpayserver.service -f`
