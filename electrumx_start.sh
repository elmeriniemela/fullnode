#!/bin/bash
export $(grep -v '^#' bitcoin-blockchain-datadir/electrumx.env | xargs)
./electrumx-venv/bin/python ./electrumx/electrumx_server
