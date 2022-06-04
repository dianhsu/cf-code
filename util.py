from Crypto.Cipher import AES

BLOCK_SIZE = 16


def init_cipher(secret_key, iv_key):
    secret_bytes = bytes.fromhex(secret_key)
    key_bytes = []
    if len(secret_bytes) >= BLOCK_SIZE:
        key_bytes = secret_bytes[:BLOCK_SIZE]
    else:
        key_bytes.extend(secret_bytes)
        key_bytes.extend([0 for x in range(0, BLOCK_SIZE - len(secret_bytes))])

    if iv_key is None or len(iv_key) == 0:
        cipher = AES.new(bytes(key_bytes), AES.MODE_ECB)
        return cipher
    else:
        iv_bytes = bytes.fromhex(iv_key)
        iv_key_bytes = []
        if len(iv_bytes) >= BLOCK_SIZE:
            iv_key_bytes = iv_bytes[:BLOCK_SIZE]
        else:
            iv_key_bytes.extend(iv_bytes)
            iv_key_bytes.extend([0 for x in range(0, BLOCK_SIZE - len(iv_bytes))])
        cipher = AES.new(bytes(key_bytes), AES.MODE_CBC, bytes(iv_key_bytes))
        return cipher


def aes_decrypt(value, secret_key, iv_key):
    cipher = init_cipher(secret_key, iv_key)
    buffer = bytes.fromhex(value)
    buffer = cipher.decrypt(buffer)
    result = bytes.hex(buffer)
    return result
