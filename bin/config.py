#!/usr/bin/env python3
import os
import sys
import json
import secrets

DEFAULT_BASE_DIR = os.environ.get(
    "BITCOIN_DIR",
    "/srv/bitcoin"
    if os.path.exists("/srv/bitcoin")
    else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
)
ENABLE_TOR = False


def save(path, config):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, mode=0o755, exist_ok=True)

    if path.endswith(".json"):
        with open(path, "w") as fp:
            json.dump(config, fp, indent=4)
            fp.write("\n")
    elif path.endswith(".toml"):
        config_str = (
            "\n".join(f"{key} = {json.dumps(value)}" for key, value in config)
            + "\n"
        )
        with open(path, "w") as fp:
            fp.write(config_str)
    else:
        config_str = (
            "\n".join(f"{key}={value}" for key, value in config) + "\n"
        )
        with open(path, "w") as fp:
            fp.write(config_str)

    os.chmod(path, 0o644)


def build_configs(base_dir):
    rpc_user = os.environ.get("BITCOIN_RPC_USER", "elmeri")
    rpc_password = os.environ.get("BITCOIN_RPC_PASSWORD") or secrets.token_urlsafe(32)

    bitcoin = [
        ("rest", "1"),
        ("upnp", "0"),
        ("txindex", "1"),
        ("networkactive", "1"),
        ("dustrelayfee", "0.00000001"),
        ("par", "4"),
        ("checkblocks", "10"),
        ("checklevel", "4"),
        ("disablewallet", "0"),
        ("rpcuser", rpc_user),
        ("rpcpassword", rpc_password),
        ("rpcbind", "127.0.0.1"),
        ("rpcallowip", "127.0.0.1"),
        ("rpcport", "8332"),
        ("zmqpubrawblock", "tcp://127.0.0.1:28332"),
        ("zmqpubrawtx", "tcp://127.0.0.1:28333"),
        ("whitelist", "127.0.0.1"),
    ]

    if ENABLE_TOR:
        bitcoin.append(("proxy", "127.0.0.1:9050"))
    else:
        bitcoin += [
            ("listenonion", "0"),
            ("onlynet", "ipv4"),
            ("onlynet", "ipv6"),
        ]

    bitcoin += [
        ("listen", "1"),
        ("bind", "0.0.0.0:8333"),
        ("bind", "[::]:8333"),
        ("natpmp", "0"),
        ("maxconnections", "256"),
        ("asmap", "latest_asmap.dat"),
        ("v2transport", "1"),
        ("maxuploadtarget", "0"),
        ("blocksonly", "0"),
        ("whitelistforcerelay", "1"),
        ("whitelistrelay", "1"),
        ("privatebroadcast", "0"),
        ("txreconciliation", "0"),
        ("maxmempool", "1000"),
        ("mempoolexpiry", "336"),
        ("persistmempool", "1"),
        ("minrelaytxfee", "0.00000010"),
        ("incrementalrelayfee", "0.00000010"),
        ("datacarrier", "1"),
        ("datacarriersize", "100000"),
        ("maxsendbuffer", "5000"),
        ("maxreceivebuffer", "5000"),
        ("dbcache", "450"),
        ("server", "1"),
        ("rpcthreads", "16"),
        ("rpcworkqueue", "64"),
    ]

    bitcoindict = dict(bitcoin)

    electrs = [
        ("auth", f'{bitcoindict["rpcuser"]}:{bitcoindict["rpcpassword"]}'),
        ("daemon_rpc_addr", f'127.0.0.1:{bitcoindict["rpcport"]}'),
        ("db_dir", os.path.join(base_dir, "data", "electrs_db_bindex")),
        ("network", "bitcoin"),
        ("electrum_rpc_addr", "127.0.0.1:50011"),
        ("log_filters", "INFO"),
        ("monitoring_addr", "127.0.0.1:4224"),
        ("db_parallelism", 4),
        ("wait_duration_secs", 5),
        ("jsonrpc_timeout_secs", 60),
        ("index_lookup_limit", 1000),
        ("auto_reindex", True),
    ]

    return bitcoin, electrs


if __name__ == "__main__":
    base_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_DIR

    config_dir = os.path.join(base_dir, "config")
    os.makedirs(config_dir, mode=0o755, exist_ok=True)
    os.chmod(config_dir, 0o755)

    bitcoin, electrs = build_configs(base_dir)

    bitcoin_conf_path = os.path.join(config_dir, "bitcoin.conf")
    electrs_toml_path = os.path.join(config_dir, "electrs.toml")

    save(bitcoin_conf_path, bitcoin)
    save(electrs_toml_path, electrs)

    print(f"Generated configuration files with 0644 permissions in {config_dir}")
