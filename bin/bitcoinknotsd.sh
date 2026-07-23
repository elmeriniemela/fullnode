#!/bin/bash
./fullnode/bitcoinknots/build/bin/bitcoind -datadir=knotsdata -conf=../config/knots.conf $@ -pid=/run/bitcoinknotsd/bitcoinknotsd.pid -startupnotify='systemd-notify --ready' -shutdownnotify='systemd-notify --stopping'
