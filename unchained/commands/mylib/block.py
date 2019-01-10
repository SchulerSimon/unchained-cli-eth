# This software is licensed under the GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007

from .const import (
    sep1,
    sep2,
    sep3,
)
from ethereum import utils

import rlp
from eth_utils import (
    keccak,
    to_bytes,
    to_hex,
)
from rlp.sedes import (
    BigEndianInt,
    big_endian_int,
    Binary,
    binary,
)
from binascii import unhexlify

# ehtereum specific types
address = Binary.fixed_length(20, allow_empty=True)
hash32 = Binary.fixed_length(32)
int256 = BigEndianInt(256)
trie_root = Binary.fixed_length(32, allow_empty=True)


class MyBlockHeader(rlp.Serializable):
    fields = [
        ('parentHash', hash32),
        ('sha3Uncles', hash32),
        ('miner', address),
        ('stateRoot', trie_root),
        ('transactionsRoot', trie_root),
        ('receiptsRoot', trie_root),
        ('logsBloom', int256),
        ('difficulty', big_endian_int),
        ('number', big_endian_int),
        ('gasLimit', big_endian_int),
        ('gasUsed', big_endian_int),
        ('timestamp', big_endian_int),
        ('extraData', binary),
        ('mixHash', binary),
        ('nonce', Binary(8, allow_empty=True))
    ]

    def hash(self) -> bytes:
        '''use the rlp and hash to recalculate the blockhash'''
        return keccak(rlp.encode(self))

    def mining_hash(self):
        '''mining_hash excludes mixhash and nonce'''
        fields2 = [
            (field, sedes) for field, sedes in MyBlockHeader._meta.fields
            if field not in ["mixHash", "nonce"]
        ]

        class BlockHeader2(rlp.Serializable):
            fields = fields2

        _self = BlockHeader2(**{f: getattr(self, f) for (f, sedes) in fields2})

        return utils.sha3(rlp.encode(
            _self, BlockHeader2))


def make_block_header(block: dict) -> MyBlockHeader:
    '''create MyBlockHeader object from dict'''
    return MyBlockHeader(
        parentHash=to_bytes(block['parentHash']),
        sha3Uncles=to_bytes(block['sha3Uncles']),
        miner=to_bytes(bytes.fromhex(block['miner'][2:])),
        stateRoot=to_bytes(block['stateRoot']),
        transactionsRoot=to_bytes(block['transactionsRoot']),
        receiptsRoot=to_bytes(block['receiptsRoot']),
        logsBloom=int(block['logsBloom'].hex(), 16),
        difficulty=block['difficulty'],
        number=block['number'],
        gasLimit=block['gasLimit'],
        gasUsed=block['gasUsed'],
        timestamp=block['timestamp'],
        extraData=to_bytes(block['extraData']),
        mixHash=to_bytes(block['mixHash']),
        nonce=to_bytes(block['nonce'])
    )


def serialize_block_header(head: MyBlockHeader) -> str:
    block_str = ''
    for k, v in head.__dict__.items():
        if k == '_cached_rlp':
            continue
        if isinstance(v, bytes):
            v = v.hex()
        block_str += k[1:] + sep2 + str(v) + sep1
    return block_str[:-1]


def deserialize_block_header(block_str: str) -> MyBlockHeader:
    block = {}
    for item in strip_string(block_str).split(sep1):
        item = item.split(sep2)
        block[item[0]] = item[1]
    return MyBlockHeader(
        parentHash=unhexlify(block['parentHash'][2:]),
        sha3Uncles=unhexlify(block['sha3Uncles'][2:]),
        miner=unhexlify(block['miner']),
        stateRoot=unhexlify(block['stateRoot'][2:]),
        receiptsRoot=unhexlify(block['receiptsRoot'][2:]),
        transactionsRoot=unhexlify(block['transactionsRoot'][2:]),
        logsBloom=int(block['logsBloom']),
        difficulty=int(block['difficulty']),
        number=int(block['number']),
        gasLimit=int(block['gasLimit']),
        gasUsed=int(block['gasUsed']),
        timestamp=int(block['timestamp']),
        extraData=unhexlify(block['extraData'][2:]),
        mixHash=unhexlify(block['mixHash'][2:]),
        nonce=unhexlify(block['nonce'][2:])
    )


def strip_string(string: str) -> str:
    return string.replace('\'', '').replace('[', '').replace(']', '').replace('\"', '')
