# Bitcoin Full Node Stack

Hardened deployment runbook for Bitcoin Core (`bitcoind`) and Electrs on Arch Linux, running on a dedicated encrypted volume mounted at `/srv/bitcoin` under the `bitcoin` system user.

## Directory Layout

All node components run inside the `/srv/bitcoin` mountpoint:
```text
/srv/bitcoin/
├── config/             # Configuration files (mode 0700, files 0600)
│   ├── bitcoin.conf
│   └── electrs.toml
├── data/               # Persistent data and indices (mode 0700)
│   ├── blocks/         # Bitcoin block storage
│   ├── chainstate/     # Bitcoin UTXO set
│   └── electrs_db/     # RocksDB Electrs index
└── fullnode/           # Repository checkout (mode 0750)
    ├── bin/            # Helper scripts and config generator
    ├── bitcoin/        # Bitcoin Core source and build
    ├── electrs/        # Electrs source and build
    └── service/        # Systemd service and target units
```

## 1. Build Instructions

### Dependencies
Install build tools and libraries:
```bash
sudo pacman -S --needed base-devel cmake boost libevent sqlite python capnproto rust clang tor
```

### Build Bitcoin Core
Build `bitcoind` and `bitcoin-cli` using CMake:
```bash
cd /srv/bitcoin/fullnode/bitcoin
cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_WALLET=OFF \
  -DENABLE_IPC=OFF \
  -DWITH_ZMQ=OFF \
  -DENABLE_EXTERNAL_SIGNER=OFF \
  -DBUILD_BITCOIN_BIN=OFF \
  -DBUILD_DAEMON=ON \
  -DBUILD_CLI=ON \
  -DBUILD_TESTS=OFF \
  -DBUILD_TX=OFF \
  -DBUILD_UTIL=OFF \
  -DBUILD_GUI=OFF \
  -DBUILD_BENCH=OFF \
  -DBUILD_FUZZ_BINARY=OFF \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DINSTALL_MAN=OFF

cmake --build build -j$(nproc)
```

### Build Electrs
Build the release binary with Cargo:
```bash
cd /srv/bitcoin/fullnode/electrs
cargo build --release --locked
```

## 2. Tor Setup

Enable and start the system Tor daemon:
```bash
sudo systemctl enable tor --now
```
Bitcoin Core connects to the local SOCKS5 proxy on `127.0.0.1:9050` to route peer and hidden service traffic securely.

## 3. Configuration Generation

Generate secure configuration files with owner-only (`0600`) permissions:
```bash
sudo -u bitcoin python3 /srv/bitcoin/fullnode/bin/config.py
```
This generates:
- `/srv/bitcoin/config/bitcoin.conf`: RPC bound strictly to `127.0.0.1:8332`, allowed IP `127.0.0.1`, public P2P listening on `0.0.0.0:8333`, Tor proxy enabled, and RPC credentials generated with Python `secrets`.
- `/srv/bitcoin/config/electrs.toml`: Authenticated against local Bitcoin Core RPC on `127.0.0.1:8332`, Electrum RPC bound to `127.0.0.1:50011`, and RocksDB index stored at `/srv/bitcoin/data/electrs_db`.

Verify permissions:
```bash
ls -la /srv/bitcoin/config
# Confirm permissions are -rw------- (0600) owned by bitcoin:bitcoin
```

## 4. Install Systemd Services

Service units are located in [`service/`](service/):
- `bitcoin-apps.target`: Coordinates starting and stopping the entire Bitcoin stack.
- `bitcoind.service`: Hardened unit running `bitcoind` under user `bitcoin` with `ProtectHome=true`, `ProtectSystem=strict`, and writable paths restricted to `/srv/bitcoin/data`.
- `electrs.service`: Hardened unit running `electrs`, ordered after `bitcoind.service`.

Install the units to `/etc/systemd/system/`:
```bash
sudo cp /srv/bitcoin/fullnode/service/bitcoin-apps.target /etc/systemd/system/
sudo cp /srv/bitcoin/fullnode/service/bitcoind.service /etc/systemd/system/
sudo cp /srv/bitcoin/fullnode/service/electrs.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable bitcoind.service electrs.service
```

## 5. Operations & Runbook

Because `/srv/bitcoin` is an encrypted volume configured with `noauto` in crypttab and fstab, services do not start automatically at boot.

### Post-Boot Startup
1. Unlock the LUKS volume:
   ```bash
   sudo systemctl start systemd-cryptsetup@bitcoin.service
   ```
2. Mount the filesystem:
   ```bash
   sudo mount /srv/bitcoin
   ```
3. Start the node stack:
   ```bash
   sudo systemctl start bitcoin-apps.target
   ```

### Check Status & Logs
```bash
systemctl status bitcoin-apps.target
journalctl -u bitcoind.service -f
journalctl -u electrs.service -f
```

### Restarting the Stack
Restarting the target restarts all member services:
```bash
sudo systemctl restart bitcoin-apps.target
```

### Stopping and Locking
```bash
sudo systemctl stop bitcoin-apps.target
sudo umount /srv/bitcoin
sudo systemctl stop systemd-cryptsetup@bitcoin.service
```

## 6. Wallet Connection

### Local / LAN via Electrum
- Raw TCP (loopback): `127.0.0.1:50011:t`
- SSL via Nginx reverse proxy: `electrs.eniemela.fi:50012:s`

Command-line test:
```bash
electrum --oneserver --server 127.0.0.1:50011:t
```

### Via Tor
Configure Electrum proxy to `127.0.0.1:9050` (SOCKS5) under Network settings.

## 7. Upgrades

### Upgrading Bitcoin Core
```bash
cd /srv/bitcoin/fullnode/bitcoin
git fetch origin --tags
git checkout <tag>
cmake --build build -j$(nproc)
sudo systemctl restart bitcoin-apps.target
```

### Upgrading Electrs
```bash
cd /srv/bitcoin/fullnode/electrs
git pull origin master
cargo build --release --locked
sudo systemctl restart electrs.service
```
