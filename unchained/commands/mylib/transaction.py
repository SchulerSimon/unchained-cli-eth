# This software is licensed under the GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
from .const import (
    sep1,
    sep2,
    sep3,
)
from .const import const_chain_id

from rlp.sedes import (
    BigEndianInt,
    big_endian_int,
    Binary,
    binary,
)
import rlp
from eth_utils import (
    keccak,
    to_bytes,
    to_hex,
)
from ethereum import utils
from ethereum.utils import normalize_address, ecrecover_to_pub
from binascii import unhexlify

secpk1n = 115792089237316195423570985008687907852837564279074904382605163141518161494337

# ehtereum specific types
address = Binary.fixed_length(20, allow_empty=True)


class MyTransaction(rlp.Serializable):
    fields = [
        ('nonce', big_endian_int),
        ('gasprice', big_endian_int),
        ('startgas', big_endian_int),
        ('to', address),
        ('value', big_endian_int),
        ('data', binary),
        ('v', big_endian_int),
        ('r', big_endian_int),
        ('s', big_endian_int)
    ]

    def hash(self) -> bytes:
        '''use the rlp and hash to recalculate the blockhash'''
        return keccak(rlp.encode(self))

    def sender(self):
        '''use signature to get sender'''
        pub = self.get_public_key()
        if pub == b'\x00' * 64:
            raise InvalidTransaction(
                'Invalid signature (zero privkey cannot sign)')
        return utils.sha3(pub)[-20:]

    def get_public_key(self):
        '''return the public key used to sign this tx'''
        if self.r == 0 and self.s == 0:
            raise InvalidTransaction('Invalid transaction signature')
        else:
            signhash, vee = self.get_sign_hash()
            return ecrecover_to_pub(signhash, vee, self.r, self.s)

    def get_sign_hash(self):
        if self.v in (27, 28):
            vee = self.v
            return utils.sha3(rlp.encode(
                unsigned_tx_from_tx(self), UnsignedTransaction)), vee
        elif self.v >= 37:
            vee = self.v - const_chain_id * 2 - 8
            assert vee in (27, 28)
            rlpdata = rlp.encode(rlp.infer_sedes(self).serialize(self)[
                                 :-3] + [const_chain_id, '', ''])
            return utils.sha3(rlpdata), vee
        else:
            raise InvalidTransaction('Invalid V value')
        if self.r >= secpk1n or self.s >= secpk1n or self.r == 0 or self.s == 0:
            raise InvalidTransaction('Invalid signature values')


def make_transaction(tx: dict) -> MyTransaction:
    if tx['to']:
        to = normalize_address(tx['to'], allow_blank=True)
    else:
        to = b''

    return MyTransaction(
        nonce=tx['nonce'],
        gasprice=tx['gasPrice'],
        startgas=tx['gas'],
        to=to,
        value=tx['value'],
        data=unhexlify(tx['input'][2:]),  # data = data_decoder(data)
        v=tx['v'],
        r=int.from_bytes(tx['r'], byteorder='big'),
        s=int.from_bytes(tx['s'], byteorder='big')
    )


def serialize_transaction(tx: MyTransaction) -> str:
    tx_string = ''
    for k, v in tx.__dict__.items():
        if isinstance(v, bytes):
            v = v.hex()
        tx_string += k[1:] + sep2 + str(v) + sep1
    return tx_string[:-1]


def deserialize_transaction(tx_string: str)->MyTransaction:
    tx = {}
    for item in strip_string(tx_string).split(sep1):
        item = item.split(sep2)
        tx[item[0]] = item[1]

    return MyTransaction(
        nonce=int(tx['nonce']),
        gasprice=int(tx['gasprice']),
        startgas=int(tx['startgas']),
        to=unhexlify(tx['to']),
        value=int(tx['value']),
        data=unhexlify(tx['data']),  # data = data_decoder(data)
        v=int(tx['v']),
        r=int(tx['r']),
        s=int(tx['s'])
    )


class UnsignedTransaction(rlp.Serializable):
    fields = [
        (field, sedes) for field, sedes in MyTransaction._meta.fields
        if field not in "vrs"
    ]


def unsigned_tx_from_tx(tx):
    return UnsignedTransaction(
        nonce=tx.nonce,
        gasprice=tx.gasprice,
        startgas=tx.startgas,
        to=tx.to,
        value=tx.value,
        data=tx.data,
    )


def strip_string(string: str) -> str:
    return string.replace('\'', '').replace('[', '').replace(']', '').replace('\"', '')
