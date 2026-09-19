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
ENABLE_TOR = True


def save(path, config):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, mode=0o700, exist_ok=True)

    if path.endswith(".json"):
        with open(path, "w") as fp:
            json.dump(config, fp, indent=4)
            fp.write("\n")
    elif path.endswith(".toml"):
        config_str = (
            "\n".join(
                f"{key} = {json.dumps(value)}"
                if isinstance(value, str)
                else f"{key} = {value}"
                for key, value in config
            )
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

    os.chmod(path, 0o600)


def build_configs(base_dir):
    bitcoin = [
        ("server", "1"),
        ("rest", "1"),
        ("maxmempool", 1024 * 2),  # 2 GB mempool
        ("upnp", 0),
        ("txindex", 1),
        ("networkactive", 1),
        ("listen", 1),
        ("bind", "0.0.0.0"),
        ("port", 8333),
        ("datacarrier", 1),
        ("datacarriersize", 100000),
        ("minrelaytxfee", "0.00000001"),
        ("incrementalrelayfee", "0.00000001"),
        ("dustrelayfee", "0.00000001"),
        ("maxconnections", 64),
        ("dbcache", 1024 * 8),  # 8 GB dbcache
        ("par", 4),
        ("checkblocks", 10),
        ("checklevel", 4),
        ("disablewallet", 1),
        ("rpcuser", "bitcoin"),
        ("rpcpassword", secrets.token_urlsafe(32)),
        ("rpcbind", "127.0.0.1"),
        ("rpcallowip", "127.0.0.1"),
        ("rpcport", 8332),
        ("zmqpubrawblock", "tcp://127.0.0.1:28332"),
        ("zmqpubrawtx", "tcp://127.0.0.1:28333"),
        ("whitelist", "127.0.0.1"),
        ("debug", "rpc"),
    ]

    if ENABLE_TOR:
        bitcoin += [
            ("proxy", "127.0.0.1:9050"),
            ("debug", "tor"),
        ]
    else:
        bitcoin += [
            ("listenonion", "0"),
            ("onlynet", "ipv4"),
            ("onlynet", "ipv6"),
        ]

    bitcoindict = dict(bitcoin)

    electrs = [
        ("auth", f'{bitcoindict["rpcuser"]}:{bitcoindict["rpcpassword"]}'),
        ("daemon_rpc_addr", f'127.0.0.1:{bitcoindict["rpcport"]}'),
        ("daemon_p2p_addr", f'127.0.0.1:{bitcoindict["port"]}'),
        ("db_dir", os.path.join(base_dir, "data", "electrs_db")),
        ("network", "bitcoin"),
        ("electrum_rpc_addr", "127.0.0.1:50011"),
        ("log_filters", "INFO"),
    ]

    return bitcoin, electrs


if __name__ == "__main__":
    base_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_DIR

    config_dir = os.path.join(base_dir, "config")
    os.makedirs(config_dir, mode=0o700, exist_ok=True)

    bitcoin, electrs = build_configs(base_dir)

    bitcoin_conf_path = os.path.join(config_dir, "bitcoin.conf")
    electrs_toml_path = os.path.join(config_dir, "electrs.toml")

    save(bitcoin_conf_path, bitcoin)
    save(electrs_toml_path, electrs)

    print(f"Generated configuration files with 0600 permissions in {config_dir}")
