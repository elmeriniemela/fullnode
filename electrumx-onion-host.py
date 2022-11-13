#!/usr/bin/env python3
import subprocess
onion_host = subprocess.run("sudo cat /var/lib/tor/electrumX_service/hostname", shell=True, check=True, capture_output=True, encoding='utf-8')
print(onion_host.stdout.strip())
