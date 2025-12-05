"""
decrypt_seed.py
Reads encrypted_seed.txt (base64), decrypts it with student_private.pem using RSA-OAEP (SHA-256),
validates the result is a 64-char hex string, and writes it to data/seed.txt.
"""
import base64,sys,os
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

PRIVATE_KEY_FILE = "student_private.pem"
ENC_FILE = "encrypted_seed.txt"
OUT_FILE = "data/seed.txt"

def die(msg):
    print("ERROR:", msg, file=sys.stderr)
    sys.exit(1)
if not os.path.isfile(PRIVATE_KEY_FILE):
    die(f"private key not found: {PRIVATE_KEY_FILE}")
with open(PRIVATE_KEY_FILE, "rb") as f:
    key_data = f.read()
try:
    private_key = load_pem_private_key(key_data, password=None)
except Exception as e:
    die(f"failed to load private key: {e}")

if not os.path.isfile(ENC_FILE):
    die(f"encrypted file not found: {ENC_FILE}")
enc_b64 = open(ENC_FILE,"r").read().strip()
if not enc_b64:
    die("encrypted_seed.txt is empty")

# 3) base64 decode
try:
    ciphertext = base64.b64decode(enc_b64)
except Exception as e:
    die(f"base64 decode failed: {e}")
try:
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
except Exception as e:
    die(f"decryption failed: {e}")
try:
    seed = plaintext.decode("utf-8").strip()
except Exception as e:
    die(f"utf-8 decode failed: {e}")

if len(seed) != 64:
    die(f"decrypted seed length is {len(seed)} (expected 64). Value: {seed!r}")

import re
if not re.fullmatch(r"[0-9a-f]{64}", seed):
    die("decrypted seed is not a 64-character lowercase-hex string")

# 6) write to data/seed.txt
with open(OUT_FILE,"w") as f:
    f.write(seed+"\n")
print("Decryption OK — wrote", OUT_FILE)
