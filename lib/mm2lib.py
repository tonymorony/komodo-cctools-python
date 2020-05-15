from bitcoin.core.script import *
from bitcoin.core import Hash160
import bitcoin.base58
import struct
import unittest
from hashlib import sha256


def payment_script(time_lock, secret_hash, pub_0, pub_1):
    """
    this function making payment script for mm2 atomic swap
    ported from mm2 rust code
    """
    return CScript([OP_IF, struct.pack('<I', time_lock), OP_NOP2 , OP_DROP, pub_0, OP_CHECKSIG,
             OP_ELSE, OP_SIZE,  b'\x20', OP_EQUALVERIFY, OP_HASH160, secret_hash, OP_EQUALVERIFY, pub_1, OP_CHECKSIG, OP_ENDIF])


def get_payment_address(time_lock, secret_hash, pub_0, pub_1):
    pubkey_script = payment_script(time_lock, secret_hash, pub_0, pub_1)
    print(pubkey_script.hex())
    pubkey_hash = Hash160(pubkey_script)
    data = b'\x55' + pubkey_hash
    checksum = sha256(sha256(data).digest()).digest()[:4]
    byte_address = data + checksum
    address = bitcoin.base58.encode(byte_address)
    return address


class AddressConvertTest(unittest.TestCase):

    def test(self):

        address = get_payment_address(1588875030,
                                       bytes.fromhex("bc88c6534d5b82866807cde2da0ce5735c335a2a"),
                                       bytes.fromhex("03683c77e807a47dcd559fa60a6510087e5c5aa0016c094cf5eb4d7e002db18e9f"),
                                       bytes.fromhex("032eadab416e372d21d8cbf798019325088dc796fd6762b6304c0298f279d58038"))
        self.assertEqual(address, "bKYeacaKzVzGEDmrEX6zB5vr2ZoRNh7A3p")


if __name__ == '__main__':
    unittest.main()
    
