#!/bin/bash
export $(grep -v '^#' bitcoin-blockchain-datadir/electrumx.env | xargs)
./electrumx/electrumx_server
