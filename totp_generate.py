import base64, time, sys, os
import pyotp

SEED_FILE = "data/seed.txt"

if not os.path.isfile(SEED_FILE):
    print("ERROR: seed file missing:", SEED_FILE, file=sys.stderr); sys.exit(2)

hex_seed = open(SEED_FILE).read().strip()
if len(hex_seed)!=64:
    print("ERROR: seed file does not contain 64-char hex", file=sys.stderr); sys.exit(3)

seed_bytes = bytes.fromhex(hex_seed)
b32 = base64.b32encode(seed_bytes).decode('utf-8') 
totp = pyotp.TOTP(b32, digits=6, interval=30)  # SHA1 default
code = totp.now()
remaining = 30 - (int(time.time()) % 30)
print(code)
print("valid_for_seconds:", remaining)
