# This software is licensed under the GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
from .block import *

from pyethash import (
    EPOCH_LENGTH,
    hashimoto_light,
    mkcache_bytes,
)

from binascii import unhexlify
from collections import OrderedDict
from typing import (
    List,
    Tuple
)

from eth_hash.auto import keccak

from eth_utils import (
    big_endian_to_int,
)

from eth_typing import (
    Hash32
)

# Type annotation here is to ensure we don't accidentally use strings
# instead of bytes.
cache_seeds = [b'\x00' * 32]  # type: List[bytes]
cache_by_seed = OrderedDict()  # type: OrderedDict[bytes, bytearray]
CACHE_MAX_ITEMS = 10


class ValidationError(Exception):

    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)


def validate_length(value, length, title="Value"):
    if not len(value) == length:
        raise ValidationError(
            "{title} must be of length {0}.  Got {1} of length {2}".format(
                length,
                value,
                len(value),
                title=title,
            )
        )


def validate_is_integer(value, title="Value"):
    if not isinstance(value, int):
        raise ValidationError(
            "{title} must be a an integer.  Got: {0}".format(
                type(value), title=title)
        )


def validate_lte(value, maximum, title="Value"):
    if value > maximum:
        raise ValidationError(
            "{title} {0} is not less than or equal to {1}".format(
                value,
                maximum,
                title=title,
            )
        )
    validate_is_integer(value, title=title)


def get_cache(block_number: int) -> bytes:
    while len(cache_seeds) <= block_number // EPOCH_LENGTH:
        cache_seeds.append(keccak(cache_seeds[-1]))
    seed = cache_seeds[block_number // EPOCH_LENGTH]
    if seed in cache_by_seed:
        c = cache_by_seed.pop(seed)  # pop and append at end
        cache_by_seed[seed] = c
        return c
    c = mkcache_bytes(block_number)
    cache_by_seed[seed] = c
    if len(cache_by_seed) > CACHE_MAX_ITEMS:
        cache_by_seed.popitem(last=False)  # remove last recently accessed
    return c


def _check_pow(block_number: int,
               mining_hash: Hash32,
               mix_hash: Hash32,
               nonce: bytes,
               difficulty: int) -> None:
    validate_length(mix_hash, 32, title="Mix Hash")
    validate_length(mining_hash, 32, title="Mining Hash")
    validate_length(nonce, 8, title="POW Nonce")

    cache = get_cache(block_number)

    mining_output = hashimoto_light(
        block_number, cache, mining_hash, big_endian_to_int(nonce))
    print(mining_output[b'mix digest'].hex())
    print(mining_output[b'result'].hex())

    if mining_output[b'mix digest'] != mix_hash:
        raise ValidationError("mix hash mismatch; {0} != {1}".format(
            mining_output[b'mix digest'].hex(), mix_hash.hex()))
    result = big_endian_to_int(mining_output[b'result'])
    validate_lte(result, 2**256 // difficulty, title="POW Difficulty")


def check_pow(block: MyBlockHeader) -> bool:
    try:
        _check_pow(block['number'],
                   block.mining_hash(),
                   block['mixHash'],
                   block['nonce'],
                   block['difficulty'])
    except Exception as e:
        return False
    return True
