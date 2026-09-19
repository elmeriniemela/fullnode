#!/bin/bash
set -euo pipefail

exec /srv/bitcoin/fullnode/go/bin/lncli --bitcoind.config=/srv/bitcoin/config/bitcoin.conf "$@"
