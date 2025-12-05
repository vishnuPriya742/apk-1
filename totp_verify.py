#!/usr/bin/env python3
import base64, sys, os
import pyotp

import base64, sys, os
import pyotp

if len(sys.argv) < 2:
    print("Usage: python3 totp_verify.py <6-digit-code>", file=sys.stderr)
    sys.exit(2)

code = sys.argv[1].strip()
SEED_FILE = "data/seed.txt"
if not os.path.isfile(SEED_FILE):
    print("ERROR: seed file missing:", SEED_FILE, file=sys.stderr); sys.exit(3)
hex_seed = open(SEED_FILE).read().strip()
seed_bytes = bytes.fromhex(hex_seed)
b32 = base64.b32encode(seed_bytes).decode('utf-8')
totp = pyotp.TOTP(b32, digits=6, interval=30)
valid = totp.verify(code, valid_window=1)  # ±1 period
print("valid:", bool(valid))
