#!/usr/bin/env bash
# Benchmark Bitcoin Core RPCs used by electrs mempool sync.

set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  bench-electrs-rpc.sh BUILD_DIR [COUNT] [-- BITCOIN_CLI_ARGS...]

Examples:
  ../bin/bench-electrs-rpc.sh build-v31
  ../bin/bench-electrs-rpc.sh master-build 5000
  ../bin/bench-electrs-rpc.sh build-v31 1000 -- -datadir=/mnt/bitcoin

COUNT defaults to 1000 mempool transactions.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -lt 1 ]]; then
    usage
    exit 0
fi

build_dir=$1
count=${2:-1000}
shift
if [[ $# -gt 0 && "$1" != "--" ]]; then
    shift
fi
if [[ "${1:-}" == "--" ]]; then
    shift
fi

if ! [[ "$count" =~ ^[0-9]+$ ]] || [[ "$count" -eq 0 ]]; then
    echo "error: COUNT must be a positive integer" >&2
    exit 1
fi

bitcoin_cli="${build_dir%/}/bin/bitcoin-cli"
if [[ ! -x "$bitcoin_cli" ]]; then
    echo "error: bitcoin-cli not found or not executable: $bitcoin_cli" >&2
    exit 1
fi

if ! command -v jq >/dev/null; then
    echo "error: jq is required" >&2
    exit 1
fi

time_cmd=(time)
if [[ -x /usr/bin/time ]]; then
    time_cmd=(/usr/bin/time -f "%e real    %U user    %S sys")
fi

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

txids_file="$tmpdir/txids.txt"

run_cli() {
    "$bitcoin_cli" "$@" "${cli_args[@]}"
}

bench_loop() {
    local label=$1
    local rpc=$2

    echo
    echo "== $label =="
    "${time_cmd[@]}" bash -c '
        set -euo pipefail
        bitcoin_cli=$1
        rpc=$2
        txids_file=$3
        shift 3
        while IFS= read -r txid; do
            "$bitcoin_cli" "$rpc" "$txid" "$@" >/dev/null
        done < "$txids_file"
    ' _ "$bitcoin_cli" "$rpc" "$txids_file" "${cli_args[@]}"
}

cli_args=("$@")

echo "bitcoin-cli: $bitcoin_cli"
echo
"$bitcoin_cli" --version
echo

echo "== getmempoolinfo =="
run_cli getmempoolinfo

echo
echo "== getrawmempool txid fetch =="
"${time_cmd[@]}" bash -c '
    set -euo pipefail
    bitcoin_cli=$1
    count=$2
    txids_file=$3
    shift 3
    "$bitcoin_cli" getrawmempool "$@" | jq -r --argjson count "$count" ".[0:\$count][]" > "$txids_file"
' _ "$bitcoin_cli" "$count" "$txids_file" "${cli_args[@]}"

txid_count=$(wc -l < "$txids_file")
echo "selected txids: $txid_count"
if [[ "$txid_count" -eq 0 ]]; then
    echo "no mempool txids available; skipping per-tx benchmarks"
    exit 0
fi

bench_loop "getmempoolentry $txid_count txs" getmempoolentry
bench_loop "getrawtransaction $txid_count txs" getrawtransaction
