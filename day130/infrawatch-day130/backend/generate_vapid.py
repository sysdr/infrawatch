#!/usr/bin/env python3
"""Generate VAPID EC P-256 keys and write them to .env"""
import base64, os, re
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key  = private_key.public_key()

private_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
private_b64   = base64.urlsafe_b64encode(private_bytes).rstrip(b'=').decode()

pub_nums     = public_key.public_numbers()
public_bytes = b'\x04' + pub_nums.x.to_bytes(32,'big') + pub_nums.y.to_bytes(32,'big')
public_b64   = base64.urlsafe_b64encode(public_bytes).rstrip(b'=').decode()

env_path = os.path.join(os.path.dirname(__file__), '.env')
with open(env_path, 'r') as f:
    content = f.read()
content = re.sub(r'^VAPID_PRIVATE_KEY=.*$', f'VAPID_PRIVATE_KEY={private_b64}', content, flags=re.MULTILINE)
content = re.sub(r'^VAPID_PUBLIC_KEY=.*$',  f'VAPID_PUBLIC_KEY={public_b64}',   content, flags=re.MULTILINE)
with open(env_path, 'w') as f:
    f.write(content)
print(f"VAPID_PUBLIC_KEY={public_b64}")
print(f"VAPID_PRIVATE_KEY={private_b64[:12]}...")
print("Keys written to .env")
