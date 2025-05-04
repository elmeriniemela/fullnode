#!/bin/bash
export $(grep -v '^#' config/electrumx.env | xargs)
./fullnode/electrumx-venv/bin/python ./fullnode/electrumx/electrumx_server
