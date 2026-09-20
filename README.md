# Bitcoin Full Node Stack

Deployment runbook for Bitcoin Core (`bitcoind`) and Electrs on Arch Linux, running on a dedicated encrypted volume mounted at `/srv/bitcoin`. The `bitcoin` system user runs services; `elmeri` maintains the configuration and checkout.

## Directory Layout

All node components run inside the `/srv/bitcoin` mountpoint:
```text
/srv/bitcoin/
├── config/             # Configuration files (mode 0755, files 0644; elmeri-owned)
│   ├── bitcoin.conf
│   └── electrs.toml
├── data/               # Persistent data and indices (directories 0755, files 0644)
│   ├── blocks/         # Bitcoin block storage
│   ├── chainstate/     # Bitcoin UTXO set
│   └── electrs_db_bindex/     # RocksDB Electrs index
└── fullnode/           # Repository checkout (mode 0755; elmeri-owned)
    ├── bin/            # Helper scripts and config generator
    ├── bitcoin/        # Bitcoin Core source and build
    ├── electrs/        # Electrs source and build
    └── systemd/        # Systemd service and target units
```

## Build Instructions

#### Setup /srv/bitcoin (Encrypted Bitcoin Storage)

The Bitcoin storage is a dedicated LUKS2 + ext4 drive mounted at `/srv/bitcoin`. Its three layers are: LUKS label `luks-bitcoin`, mapper name `bitcoin`, and filesystem label `ext4-bitcoin`.

Partition and format the verified disk:
```bash
DEV=/dev/disk/by-id/ata-REPLACE_WITH_VERIFIED_DISK_ID
PART=/dev/disk/by-id/ata-REPLACE_WITH_VERIFIED_DISK_ID-part1
sudo parted --script "$DEV" mklabel gpt mkpart primary 1MiB 100%
sudo partprobe "$DEV"
sudo cryptsetup luksFormat --label luks-bitcoin "$PART"
sudo cryptsetup open "$PART" bitcoin
sudo mkfs.ext4 -L ext4-bitcoin /dev/mapper/bitcoin
```

Configure `/etc/crypttab` for manual unlock:
```text
bitcoin LABEL=luks-bitcoin none noauto,luks
```

Configure `/etc/fstab` for manual mount:
```text
/dev/mapper/bitcoin /srv/bitcoin ext4 noauto,relatime 0 2
```

Create the dedicated `bitcoin` system user (non-login shell, home `/srv/bitcoin`):
```bash
sudo useradd --system \
  --user-group \
  --no-create-home \
  --home-dir /srv/bitcoin \
  --shell /usr/bin/nologin \
  bitcoin
```

Unlock, mount, and establish the directory hierarchy and permissions:
```bash
sudo systemctl daemon-reload
sudo systemctl start systemd-cryptsetup@bitcoin.service
sudo mkdir -p /srv/bitcoin
sudo mount /srv/bitcoin

# Layout: config and checkout are maintained by elmeri; services own their data.
sudo install -d -m 0755 /srv/bitcoin
sudo install -d -o elmeri -g elmeri -m 0755 /srv/bitcoin/config /srv/bitcoin/fullnode
sudo install -d -o bitcoin -g bitcoin -m 0755 /srv/bitcoin/data
```

Data and runtime permissions overview:
- `/srv/bitcoin`: mode `0755`, owned by `root:root`.
- `/srv/bitcoin/config`: mode `0755`, owned by `elmeri:elmeri`. Configuration files are mode `0644`, so the `bitcoin` service user can read them.
- `/srv/bitcoin/data`: owned by `bitcoin:bitcoin`; directories are mode `0755` and files mode `0644`, making the blockchain and index data readable to all local users.
- `/srv/bitcoin/fullnode`: mode `0755`, owned by `elmeri:elmeri`. It contains the source code, compiled binaries, and helper scripts.

### Dependencies
Install build tools and libraries:
```bash
sudo pacman -S --needed base-devel cmake boost libevent sqlite python capnproto rust clang tor zeromq jq
```

### Build Bitcoin Core
Build all node components, utilities, wallet, and libraries using CMake:
```bash
cd /srv/bitcoin/fullnode/bitcoin

cmake_flags=(
  -DCMAKE_BUILD_TYPE=Release          # Build optimized release binaries
  -DENABLE_WALLET=ON                  # Enable SQLite descriptor wallet support
  -DBUILD_WALLET_TOOL=ON              # Build offline wallet tool (bitcoin-wallet) for descriptor inspection
  -DWITH_ZMQ=ON                       # Enable ZeroMQ notifications (for LND, BTCPay, and external services)
  -DENABLE_IPC=ON                     # Enable Cap'n Proto multiprocess IPC (builds bitcoin-node)
  -DENABLE_EXTERNAL_SIGNER=ON         # Enable hardware wallet support (HWI for Ledger, Trezor, Coldcard)
  -DBUILD_BITCOIN_BIN=ON              # Build unified bitcoin binary runner
  -DBUILD_DAEMON=ON                   # Build bitcoind server daemon
  -DBUILD_CLI=ON                      # Build bitcoin-cli RPC client
  -DBUILD_TX=ON                       # Build bitcoin-tx tool for creating and manipulating raw transactions
  -DBUILD_UTIL=ON                     # Build bitcoin-util tool
  -DBUILD_UTIL_CHAINSTATE=ON          # Build experimental bitcoin-chainstate standalone binary
  -DBUILD_KERNEL_LIB=ON               # Build experimental libbitcoinkernel library
  -DWITH_EMBEDDED_ASMAP=ON            # Embed standard ASMap data for peer bucketing
  -DWITH_USDT=ON                      # Enable USDT (User-Space, Statically Defined Tracing) tracepoints
  -DBUILD_TESTS=OFF                   # Skip unit tests to reduce compile time
  -DBUILD_BENCH=OFF                   # Skip microbenchmarks
  -DBUILD_FUZZ_BINARY=OFF             # Skip fuzzing harnesses
  -DBUILD_GUI=OFF                     # Skip Qt GUI (headless server setup)
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON  # Generate compile_commands.json for LSP/tooling
  -DINSTALL_MAN=OFF                   # Skip installing manual pages
)

cmake -S . -B build "${cmake_flags[@]}"
cmake --build build -j$(nproc)
```

### Build Electrs
Build the release binary with Cargo (`CXXFLAGS` ensures RocksDB C++ headers compile on modern GCC):
```bash
cd /srv/bitcoin/fullnode/electrs
CXXFLAGS="-include cstdint" cargo build --release --locked
```

## Tor Setup (Optional)

If routing node traffic through Tor is desired, enable and start the Tor daemon:
```bash
sudo systemctl enable tor --now
```
By default, Bitcoin Core runs on low-latency clearnet (IPv4 / IPv6) for optimal transaction and RBF propagation speed. Tor can be enabled in `bin/config.py` via `ENABLE_TOR`.

## Configuration Generation

Generate configuration files with normal (`0644`) permissions:
```bash
python3 /srv/bitcoin/fullnode/bin/config.py
```
This generates:
- `/srv/bitcoin/config/bitcoin.conf`: Clearnet P2P listening on `0.0.0.0:8333` and `[::]:8333`, 256 connections, 1000 MB mempool, ASMap bucketing, wallet enabled (`disablewallet=0`), 16 RPC threads, 64 workqueue, RPC bound to `127.0.0.1:8332` with allowed IP `127.0.0.1`, and RPC credentials.
- `/srv/bitcoin/config/electrs.toml`: Authenticated against local Bitcoin Core RPC on `127.0.0.1:8332`, Electrum RPC on `127.0.0.1:50011`, RocksDB parallelism (`db_parallelism=4`), extended JSON-RPC timeouts (`jsonrpc_timeout_secs=60`), index lookup limits (`index_lookup_limit=1000`), auto-reindex enabled, Prometheus monitoring on `127.0.0.1:4224`, and index stored at `/srv/bitcoin/data/electrs_db_bindex`.

Verify permissions:
```bash
ls -la /srv/bitcoin/config
# Confirm permissions are -rw-r--r-- (0644) owned by elmeri:elmeri
```

## Install Systemd Services

Service units are located in [`systemd/`](systemd/):
- `bitcoin-apps.target`: Coordinates starting and stopping the entire Bitcoin stack.
- `bitcoind.service`: Hardened unit running `bitcoind` under user `bitcoin` with `ProtectHome=true`, `ProtectSystem=strict`, and writable paths restricted to `/srv/bitcoin/data`.
- `electrs.service`: Hardened unit running `electrs`, ordered after `bitcoind.service`.

Install the units to `/etc/systemd/system/`:
```bash
sudo cp /srv/bitcoin/fullnode/systemd/bitcoin-apps.target /etc/systemd/system/
sudo cp /srv/bitcoin/fullnode/systemd/bitcoind.service /etc/systemd/system/
sudo cp /srv/bitcoin/fullnode/systemd/electrs.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable bitcoind.service electrs.service
```

## Operations & Runbook

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

## Upgrades

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
