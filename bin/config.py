#!/usr/bin/env python3
import subprocess
import secrets
import os
import json

CURRENT_DIR = os.getcwd()

ENABLE_TOR = True

bitcoin = [
    ('maxmempool', 2000), # store 2gb of low fee transactions instead of 0.3
    ('upnp', 1),
    ('txindex', 1),
    ('networkactive', 1), # Enable all P2P network activity (default: 1). Can be changed by the setnetworkactive RPC command
    ('listen', 1),
    ('bind', '0.0.0.0'),
    ('port', 8333),
    ('maxconnections', 64),
    ('dbcache', 64),
    ('par', 2),
    ('checkblocks', 24),
    ('checklevel', 0),
    ('disablewallet', 1),
    ('rpcuser', 'elmeri'),
    ('rpcpassword', secrets.token_urlsafe(32)),
    ('rpcbind', '0.0.0.0'),
    ('rpcallowip', '192.168.0.0/16'),
    ('rpcallowip', '37.27.20.117/32'),
    ('rpcport', 8332),
    ('zmqpubrawblock', 'tcp://127.0.0.1:28332'),
    ('zmqpubrawtx', 'tcp://127.0.0.1:28333'),
    ('whitelist', '127.0.0.1'),
]
if ENABLE_TOR:
    bitcoin += [
        ('proxy', '127.0.0.1:9050'), # Tor Proxy
        ('debug', 'tor'), # enable Tor debug logging.
    ]
# onion_host = subprocess.run("./electrumx-onion-host.py", shell=True, check=True, capture_output=True, encoding='utf-8').stdout.strip()
bitcoindict = dict(bitcoin)

electrumx = [
    ('PEER_DISCOVERY', 'self'), # peer discovery is disabled and the server will only return itself in the peers list.
    ('SERVICES', 'tcp://0.0.0.0:50001,ssl://0.0.0.0:50002,rpc://127.0.0.1:50000'),
     #('REPORT_SERVICES', 'tcp://{onion_host}:50001,ssl://{onion_host}:50002'),
    ('DAEMON_URL', f'http://{bitcoindict["rpcuser"]}:{bitcoindict["rpcpassword"]}@{bitcoindict["rpcbind"]}:{bitcoindict["rpcport"]}'),
    ('USERNAME', 'elmeri'),
    ('NET', 'mainnet'),
    ('COIN', 'Bitcoin'),
    ('ELECTRUMX', 'electrumx/electrumx_server'),
    ('DB_DIRECTORY', 'data/electrum_db'),
    ('FORCE_PROXY', True),
    ('SSL_CERTFILE', os.path.join(CURRENT_DIR, 'config/electrumx-ssl.crt')),
    ('SSL_KEYFILE', os.path.join(CURRENT_DIR, 'config/electrumx-ssl.key')),
]
if ENABLE_TOR:
    electrumx += [
        ('TOR_PROXY_HOST', 'localhost'),
        ('TOR_PROXY_PORT', 9050),
    ]

electrumxdict = dict(electrumx)

nbxplorer = [
    ('postgres', '"User ID=elmeri;Host=localhost;Database=nbxplorer"'),
    ('btcrpcauth', f'{bitcoindict["rpcuser"]}:{bitcoindict["rpcpassword"]}'),
    ('btcrpcurl', f'http://127.0.0.1:{bitcoindict["rpcport"]}'),
    ('btcnodeendpoint', f'127.0.0.1:{bitcoindict["port"]}'),
]

nbxplorerdict = dict(nbxplorer)

certthumbprint = subprocess.run('openssl x509 -noout -fingerprint -sha256 -in ~/.lnd/tls.cert | sed -e "s/.*=//;s/://g"', shell=True, check=True, stdout=subprocess.PIPE).stdout.decode().strip()
btcpayserver = [
    ('networ', 'mainnet'),
    ('port', 23000),
    ('bind', "127.0.0.1"),
    ('explorerpostgres', nbxplorerdict['postgres']),
    ('postgres', '"User ID=elmeri;Host=localhost;Database=btcpayserver"'),
    ('btclightning', f'"type=lnd-rest;server=https://127.0.0.1:8080/;macaroonfilepath=/home/elmeri/.lnd/data/chain/bitcoin/mainnet/admin.macaroon;certthumbprint={certthumbprint}"'),
]

if not os.path.exists(electrumxdict['SSL_CERTFILE']):
    subprocess.run(f'openssl req -new -newkey rsa:2048 -days 18250 -nodes -x509 -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com" -keyout {electrumxdict["SSL_KEYFILE"]} -out {electrumxdict["SSL_CERTFILE"]}', shell=True, check=True)

datum_gateway = {
	"bitcoind": {
		"rpcuser": bitcoindict["rpcuser"],
		"rpcpassword": bitcoindict["rpcpassword"],
		"rpcurl": f'http://127.0.0.1:{bitcoindict["rpcport"]}',
		"notify_fallback": True
	},
	"stratum": {
		"listen_port": 23334
	},
	"mining": {
		"pool_address": "put your own Bitcoin invoice address here",
		"coinbase_tag_primary": "DATUM Gateway",
		"coinbase_tag_secondary": "DATUM User"
	},
	"api": {
		"admin_password": secrets.token_urlsafe(32),
		"listen_port": 7152,
		"modify_conf": False
	},
	"logger": {
		"log_to_console": True,
		"log_to_file": False,
		"log_file": "/var/log/datum.log",
		"log_rotate_daily": True,
		"log_level_console": 2,
		"log_level_file": 1
	},
	"datum": {
		"pool_pass_workers": True,
		"pool_pass_full_users": True,
		"pooled_mining_only": False, # if connection to OCEAN dies, switch to lotto mining
	}
}


def save(path, config):
    config_str = '\n'.join(f'{key}={value}' for key, value in config) + '\n'
    with open(path, 'w') as fp:
        fp.write(config_str)



save('data/btcpayserver/Main/settings.config', btcpayserver)
save('data/bitcoin.conf', bitcoin)
save('config/electrumx.env', electrumx)
save('config/nbxplorer.config', nbxplorer)
with open('config/datum_gateway.json', 'w') as fp:
    json.dump(datum_gateway, fp, indent=4)