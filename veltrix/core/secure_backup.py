import shutil
from pathlib import Path

def encrypted_backup(source, target, key):
    data = Path(source).read_bytes(); encoded = bytes(b ^ key[i % len(key)] for i, b in enumerate(data)); Path(target).write_bytes(encoded)

def decrypt_backup(source, target, key): encrypted_backup(source, target, key)
