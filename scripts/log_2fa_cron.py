#!/usr/bin/env python3
# Cron script to log 2FA codes every minute
# Writes: "YYYY-MM-DD HH:MM:SS - 2FA Code: 123456"

import os
import sys
from datetime import datetime, timezone
import base64
import binascii

# Use the helper totp_generate function if you have one.
# Minimal inline TOTP implementation using pyotp if available.
try:
    import pyotp
except Exception:
    pyotp = None

SEED_PATH = '/data/seed.txt'

def read_hex_seed(path=SEED_PATH):
    try:
        with open(path, 'r') as f:
            s = f.read().strip()
            if len(s) != 64:
                return None
            # validate hex
            int(s, 16)
            return s.lower()
    except FileNotFoundError:
        return None
    except Exception:
        return None

def hex_to_base32(hex_seed):
    b = binascii.unhexlify(hex_seed)
    b32 = base64.b32encode(b).decode('utf-8')
    return b32

def generate_code_from_hex(hex_seed):
    # Prefer pyotp if installed
    b32 = hex_to_base32(hex_seed)
    if pyotp:
        totp = pyotp.TOTP(b32)
        return totp.now()
    # Fallback minimal implementation (requires hmac, hashlib)
    import hmac, hashlib, time, struct
    key = base64.b32decode(b32)
    interval = int(time.time()) // 30
    msg = struct.pack(">Q", interval)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 0x0f
    code = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return f"{code:06d}"

def main():
    hex_seed = read_hex_seed()
    if not hex_seed:
        print("Seed not found or invalid", flush=True)
        return 1
    code = generate_code_from_hex(hex_seed)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - 2FA Code: {code}", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
