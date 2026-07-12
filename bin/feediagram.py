#!/usr/bin/env python3
"""Serve a live plot of `bitcoin-cli getmempoolfeeratediagram` on http://0.0.0.0:8350"""
import os
import shlex
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BITCOIN_CLI = shlex.split(os.environ.get("BITCOIN_CLI", "bitcoin-cli"))
PORT = int(os.environ.get("PORT", 8350))

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Mempool feerate diagram</title>
<style>
  body { font: 14px sans-serif; margin: 2em; background: #111; color: #ddd; }
  svg { width: 100%; height: 80vh; background: #181818; }
  path { fill: none; stroke: #f7931a; stroke-width: 2; }
  line { stroke: #333; } text { fill: #888; font-size: 12px; }
</style></head><body>
<h2>Mempool feerate diagram <small id="info"></small></h2>
<svg id="svg" viewBox="0 0 1000 500" preserveAspectRatio="none"></svg>
<script>
async function draw() {
  const d = await (await fetch('data.json')).json();
  if (!d.length) { info.textContent = '(mempool empty)'; return; }
  const W = 1000, H = 500, maxW = d[d.length-1].weight, maxF = d[d.length-1].fee;
  const x = v => v / maxW * W, y = v => H - v / maxF * H;
  let s = '';
  // block boundary gridlines every 4M weight units
  for (let b = 4e6; b < maxW; b += 4e6)
    s += `<line x1="${x(b)}" y1="0" x2="${x(b)}" y2="${H}"/>` +
         `<text x="${x(b)+4}" y="14">${b/4e6}</text>`;
  s += '<path d="M' + d.map(p => `${x(p.weight)},${y(p.fee)}`).join(' L') + '"/>';
  svg.innerHTML = s;
  info.textContent = `${(maxW/4e6).toFixed(1)} blocks of weight, ` +
                     `${maxF} BTC total fees — ${new Date().toLocaleTimeString()}`;
}
draw(); setInterval(draw, 30000);
</script></body></html>""".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data.json":
            try:
                body = subprocess.run(BITCOIN_CLI + ["getmempoolfeeratediagram"],
                                      capture_output=True, check=True, timeout=30).stdout
                self.reply(200, "application/json", body)
            except subprocess.CalledProcessError as e:
                self.reply(500, "text/plain", e.stderr)
        elif self.path == "/":
            self.reply(200, "text/html", HTML)
        else:
            self.reply(404, "text/plain", b"not found")

    def reply(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"serving on http://0.0.0.0:{PORT} using: {' '.join(BITCOIN_CLI)}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
