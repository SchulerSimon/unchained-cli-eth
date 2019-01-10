# This software is licensed under the GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
from .const import (
    sep1,
    sep2,
    sep3,
)
from .transaction import MyTransaction, make_transaction
from trie import (
    HexaryTrie,
)
from typing import (
    Tuple,
)

from web3 import Web3

import rlp

Transactions = Tuple[MyTransaction, ...]


class MyTrie():

    fields = [
        ('trie', HexaryTrie),
        ('data', dict)
    ]

    def __init__(self, trie, data):
        self.trie = trie
        self.data = data


def make_trie(transactions: Transactions) -> MyTrie:
    transactions = tuple(rlp.encode(item) for item in transactions)
    kv_store = {}
    trie = HexaryTrie(kv_store)
    with trie.squash_changes() as memory_trie:
        for index, item in enumerate(transactions):
            index_key = rlp.encode(index, sedes=rlp.sedes.big_endian_int)
            memory_trie[index_key] = item
    return MyTrie(
        trie=trie,
        data=kv_store
    )


def make_trie_from_hashes(web3: Web3, tx_hashes: list) -> MyTrie:
    transactions = tuple()
    for tx_hash in tx_hashes:
        raw_tx = web3.eth.getTransaction(tx_hash)
        transactions += (make_transaction(raw_tx), )
    return make_trie(transactions)


def serialize_trie(trie: MyTrie) -> (str, str):
    trie_string = serialize_trie_data(trie.data)
    return trie_string, trie.trie.root_hash.hex()


def deserialize_trie(trie_string: str, root_hash_string: str) -> MyTrie:
    data = deserialize_trie_data(trie_string)
    trie = HexaryTrie(data, root_hash=root_hash_string)
    return MyTrie(
        data=data,
        trie=trie
    )


def serialize_trie_data(db: dict) -> str:
    db_str = ''
    for path, data in db.items():
        db_str += path.hex() + sep2 + data.hex() + sep1
    db_str = db_str[:-1]
    return db_str


def deserialize_trie_data(db_str: str) -> dict:
    db = {}
    for item in db_str.split(sep1):
        item = item.split(sep2)
        db[bytes.fromhex(item[0])] = bytes.fromhex(item[1])
    return db
