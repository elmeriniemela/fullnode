#!/usr/bin/env python3

import secrets

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
}

electrumx = {
    'PEER_DISCOVERY': 'self', # peer discovery is disabled and the server will only return itself in the peers list.
    'SERVICES': 'tcp://0.0.0.0:50001,rpc://127.0.0.1:50000',
    'DAEMON_URL': f'http://{bitcoin["rpcuser"]}:{bitcoin["rpcpassword"]}@{bitcoin["rpcbind"]}:{bitcoin["rpcport"]}',
    'USERNAME': 'elmeri',
    'NET': 'mainnet',
    'COIN': 'Bitcoin',
    'ELECTRUMX': 'electrumx/electrumx_server',
    'DB_DIRECTORY': 'bitcoin-blockchain-datadir/electrum_db',
}

def save(path, config):
    config_str = '\n'.join(f'{key}={value}' for key, value in config.items())
    with open(path, 'w') as fp:
        fp.write(config_str)

save('bitcoin-blockchain-datadir/electrumx.env', electrumx)
save('bitcoin-blockchain-datadir/bitcoin.conf', bitcoin)
