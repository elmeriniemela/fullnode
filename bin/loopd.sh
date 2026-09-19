#!/bin/bash
set -euo pipefail

exec /srv/bitcoin/fullnode/go/bin/loopd "$@"
