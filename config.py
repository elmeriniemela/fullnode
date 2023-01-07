#!/usr/bin/env python3
import subprocess
import secrets
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

bitcoin = {
    'upnp': 1,
    'txindex': 1,
    'networkactive': 1, # Enable all P2P network activity (default: 1). Can be changed by the setnetworkactive RPC command
    'proxy': '127.0.0.1:9050', # Tor Proxy
    'debug': 'tor', # enable Tor debug logging.
    'listen': 1,
    'bind': '0.0.0.0',
    'port': 8333,
    'maxconnections': 64,
    'dbcache': 64,
    'par': 2,
    'checkblocks': 24,
    'checklevel': 0,
    'disablewallet': 1,
    'rpcuser': secrets.token_urlsafe(32),
    'rpcpassword': secrets.token_urlsafe(32),
    'rpcbind': '127.0.0.1',
    'rpcallowip': '127.0.0.1',
    'rpcport': 8332,
    'zmqpubrawblock': 'tcp://127.0.0.1:28332',
    'zmqpubrawtx': 'tcp://127.0.0.1:28333',
}

# onion_host = subprocess.run("./electrumx-onion-host.py", shell=True, check=True, capture_output=True, encoding='utf-8').stdout.strip()

electrumx = {
    'PEER_DISCOVERY': 'self', # peer discovery is disabled and the server will only return itself in the peers list.
    'SERVICES': 'tcp://0.0.0.0:50001,ssl://0.0.0.0:50002,rpc://127.0.0.1:50000',
     #'REPORT_SERVICES': 'tcp://{onion_host}:50001,ssl://{onion_host}:50002',
    'DAEMON_URL': f'http://{bitcoin["rpcuser"]}:{bitcoin["rpcpassword"]}@{bitcoin["rpcbind"]}:{bitcoin["rpcport"]}',
    'USERNAME': 'elmeri',
    'NET': 'mainnet',
    'COIN': 'Bitcoin',
    'ELECTRUMX': 'electrumx/electrumx_server',
    'DB_DIRECTORY': 'bitcoin-blockchain-datadir/electrum_db',
    'FORCE_PROXY': True,
    'TOR_PROXY_HOST': 'localhost',
    'TOR_PROXY_PORT': 9050,
    'SSL_CERTFILE': os.path.join(CURRENT_DIR, 'bitcoin-blockchain-datadir/electrumx-ssl.crt'),
    'SSL_KEYFILE': os.path.join(CURRENT_DIR, 'bitcoin-blockchain-datadir/electrumx-ssl.key'),
}

if not os.path.exists(electrumx['SSL_CERTFILE']):
    subprocess.run(f'openssl req -new -newkey rsa:2048 -days 18250 -nodes -x509 -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com" -keyout {electrumx["SSL_KEYFILE"]} -out {electrumx["SSL_CERTFILE"]}', shell=True, check=True)

def save(path, config):
    config_str = '\n'.join(f'{key}={value}' for key, value in config.items())
    with open(path, 'w') as fp:
        fp.write(config_str)

save('bitcoin-blockchain-datadir/electrumx.env', electrumx)
save('bitcoin-blockchain-datadir/bitcoin.conf', bitcoin)
