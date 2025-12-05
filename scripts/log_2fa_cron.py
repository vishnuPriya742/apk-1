import os, sys, time, binascii, base64
try:
    path = "/data/seed.txt"
    if not os.path.exists(path):
        print("Seed not available")
        sys.exit(0)
    seed = open(path).read().strip()
    b = binascii.unhexlify(seed)
    b32 = base64.b32encode(b).decode("utf-8")
    import pyotp
    totp = pyotp.TOTP(b32)
    code = totp.now()
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    print(f"{ts} - 2FA Code: {code}")
except Exception as e:
    print("error:",
import os, sys, time, binascii, base64
try:
    path = "/data/seed.txt"
    if not os.path.exists(path):
        print("Seed not available")
        sys.exit(0)
    seed = open(path).read().strip()
    b = binascii.unhexlify(seed)
    b32 = base64.b32encode(b).decode("utf-8")
    import pyotp
    totp = pyotp.TOTP(b32)
    code = totp.now()
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    print(f"{ts} - 2FA Code: {code}")
except Exception as e:
    print("error:", str(e))
