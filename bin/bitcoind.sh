#!/bin/bash
./fullnode/bitcoin/build/bin/bitcoind -datadir=data -conf=../config/bitcoin.conf $@ -pid=/run/bitcoind/bitcoind.pid -startupnotify='systemd-notify --ready' -shutdownnotify='systemd-notify --stopping'
