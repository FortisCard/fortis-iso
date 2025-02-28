from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib
import subprocess

PACKAGE_AID = [0xA0, 0x01, 0x02, 0x03, 0x04, 0x05, 0x01]
APPLET_AID = PACKAGE_AID + [0x01]
INS_STORE_SEED = 0x10


def store_encrypted_seed(connection, seed, pin):
    _reset_fortis_card(connection)
    encrypted_data = _encrypt_seed(seed, pin)
    fingerprint = hashlib.sha256(seed).digest()[:4]
    data = encrypted_data + fingerprint

    select_applet_apdu = [0x00, 0xA4, 0x04, 0x00] + [len(APPLET_AID)] + APPLET_AID
    apdu = [0x00, INS_STORE_SEED, 0x00, 0x00, len(data)] + list(data)
    _send_apdu(connection, select_applet_apdu)
    _send_apdu(connection, apdu)

def _encrypt_seed(seed, pin):
    key = hashlib.sha256(pin).digest()
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_seed = encryptor.update(seed) + encryptor.finalize()
    return encrypted_seed


def _reset_fortis_card(connection):
    command = 'gpp -delete A0010203040501 -f && gpp -install fortis-*.cap'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f'Error: {result.stderr}')

    connection.reconnect()

def _send_apdu(connection, apdu):
    _, sw1, sw2 = connection.transmit(apdu)

    if sw1 != 0x90 or sw2 != 0x00:
        raise Exception(f'FortisCard Error: {sw1:02X}{sw2:02X}')

