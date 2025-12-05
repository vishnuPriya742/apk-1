import time
import base64
import pyotp
from datetime import datetime, timezone

def load_seed():
    try:
        with open("/data/seed.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

while True:
    hex_seed = load_seed()
    if not hex_seed:
        print("Seed not found")
        break

    try:
        seed_bytes = bytes.fromhex(hex_seed)
        seed_base32 = base64.b32encode(seed_bytes).decode()
        totp = pyotp.TOTP(seed_base32)
        code = totp.now()

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - 2FA Code: {code}")
    except Exception as e:
        print("Error:", str(e))
    break
