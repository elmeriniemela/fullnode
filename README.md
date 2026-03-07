
# Personal 'fullnode'
DISCLAIMER: This repository is for my personal deployment of Bitcoin-related software on my own infrastructure.

It is not intended to be a generic installer, production-ready distribution, or security-hardened template for other environments.

Expect host-specific assumptions (paths, usernames, system services, network settings) that may not apply outside my setup.

## Build bitcoind
* Tor is for securely accessing the node from outside networks. ZeroMQ is for lnd notifications.
* `sudo pacman -S --needed tor zeromq autoconf automake boost gcc libevent libtool make pkgconf python sqlite cmake capnproto`
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
* `cmake -B build -DWITH_ZMQ=ON -DENABLE_WALLET=OFF`
* `cmake --build build -j 8`
* Source: https://github.com/bitcoin/bitcoin/blob/master/doc/build-unix.md

## Install electrumx dependencies:
* `python3.12 -m venv electrumx-venv`
* `cd electrumx/`
* `../electrumx-venv/bin/python -m pip install .`

## electrs
* Check hints from PKGBUILD via AUR: https://aur.archlinux.org/packages/electrs
* `sudo pacman -S --needed clang gcc-libs cmake rust`
* `export CXXFLAGS="$CXXFLAGS -include cstdint"`
* `cargo build --bins --tests --release --locked`


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



## Core Lightning (CLN)
* `sudo pacman --needed -S uv jq autoconf automake libtool net-tools gettext lowdown valgrind shellcheck cppcheck lowdown cargo rustfmt protobuf`
* `uv sync --all-extras --all-groups --frozen`
* `./configure CWARNFLAGS="-Wall -Wundef -Wmissing-prototypes -Wmissing-declarations -Wstrict-prototypes -Wold-style-definition -Werror -Wno-maybe-uninitialized -Wshadow=local -Wno-error=discarded-qualifiers"`
* `uv run make`
* `uv run make check VALGRIND=0`


## Elements Project blockchain platform (Liquid network)
* `mkdir`




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
* `sudo systemctl enable electrs --now && journalctl -u electrs.service -f`

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

